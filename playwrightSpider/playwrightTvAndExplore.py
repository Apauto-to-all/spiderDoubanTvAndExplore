import asyncio  # 异步io
import sys
from playwright.async_api import async_playwright  # 异步Playwright
import logging  # 日志模块
from FunctionTvAndExplore import FunctionTvAndExplore  # 一些功能的实现，父类
import traceback  # 异常处理更多信息


class PlaywrightTvAndExplore(FunctionTvAndExplore):
    """
    爬取豆瓣电视剧和电影探索页面\n
    输入：dict={"url": "爬取的url", "type": "类型"}
    """

    def __init__(self, dict):
        super().__init__()  # 调用父类的 __init__ 方法
        self.dict = dict  # 传入的字典
        self.url = dict["url"]  # url
        self.type = dict["type"]  # 类型
        asyncio.run(self.open_browser())

    # 打开浏览器
    async def open_browser(self):  # 打开浏览器
        """
        打开浏览器
        """
        if await self.isSaveType():  # 如果已经爬取过目标类型
            all_save = await self.getSavaJson()
            if (
                not all_save
            ):  # 如果保存的分组数据已经爬取完成，列表为空，那么无需再次爬取
                logging.info(f"{self.dict}已经爬取完成，无需再次爬取")
                return
        logging.info("打开浏览器中……")
        async with async_playwright() as p:
            if self.isLogin:  # 如果选择登录，设置用户数据目录
                self.browser = await p.chromium.launch_persistent_context(
                    user_data_dir=self.isLogin_user_data_path,
                    headless=self.isHeadless,
                    ignore_default_args=[
                        "--enable-automation"
                    ],  # 禁止弹出Chrome正在受到自动软件的控制的通知
                )
            else:
                self.browser = await p.chromium.launch(
                    headless=self.isHeadless,
                    ignore_default_args=[
                        "--enable-automation"
                    ],  # 禁止弹出Chrome正在受到自动软件的控制的通知
                )
            logging.info(f"浏览器已经打开，即将打开页面")
            await self.open_page()  # 打开页面

    # 获取一个新的页面
    async def get_page(self):
        """
        获取打开目标url的页面
        """
        page = await self.browser.new_page()
        if self.isLogin and self.isLogin_isWait:
            if self.isLogin_wait_url:
                await page.goto(self.isLogin_wait_url)
            await asyncio.sleep(self.isLogin_wait_time)
            await self.close_browser()
            sys.exit()

        await page.route(
            "**/*.{png,jpg,jpeg,gif,svg,ico}", lambda route, request: route.abort()
        )  # 禁止加载图片
        await page.route(
            "**/*.woff2", lambda route, request: route.abort()
        )  # 禁止加载字体
        # await page.route(
        #     "**/*.css", lambda route, request: route.abort()
        # )  # 禁止加载CSS
        # await page.route(
        #     "**/*.js", lambda route, request: route.abort()
        # )  # 禁止加载JavaScript
        await page.add_init_script(  # 添加初始化脚本
            'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        )
        await page.goto(self.url)
        await page.wait_for_load_state("load")  # 等待页面加载完成
        # await page.wait_for_load_state("networkidle")  # 等待网络空闲
        await self.random_sleep()
        return page

    # 打开页面
    async def open_page(self):  # 打开页面
        """
        打开页面
        """
        logging.info(f"打开页面：{self.url} 中……")

        async def on_request(response):
            if "/recommend/filter_tags" in response.url and response.status == 200:
                data = await response.json()
                await self.handle_tags_data(data)  # 处理tags数据

            if "/recommend?refresh=0&start=" in response.url and response.status == 200:
                data = await response.json()
                if not self.region_list:
                    for category in data["recommend_categories"]:
                        # 如果type是"地区"，那么提取data中的text
                        if category["type"] == "地区":
                            for item in category["data"]:
                                self.region_list.append(item["text"])
                    # 遍历sorts列表
                    for sort in data["sorts"]:
                        # 提取text
                        self.sort_list.append(sort["text"])

        try:
            page = await self.get_page()
            await asyncio.sleep(5)  # 等待5秒，等待数据加载完成
            page.on("response", on_request)

        except Exception as e:
            if self.error_count >= self.max_error_count:
                logging.error(
                    f"打开页面出现错误：{e}\n类型：{type(e)}\n堆栈跟踪：\n{traceback.format_exc()}"
                )
                logging.info("错误次数过多，即将关闭浏览器")
                # await self.close_browser()  # 手动关闭浏览器
                return
            logging.error(
                f"打开页面出现错误：{e}\n类型：{type(e)}\n堆栈跟踪：\n{traceback.format_exc()}"
            )
            logging.info("即将重新打开页面")
            self.error_count += 1
            await self.open_page()
            return

        logging.info("页面已经打开，首先获取所有的组合")
        await self.trySaveAllCombinations(page)
        await page.close()
        self.all_combinations_dicts = await self.getSavaJson()  # 获取保存的json数据
        logging.info(
            f"获取所有的组合完成，即将并发[并发量：{self.CONCURRENCY}]爬取————所有组合的数据"
        )
        if not self.all_combinations_dicts:
            logging.info(f"{self.dict}无组合，已经爬取完成，即将关闭浏览器")
            # await self.close_browser()  # 手动关闭浏览器
            return
        combinations_dicts = self.all_combinations_dicts  # 取所有数据
        tasks = [
            asyncio.ensure_future(self.drop_down_selection(combinations_dict))
            for combinations_dict in combinations_dicts
        ]
        # 使用asyncio.gather并发地运行所有的任务
        await asyncio.gather(*tasks)

        logging.info(f"{self.dict}————已经全部获取，立即关闭浏览器，程序运行完成。")

    # 获取所有的组合
    async def trySaveAllCombinations(self, page) -> None:
        """
        获取所有的组合
        """
        logging.info(f"获取所有{self.dict}的组合中……")
        if not await self.isSaveType():
            await page.click('//div[@class="explore-sticky"]//*[text()="类型"]')
            await self.random_sleep()
            await page.click(f'//div[@class="explore-sticky"]//*[text()="{self.type}"]')
            await page.wait_for_load_state("load")  # 等待页面加载完成
            await asyncio.sleep(5)  # 等待5秒，等待数据加载完成
            await self.saveAllCombinationsDict()

    # 下拉框选择，选择类型、地区、年代、平台、标签、排序
    async def drop_down_selection(self, combinations_dict):
        """
        下拉框选择，选择类型、地区、年代、平台、标签、排序
        """
        async with self.semaphore:
            isAll = [False]

            # 处理response
            async def on_request(response):
                """
                获取Ajax数据，并进行处理+保存数据
                """
                if (
                    "/recommend?refresh=0&start=" in response.url
                    and response.status == 200
                ):
                    try:
                        data = await response.json()
                        if not data["items"]:
                            isAll[0] = True
                            return
                        await self.save_data(data)  # 处理+保存数据
                    except Exception as e:
                        logging.error(
                            f"处理+保存数据出现错误：{e}\n类型：{type(e)}\n堆栈跟踪：\n{traceback.format_exc()}"
                        )

            logging.info(
                f"选择下拉框选项：type：{self.type}，dict：{combinations_dict}中……"
            )
            try:
                page = await self.get_page()
                await page.click('//div[@class="explore-sticky"]//*[text()="类型"]')
                await self.random_sleep()
                await page.click(
                    f'//div[@class="explore-sticky"]//*[text()="{self.type}"]'
                )
                await self.random_sleep()
                page.on("response", on_request)  # 处理response
                if combinations_dict.get("region"):
                    await page.click('//div[@class="explore-sticky"]//*[text()="地区"]')
                    await self.random_sleep()
                    await page.click(
                        f'//div[@class="explore-sticky"]//*[text()="{combinations_dict["region"]}"]'
                    )
                    await self.random_sleep()
                if combinations_dict.get("era"):
                    await page.click('//div[@class="explore-sticky"]//*[text()="年代"]')
                    await self.random_sleep()
                    await page.click(
                        f'//div[@class="explore-sticky"]//*[text()="{combinations_dict["era"]}"]'
                    )
                    await self.random_sleep()
                if combinations_dict.get("platform"):
                    await page.click('//div[@class="explore-sticky"]//*[text()="平台"]')
                    await self.random_sleep()
                    await page.click(
                        f'//div[@class="explore-sticky"]//*[text()="{combinations_dict["platform"]}"]'
                    )
                    await self.random_sleep()
                if combinations_dict.get("label"):
                    await page.click('//div[@class="explore-sticky"]//*[text()="标签"]')
                    await self.random_sleep()
                    await page.click(
                        f'//div[@class="explore-sticky"]//*[text()="{combinations_dict["label"]}"]'
                    )
                    await self.random_sleep()
                if combinations_dict.get("sort"):
                    await page.click('//div[@class="explore-sticky"]//*[text()="排序"]')
                    await self.random_sleep()
                    await page.click(
                        f'//div[@class="explore-sticky"]//*[text()="{combinations_dict["sort"]}"]'
                    )
                    await self.random_sleep()

            except Exception as e:
                if self.error_count >= self.max_error_count:
                    logging.error(
                        f"选择下拉框选项出现错误：{e}\n类型：{type(e)}\n堆栈跟踪：\n{traceback.format_exc()}"
                    )
                    logging.info("错误次数过多，即将关闭当前页面")
                    await page.close()
                    return
                logging.error(
                    f"选择下拉框选项出现错误：{e}\n类型：{type(e)}\n堆栈跟踪：\n{traceback.format_exc()}"
                )
                logging.info("即将关闭页面，重新打开后，进行下拉选择")
                await page.close()
                self.error_count += 1
                await self.drop_down_selection(combinations_dict)  # 重新选择选项
                return
            await self.slip_down(
                page=page, isAll=isAll, combinations_dict=combinations_dict
            )  # 向下滑动页面

    # 向下滑动页面
    async def slip_down(self, page, isAll, combinations_dict):
        """
        向下滑动页面，加载数据
        """
        try:
            while True:
                # 创建一个 Locator 对象
                load_more_button = page.locator("text=加载更多")
                # 检查按钮是否存在
                if await load_more_button.count() > 0:
                    # 按钮存在，可以执行操作
                    await load_more_button.focus(timeout=4000)
                    await self.random_sleep()
                    await load_more_button.click(timeout=8000)
                    await self.random_sleep()
                    await load_more_button.focus(timeout=4000)
                else:
                    break
                if isAll[0]:
                    break
        except Exception as e:
            pass
        finally:
            logging.info(f"组合：{combinations_dict}————已全部获取")
            await self.popOneCombination(combinations_dict)
            isAll[0] = False
            try:
                # await page.wait_for_load_state("load")  # 等待页面加载完成
                await asyncio.sleep(1)  # 延迟关闭页面，防止response未完成
                await page.close()
            except Exception as e:
                logging.error(
                    f"页面关闭时出现错误：{e}\n类型：{type(e)}\n堆栈跟踪：\n{traceback.format_exc()}"
                )

    # 关闭浏览器
    async def close_browser(self):
        await self.browser.close()
        return
