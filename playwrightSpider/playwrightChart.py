import asyncio  # 异步io
import json
import os  # 操作系统
import random  # 随机数
import sys
import traceback  # 系统
from playwright.async_api import async_playwright  # 异步Playwright
import logging  # 日志模块

# 配置logging模块，将日志信息输出到log文件中
logging.basicConfig(
    filename="PlaywrightChart.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)


class FunChart:
    def __init__(self):
        self.url = "https://movie.douban.com/chart"
        # 浏览器设置
        self.isHeadless = True  # 是否无头模式

        # 并发设置
        self.CONCURRENCY = 3  # 最大并发量
        self.semaphore = asyncio.Semaphore(
            self.CONCURRENCY
        )  # 创建一个信号量，限制并发数量为self.CONCURRENCY

        # 登入设置
        self.isLogin = True  # 是否登录
        self.isLogin_user_data_name = "douban_user_data_dir"  # 用户数据目录，路径
        self.isLogin_user_data_path = os.path.abspath(
            self.isLogin_user_data_name
        )  # 用户数据目录，绝对路径
        self.isLogin_isWait = False  # 是否在打开页面后等待self.wait_time之久
        self.isLogin_wait_time = 100  # 等待时间
        self.isLogin_wait_url = (
            "https://movie.douban.com/"  # 如果需要等待，则打开的的url，用于登入之类的
        )

        # 储存用于爬取的数据字典
        self.allSpiderLinks = []

        # 所有的需要爬取的链接，保存的文件夹
        self.doubanWaitToSpider = "doubanWaitToSpider"  # 储存的文件夹

    # 保存爬取的数据
    async def saveData(self, data):
        """
        保存爬取的数据
        """
        for item in data:
            id = item.get("id", None)  # id
            title = item.get("title", None)  # 标题
            douban_link = f"https://movie.douban.com/subject/{id}/"  # 豆瓣链接
            pic_normal = item.get("cover_url", None)  # 普通图片链接
            score = float(item.get("score", 0.0))  # 评分
            score_num = int(item.get("vote_count", 0))  # 评分人数
            genres = item.get("types", [])  # 类型
            country = item.get("regions", [])  # 国家
            release_date = item.get("release_date", None)  # 上映日期
            actors = item.get("actors", [])  # 演员
            item_type = "movie"  # 类型

            logging.info(f"id: {id}，标题: {title}")  # 同样需要自行完成数据储存的功能

    # 随机等待时间
    async def random_sleep(self):
        """
        随机等待时间
        """
        sleep_time = round(random.uniform(0.2, 0.8), 2)
        await asyncio.sleep(sleep_time)

    # 是否保存Chart所有的链接
    async def isSaveChartLinks(self):
        """
        是否已经保存Chart所有的链接
        """
        # 检测路径是否存在，不存在则创建
        if not os.path.exists(self.doubanWaitToSpider):
            os.makedirs(self.doubanWaitToSpider)
        # 检测chart文件是否存在，不存在则创建
        if os.path.exists(f"{self.doubanWaitToSpider}/chart.json"):
            return True
        else:
            return False

    # 保存Chart所有的链接的数据
    async def saveChartLinks(self, data):
        """
        保存Chart所有的链接的数据
        """
        with open(f"{self.doubanWaitToSpider}/chart.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)  # 写入数据

    # 获取之前保存的Chart所有的链接的数据
    async def getChartLinks(self):
        """
        获取之前保存的Chart所有的链接的数据
        """
        with open(f"{self.doubanWaitToSpider}/chart.json", "r", encoding="utf-8") as f:
            data = json.load(f)  # 加载数据
        return data  # 返回数据


class PlaywrightChart(FunChart):
    """
    利用Playwright爬取豆瓣电影排行榜
    """

    def __init__(self):
        super().__init__()  # 调用父类的 __init__ 方法
        asyncio.run(self.open_browser())  # 运行open_browser方法

    # 打开浏览器
    async def open_browser(self):  # 打开浏览器
        """
        打开浏览器
        """
        logging.info("打开浏览器中……")
        if await self.isSaveChartLinks() and not await self.getChartLinks():
            logging.info("数据已经爬取完成，无需再次运行，退出程序中……")
            logging.info(
                f"如果需要重新爬取数据，请删除{self.doubanWaitToSpider}文件夹中的chart.json文件"
            )
            return
        async with async_playwright() as p:
            if self.isLogin:  # 如果选择登录，设置用户数据目录
                self.browser = await p.chromium.launch_persistent_context(
                    user_data_dir=self.isLogin_user_data_path,  # 用户数据目录
                    headless=self.isHeadless,  # 是否无头模式
                    ignore_default_args=[
                        "--enable-automation"
                    ],  # 禁止弹出Chrome正在受到自动软件的控制的通知
                )
            else:
                self.browser = await p.chromium.launch(
                    headless=self.isHeadless,  # 是否无头模式
                    ignore_default_args=[
                        "--enable-automation"
                    ],  # 禁止弹出Chrome正在受到自动软件的控制的通知
                )
            logging.info(f"浏览器已经打开，即将打开页面")
            await self.open_page()  # 打开页面

    # 获取一个新的页面
    async def get_page(self, url):
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
        await page.goto(url)
        await page.wait_for_load_state("load")  # 等待页面加载完成
        # await page.wait_for_load_state("networkidle")  # 等待网络空闲
        await self.random_sleep()
        return page

    # 打开页面
    async def open_page(self):
        """
        打开页面，获取数据页面
        """
        if not await self.isSaveChartLinks():  # 如果没有保存数据，则获取数据
            page = await self.get_page(self.url)  # 打开页面
            # 获取所有分类排行榜的链接和名称
            all_elements = await page.query_selector_all(
                ".types span a"
            )  # 用css选择器获取所有分类排行榜的链接
            all_links = []  # 存储所有链接
            from urllib.parse import urljoin  # urljoin方法，拼接url
            import re  # 正则表达式，用于替换url

            for element in all_elements:
                # /typerank?type_name=历史&type=4&interval_id=100:90&action=，需要替换interval_id的值
                relative_url = await element.get_attribute("href")  # 获取链接
                for i in range(100, 0, -10):  # 从100开始，每次减少10
                    re_url = re.sub(  # 替换url
                        "interval_id=(\d+):(\d+)",
                        f"interval_id={i}:{i-10}",
                        relative_url,
                    )
                    full_url = urljoin(self.url, re_url)  # 拼接url
                    all_links.append(full_url)  # 存储拼接后的url
            # 存储所有链接
            await self.saveChartLinks(all_links)  # 保存所有链接
            await self.random_sleep()  # 随机等待时间
            await page.close()  # 关闭页面

        # 开始爬取所有链接
        self.allSpiderLinks = await self.getChartLinks()  # 获取所有链接

        tasks = [
            asyncio.ensure_future(self.spiderAll(link)) for link in self.allSpiderLinks
        ]
        # 使用asyncio.gather并发地运行所有的任务
        await asyncio.gather(*tasks)

    # 开始爬取所有链接的数据
    async def spiderAll(self, link):
        """
        开始爬取所有链接的数据
        """
        async with self.semaphore:  # 限制并发数量
            slip_count = -1  # 需要下滑加载数据的次数
            load_count = 0  # 加载次数

            # 处理response
            async def on_request(response):
                """
                获取Ajax数据，并进行处理+保存数据
                """
                nonlocal slip_count, load_count  # nonlocal声明，可以修改外部变量slip_count, load_count
                if "/top_list_count?type" in response.url and response.status == 200:
                    # 提取出最大下滑次数
                    try:
                        data = await response.json()
                        max_total = data.get("total", 0)  # 最多爬取的数据量
                        slip_count = (
                            max_total // 20 + 1
                        )  # 每次加载20条数据，计算需要下滑的次数
                    except Exception as e:
                        logging.error(
                            f"处理+保存数据出现错误：{e}\n类型：{type(e)}\n堆栈跟踪：\n{traceback.format_exc()}"
                        )

                if "/top_list?type=" in response.url and response.status == 200:
                    load_count += 1  # 加载次数+1
                    try:
                        data = await response.json()
                        await self.saveData(data)  # 保存爬取的数据
                    except Exception as e:
                        logging.error(
                            f"处理+保存数据出现错误：{e}\n类型：{type(e)}\n堆栈跟踪：\n{traceback.format_exc()}"
                        )

            logging.info(f"开始爬取链接：{link}")  # 开始爬取链接
            page = await self.get_page(link)  # 打开页面
            page.on("response", on_request)  # 监听response事件
            await page.reload()  # 重新加载页面，重新触发response事件
            await page.wait_for_load_state("load")  # 等待页面加载完成
            # 不断下滑，直到没有新的数据
            try:
                while True:
                    # 不断下滑
                    await page.evaluate(
                        "window.scrollTo(0, document.body.scrollHeight)"
                    )
                    # await page.wait_for_load_state("networkidle")  # 等待网络空闲
                    await page.wait_for_load_state("load")  # 等待页面加载完成
                    await self.random_sleep()  # 随机等待时间
                    if load_count == slip_count:  # 如果加载次数等于下滑次数，退出循环
                        break
                logging.info(f"爬取数据完成：{link}")  # 爬取数据完成
                self.allSpiderLinks.remove(link)  # 移除已经爬取的链接
                await self.saveChartLinks(self.allSpiderLinks)  # 保存剩余的链接
            except Exception as e:
                logging.error(
                    f"爬取数据出现错误：{e}\n类型：{type(e)}\n堆栈跟踪：\n{traceback.format_exc()}"
                )
            finally:
                await self.random_sleep()  # 随机等待时间
                await page.close()  # 关闭页面，爬取下一个链接


if __name__ == "__main__":
    play = PlaywrightChart()
