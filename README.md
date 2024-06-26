# 免责声明

本项目仅供学习和研究使用，使用者应遵守相关法律法规，任何由使用者因违法使用所产生的后果，与本项目无关。[爬虫违法违规案例](https://github.com/HiddenStrawberry/Crawler_Illegal_Cases_In_China)

# 目录

- [免责声明](#免责声明)
- [项目说明](#项目说明)
- [使用前需要先搭建好环境](#使用前需要先搭建好环境)
- [如何使用：爬取豆瓣TV和豆瓣Explore页面](#如何使用爬取豆瓣tv和豆瓣explore页面)
- [如何使用：爬取豆瓣Chart页面](#如何使用爬取豆瓣chart页面)
- [可选](#可选)

# 项目说明

- 本项目基于playwright包，可以爬取[豆瓣TV](https://movie.douban.com/tv/)和[豆瓣Explore](https://movie.douban.com/explore)，以及[豆瓣Chart](https://movie.douban.com/chart)页面，获取电影和电视剧的相关信息。

- 在[豆瓣TV](https://movie.douban.com/tv/)页面和[豆瓣Explore](https://movie.douban.com/explore)页面，实现下拉框中选择不同标签，实现不同组合方式，深度挖掘电影/电视剧信息

- 在[豆瓣Chart](https://movie.douban.com/chart)页面，实现对所有分类排行榜标签进行爬取，从 `好于100%-90% 的~` 到 `好于10%-0% 的~`

# 使用前需要先搭建好环境
- 搭建python环境（当前测试环境：3.11.8版本），下载本项目的代码，安装必要的包
```python
# 当前测试使用的playwright版本
pip install playwright==1.43.0
# 安装好后你需要运行playwright install来下载对应版本的浏览器
playwright install
```

# 如何使用：爬取豆瓣TV和豆瓣Explore页面

- 该功能包含3个文件：`FunctionTvAndExplore.py`，`playwrightTvAndExplore.py`，`main_Tv_Explore.py`。

1. 首先登入豆瓣账户，修改`FunctionTvAndExplore.py`文件中的`def __init__(self) -> None:`数据
    - self.isHeadless = False # 关闭浏览器的无头选项
    - self.isLogin = True  # 选择登录（默认为True）
    - self.isLogin_isWait = True  # 打开页面后等待self.wait_time之久
    
    然后运行`main_Tv_Explore.py`文件，进行登入豆瓣

2. 完成登入后可以关闭浏览器，然后还原`FunctionTvAndExplore.py`文件中的`def __init__(self) -> None:`数据
    - self.isHeadless = True # 如果你希望设置为有头浏览器，也可以设置False
    - self.isLogin = True
    - self.isLogin_isWait = False

3. 之后，修改`FunctionTvAndExplore.py`文件中`async def save_data(self, data):`函数，为
```python
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
```
添加储存方式，推荐储存到数据库，项目内附有`explore样例.json`和`tv样例.json`2个样例文件，也可以自行参考其中的内容提取所需数据

4. 最后运行`main_Tv_Explore.py`文件，就能不断爬取信息。
>注意：
>
> 1. 设置了自动保存功能，每爬取`self.every_save_data_count`个组合就会保存一次数据，如果不希望运行了，可以直接选择退出
>
> 2. 在`main_Tv_Explore.py`文件中，可以自行修改`PlaywrightTvAndExplore(choice_dict)`中的choice_dict值，设置爬取的页面和类型，相关格式可以参考`MainRun`类中的`main()`函数
>
> 3. log日志会储存在目录下的`PlaywrightTvAndExplore.log`文件中
>
> 4. 提取出来的`导演`和`演员`会出现问题，因为人名是按空格分割的，而有些人名是非中文的……如果介意可以修改代码，不按空格分割人名

# 如何使用：爬取豆瓣Chart页面

- 该功能只包含1个文件：`playwrightChart.py`。

1. 登入豆瓣，与上面的第一步相同，如果已经实现了，可以跳过这个一步，修改`playwrightChart.py`内`FunChart`类的`def __init__(self):`：
    - self.isHeadless = False # 关闭浏览器的无头选项
    - self.isLogin = True  # 选择登录（默认为True）
    - self.isLogin_isWait = True  # 打开页面后等待self.wait_time之久
    - 然后直接运行`playwrightChart.py`文件，进行登入后，登入完成后可以直接退出浏览器。

2. 完成登入后可以关闭浏览器，然后还原`playwrightChart.py`文件中`FunChart`类的`def __init__(self):`：
    - self.isHeadless = True # 如果你希望设置为有头浏览器，也可以设置False
    - self.isLogin = True
    - self.isLogin_isWait = False

3. 之后，修改`playwrightChart.py`文件中`FunChart`类的`async def saveData(self, data):`函数：
```python
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
```
为其添加储存方式，同样推荐储存到数据库，项目内附有`chart样例.json`，也可以自行参考其中的内容提取所需数据。

4. 最后直接运行`playwrightChart.py`文件，就能不断爬取信息。

# 可选
在`FunctionTvAndExplore.py`文件中：
1. self.CONCURRENCY = 3  # 最大并发量，不要设置太高
2. self.every_save_data_count = 5  # 每爬取多少个组合，保存一次数据

>……
>
>还有一些功能请自行探寻