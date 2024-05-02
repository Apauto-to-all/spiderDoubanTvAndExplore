from playwrightTvAndExplore import PlaywrightTvAndExplore
import random


tv_type = [
    "不限类型",
    "全部剧集",
    "全部综艺",
    "喜剧",
    "爱情",
    "悬疑",
    "动画",
    "武侠",
    "古装",
    "家庭",
    "犯罪",
    "科幻",
    "恐怖",
    "历史",
    "战争",
    "动作",
    "冒险",
    "传记",
    "剧情",
    "奇幻",
    "惊悚",
    "灾难",
    "歌舞",
    "音乐",
    "真人秀",
    "脱口秀",
    "音乐",
    "歌舞",
]
explore_type = [
    "全部类型",
    "喜剧",
    "爱情",
    "动作",
    "科幻",
    "动画",
    "悬疑",
    "犯罪",
    "惊悚",
    "冒险",
    "音乐",
    "历史",
    "奇幻",
    "恐怖",
    "战争",
    "传记",
    "歌舞",
    "武侠",
    "情色",
    "灾难",
    "西部",
    "纪录片",
    "短片",
]


# 异步运行
class MainRun:
    def __init__(self):
        self.choice_list = []  # 选择的类型列表
        self.main()

    def main(self):
        for tv in tv_type:
            choice_tv = {
                "url": "https://movie.douban.com/tv/",
                "type": tv,
            }
            self.choice_list.append(choice_tv)
        for explore in explore_type:
            choice_explore = {
                "url": "https://movie.douban.com/explore",
                "type": explore,
            }
            self.choice_list.append(choice_explore)
        # 对self.choice_list列表进行随机排序
        random.shuffle(self.choice_list)
        for choice_dict in self.choice_list:  # 遍历列表
            PlaywrightTvAndExplore(choice_dict)  # 爬取每个类型的数据


MainRun()
