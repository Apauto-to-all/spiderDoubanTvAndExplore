# 免责声明

本项目仅供学习和研究使用，使用者应遵守相关法律法规，任何由使用者因违法使用所产生的后果，与本项目无关。[爬虫违法违规案例](https://github.com/HiddenStrawberry/Crawler_Illegal_Cases_In_China)

# 话不多说，先看效果

<video src="./asset/show.mp4" height="480px" autoplay="autoplay" loop="loop" controls="controls"></video> 

# 如何使用

1. 搭建python环境（当前测试环境：3.11.8版本），下载本项目的代码，安装必要的包
```python
# 当前测试使用的playwright版本
pip install playwright==1.43.0
# 安装好后你需要运行playwright install来下载对应版本的浏览器
playwright install
```

2. 首先登入豆瓣账户，修改`FunctionTvAndExplore.py`文件中的`def __init__(self) -> None:`数据
    - self.isHeadless = False # 关闭浏览器的无头选项
    - self.isLogin = True  # 选择登录（默认为True）
    - self.isLogin_isWait = True  # 打开页面后等待self.wait_time之久
    
    然后运行`__init__.py`文件，进行登入豆瓣

3. 完成登入后可以关闭浏览器，然后还原`FunctionTvAndExplore.py`文件中的`def __init__(self) -> None:`数据
    - self.isHeadless = True # 如果你希望设置为有头浏览器，也可以设置False
    - self.isLogin = True
    - self.isLogin_isWait = False

4. 之后，修改`FunctionTvAndExplore.py`文件中`async def save_data(self, data):`函数，为
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

5. 最后运行`__init__.py`文件，就能不断爬取信息。
>注意：
>
> 1. 设置了自动保存功能，每爬取`self.every_save_data_count`个组合就会保存一次数据，如果不希望运行了，可以直接选择退出
>
> 2. 在`__init__.py`文件中，可以自行修改`PlaywrightTvAndExplore(choice_dict)`中的choice_dict值，设置爬取的页面和类型，相关格式可以参考`MainRun`类中的`main()`函数
>
> 3. log日志会储存在目录下的`PlaywrightTvAndExplore.log`文件中
>
> 4. 提取出来的`导演`和`演员`会出现问题，因为人名是按空格分割的，而有些人名是非中文的……如果介意可以修改代码，不按空格分割人名

# 可选
`FunctionTvAndExplore.py`文件中：
1. self.CONCURRENCY = 3  # 最大并发量，不要设置太高
2. self.every_save_data_count = 5  # 每爬取多少个组合，保存一次数据

>……
>
>还有一些功能请自行探寻