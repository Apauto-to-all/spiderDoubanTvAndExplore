# 用于打开浏览器的配置
import asyncio  # 异步io
import itertools  # 用于生成所有的组合
import json  # json模块
import logging  # 日志模块
import os  # os模块
import random  # 随机数，用于随机等待时间


# 一些功能的实现
class FunctionTvAndExplore:
    """
    一些功能的实现，用于爬取豆瓣电视剧和电影探索页面
    """

    def __init__(self) -> None:
        # 配置logging模块，将日志信息输出到log文件中
        logging.basicConfig(
            filename="PlaywrightTvAndExplore.log",
            level=logging.INFO,
            format="%(asctime)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            encoding="utf-8",
        )
        # 浏览器管理设置
        self.isHeadless = True  # 是否无头浏览器
        # 最大并发量
        self.CONCURRENCY = 3  # 最大并发量
        self.semaphore = asyncio.Semaphore(
            self.CONCURRENCY
        )  # 创建一个信号量，限制并发数量为self.CONCURRENCY
        self.error_count = 0  # 错误次数
        self.max_error_count = 5  # 最大错误次数
        # 是否登录，以及登录后是否等待
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
        # 初步提供的数据
        self.dict = {}  # 一些数据
        self.url = ""  # url
        self.type = ""  # 类型
        # 一些数据，在handle_tags_data和save_中提取
        self.region_list = []  # 地区
        self.era_list = []  # 年代
        self.platform_list = []  # 平台
        self.label_list = []  # 标签
        self.sort_list = []  # 排序
        # 所有组合保存的列表
        self.all_combinations_dicts = []  # 储存所有组合
        # 所有的组合，等待被爬的文件名
        self.doubanWaitToSpider = "doubanWaitToSpider"
        # 每爬取一定数量的组合，保存一次数据
        self.save_data_count = 0  # 爬取的组合数量
        self.every_save_data_count = 5  # 每爬取多少个组合，保存一次数据

    # 随机等待时间
    async def random_sleep(self):
        """
        随机等待时间
        """
        sleep_time = round(random.uniform(0.2, 0.8), 2)
        await asyncio.sleep(sleep_time)

    # 检查是否保存了目标type的组合数据
    async def isSaveType(self) -> bool:
        """
        检查是否保存了目标type的组合数据
        """
        # 检测路径是否存在，不存在则创建
        if not os.path.exists(self.doubanWaitToSpider):
            os.makedirs(self.doubanWaitToSpider)
        # 检测tv和explore文件夹是否存在，不存在则创建
        if not os.path.exists(f"{self.doubanWaitToSpider}/tv"):
            os.makedirs(f"{self.doubanWaitToSpider}/tv")
        if not os.path.exists(f"{self.doubanWaitToSpider}/explore"):
            os.makedirs(f"{self.doubanWaitToSpider}/explore")
        # 再次检测是否存在
        if self.url == "https://movie.douban.com/tv/":
            if os.path.exists(f"{self.doubanWaitToSpider}/tv/{self.type}.json"):
                return True
        elif self.url == "https://movie.douban.com/explore":
            if os.path.exists(f"{self.doubanWaitToSpider}/explore/{self.type}.json"):
                return True
        return False

    # 获取保存的json数据
    async def getSavaJson(self) -> list:
        """
        获取保存的json数据
        """
        if self.url == "https://movie.douban.com/tv/":
            with open(
                f"{self.doubanWaitToSpider}/tv/{self.type}.json", "r", encoding="utf-8"
            ) as f:
                data = json.load(f)
            logging.info(f"获取：tv/{self.type}.json数据完成！一共{len(data)}个组合！")
        elif self.url == "https://movie.douban.com/explore":
            with open(
                f"{self.doubanWaitToSpider}/explore/{self.type}.json",
                "r",
                encoding="utf-8",
            ) as f:
                data = json.load(f)
            logging.info(
                f"获取：explore/{self.type}.json数据完成！一共{len(data)}个组合！"
            )
        else:
            data = []
            logging.error("获取json数据失败！")

        return data

    # 弹出，去除一个已经完成爬取的组合
    async def popOneCombination(self, dict):
        """
        弹出，去除一个已经完成爬取的组合
        """
        try:
            self.save_data_count += 1  # 爬取的组合数量+1
            self.all_combinations_dicts.remove(dict)  # 去除这个组合
        except Exception as e:
            logging.error(f"所有组合中不存在这个组合！")
            return
        finally:
            logging.info(f"已弹出一个已经完成爬取的组合：{dict}")
        # 每爬取self.every_save_data_count个组合，保存一次数据
        if (
            self.save_data_count % self.every_save_data_count == 0
            or len(self.all_combinations_dicts) <= 3
        ):
            # 将数据保存到文件中
            if self.url == "https://movie.douban.com/tv/":
                loacl_path = f"{self.doubanWaitToSpider}/tv/{self.type}.json"
            elif self.url == "https://movie.douban.com/explore":
                loacl_path = f"{self.doubanWaitToSpider}/explore/{self.type}.json"

            with open(loacl_path, "w", encoding="utf-8") as f:
                json.dump(self.all_combinations_dicts, f, ensure_ascii=False, indent=4)

            logging.info(f"保存数据成功！")

    # 快速保存组合
    async def quickSaveCombination(self, waitSortList, all_combinations_dicts):
        """
        快速保存组合，waitSortList是需要排序的列表
        """
        # 将所有的列表保存到字典中，如果列表在waitSortList中，则保存，否则保存[None]
        dict_all = {
            "region": self.region_list if "region" in waitSortList else [None],
            "era": self.era_list if "era" in waitSortList else [None],
            "platform": self.platform_list if "platform" in waitSortList else [None],
            "label": self.label_list if "label" in waitSortList else [None],
            "sort": self.sort_list if "sort" in waitSortList else [None],
        }
        # 生成所有的组合
        all_combinations = list(
            itertools.product(
                dict_all["region"],
                dict_all["era"],
                dict_all["platform"],
                dict_all["label"],
                dict_all["sort"],
            )
        )
        for combination in all_combinations:
            combination_dict = {
                "region": combination[0],
                "era": combination[1],
                "platform": combination[2],
                "label": combination[3],
                "sort": combination[4],
            }
            all_combinations_dicts.append(combination_dict)

    # 保存所有的组合到文件中
    async def saveAllCombinationsDict(self):
        """
        生成所有的组合，并保存到文件中
        """
        all_list = f"""
地区：{self.region_list}
年代：{self.era_list}
平台：{self.platform_list}
标签：{self.label_list}
排序：{self.sort_list}
        """
        logging.info(f"所有的列表：{all_list}")
        # 将生成的组合转换为字典
        all_combinations_dicts = []
        if self.platform_list:  # tv选择电视剧
            waitSortList = ["region", "sort"]
            await self.quickSaveCombination(waitSortList, all_combinations_dicts)
            waitSortList = ["era", "sort"]
            await self.quickSaveCombination(waitSortList, all_combinations_dicts)
            waitSortList = ["platform", "sort"]
            await self.quickSaveCombination(waitSortList, all_combinations_dicts)
            waitSortList = ["label", "sort"]
            await self.quickSaveCombination(waitSortList, all_combinations_dicts)
            # waitSortList = ["era", "label", "sort"]
            # await self.quickSaveCombination(waitSortList, all_combinations_dicts)
            # waitSortList = ["platform", "label", "sort"]
            # await self.quickSaveCombination(waitSortList, all_combinations_dicts)

        else:  # explore选择电影
            waitSortList = ["region", "sort"]
            await self.quickSaveCombination(waitSortList, all_combinations_dicts)
            waitSortList = ["era", "sort"]
            await self.quickSaveCombination(waitSortList, all_combinations_dicts)
            waitSortList = ["label", "sort"]
            await self.quickSaveCombination(waitSortList, all_combinations_dicts)
            # waitSortList = ["era", "label", "sort"]
            # await self.quickSaveCombination(waitSortList, all_combinations_dicts)

        # 将数据保存到文件中
        if self.url == "https://movie.douban.com/tv/":
            loacl_path = f"{self.doubanWaitToSpider}/tv/{self.type}.json"
        elif self.url == "https://movie.douban.com/explore":
            loacl_path = f"{self.doubanWaitToSpider}/explore/{self.type}.json"

        with open(loacl_path, "w", encoding="utf-8") as f:
            json.dump(all_combinations_dicts, f, ensure_ascii=False, indent=4)

    # 处理tags数据
    async def handle_tags_data(self, data):
        """
        处理tags数据
        """
        if not self.label_list:
            # 遍历tags列表
            for tag in data["tags"]:
                # 如果type是"年代"，那么提取tags的内容
                if tag["type"] == "年代":
                    self.era_list = tag["tags"]
                if tag["type"] == "平台":
                    self.platform_list = tag["tags"]
                if tag["type"] == "标签":
                    self.label_list = tag["tags"]

    # 保存爬取的json数据
    async def save_data(self, data):
        """
        保存爬取的json数据
        """
        if not data["items"]:
            return
        items = data.get("items")
        for item in items:
            if not item.get("pic"):
                continue
            id = item.get("id")  # 豆瓣id，唯一
            title = item.get("title")  # 名称，一般为中文名
            try:
                year = int(item.get("year"))  # 上映年份
            except Exception as e:
                year = None
            douban_link = f"https://movie.douban.com/subject/{id}/"  # 豆瓣链接
            try:
                pic_normal = item.get("pic").get("normal")  # 普通图片链接
            except Exception as e:
                pic_normal = None
            try:
                pic_large = item.get("pic").get("large")  # 大图片链接
            except Exception as e:
                pic_large = None

            try:
                comment = item.get("comment").get("comment")  # 一条评论
            except Exception as e:
                comment = ""
            try:
                score_num = int(item.get("rating").get("count"))  # 评分人数
            except Exception as e:
                score_num = 0

            try:
                score = float(item.get("rating").get("value"))  # 评分
            except Exception as e:
                score = 0.0

            try:
                card_subtitle = item.get("card_subtitle")  # 副标题
                parts = card_subtitle.split(" / ")  # 分割副标题
                country = parts[1].split(" ")  # 国家
                genres = parts[2].split(" ")  # 类型
                directors = parts[3].split(" ")  # 导演
                actors = parts[4].split(" ")  # 演员
            except Exception as e:
                country = []
                genres = []
                directors = []
                actors = []

            try:
                item_type = item.get("type")  # 类型：tv或者movie
            except Exception as e:
                item_type = None
            # 保存数据，自行选择保存方式
            all_data = {
                "id": id,
                "标题": title,
                "上映年份": year,
                "豆瓣链接": douban_link,
                "普通图片链接": pic_normal,
                "大图片链接": pic_large,
                "一条评论": comment,
                "评分人数": score_num,
                "评分": score,
                "国家": country,
                "类型": genres,
                "导演": directors,
                "演员": actors,
                "tv or movie类型": item_type,
            }
            logging.info(f"抓取数据——id：{id}，标题：{title}")
