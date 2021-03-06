# <center>爬虫整理

    什么是爬虫？
    请求网站并提取数据的自动化程序

## 爬虫基本流程

1. 发起请求

        通过Http库向目标站点发起Request请求，请求会包含Header等信息，等待服务器响应

2. 获取响应数据

        服务器对我们的请求进行响应，得到一个Response,正常返回的话，Response的内容就是我们想要的页面内容，类型可能有Html，Json等字符串，二进制数据（图片，视频等类型）

3. 解析内容

        得到响应内容如果是Html，可以借助正则表达式，网页解析库（BeautifulSoup,PyQuery,XPath等）来进行解析。如果是Json,那太棒了(应该是请求了某个后端接口，没办法，后端出身^_^)，直接转换呈Json对象，要什么取什么。如果是二进制数据，可以保存或者做进一步的处理。

4. 保存数据

        可以保存到数据库，也可以保存到特定的文件格式，比如文本，CSV等。


```
    请求得到的数据的和浏览器得到的数据为什么不一样？
    如果做过web开发的话，这个就很好理解了，现在网站基本上都是前端通过Ajax异步请求后端拿到数据之后浏览器会再渲染页面，所以会导致我们请求得到的数据会和页面上的数据不一样，那么怎么解决这个问题呢？很简单，分析Ajax请求返回的数据，一般是Json格式，或者是用Selenium的webDriver模拟浏览器进行访问。
```


## 常用库

* Urlib
Python内置的Http请求库

        urllib.request      请求模块
        urllib.error        异常处理模块
        urllib.parse        url解析模块
        urllib.robotparser  robots.txt解析模块

* Request

            基于urllib库，更容易使用

* 正则表达式 re模块

        尽量使用泛型匹配
        使用括号得到匹配目标
        尽量使用非贪婪模式
        有换行符就用re.S
        为匹配方便，能用search就不用match

* BeautifulSoup

        推荐使用lxml解析库，必要时使用html.parser
        标签选择筛选功能弱但是速度快
        建议使用find（）,find_all()查询匹配单个或者多个结果
        如果对CSS选择器熟悉，建议使用select()
        记住常用的获取属性值和文本值的方法

* PyQuery

        熟悉JQuery的话，PyQuery简直好用的不得了
* Selenium

        自动化测试工具，支持多种浏览器
        爬虫中主要用来解决JavaScript渲染的问题



### 实战

* Request+re爬取猫眼电影

        先对猫眼电影的榜单页面进行目标站点分析，明确需要爬取的信息以及分析目标站点的网页结构

    思路：

        1. 使用Request库请求目标站点，得到单个网站的HTML内容，返回该内容
        2. 使用re解析返回的HTML内容，解析出电影名称，主演，上映时间，评分，排名等信息
        3. 将解析结果以Json形式保存到文件

* Ajax抓取今日头条
            
         这类网站就是通过的Ajax请求后台拿到数据之后再渲染页面，不能直接请求页面获取数据，这个类型是比较流行的，因为现在网站基本上都是前后端分离的项目
                    
    思路：
        
        1. 抓取索引页内容，使用Requests库请求目标站点，得到HTML内容，返回该内容
        2. 抓取详情页内容，解析索引页返回的结果，得到详情页的链接，并进一步抓取详情页的信息。
        3. 下载图片到文件夹，将相关信息保存MongoDB

* Selenium爬取淘宝信息
    
            现在的网站基本上都是前后端分离，这种时候想要获取我们想要的信息都得费很大力气去分析前台是如何请求后台接口的，这个时候可以使用selenium来驱动浏览器来获取我们想要的数据
    
    
        
    思路：
        
        1. 搜索关键字，利用Selenium驱动浏览器来搜索关键字，得到查询后的商品列表
        2. 分析页码并翻页，得到商品页码数，模拟翻页，得到后续页面的商品列表。
        3. 分析提取商品内容，利用PyQuery解析出得到商品列表
        4. 保存商品列表信息到MongoDB

 
* 爬取拉钩职位信息：

    ![](lagou/goal.png)
    
    一共爬到了120个岗位，筛选了一下500人以上规模和1-3年经验的公司，只剩下14个岗位，其中还有几个是外包的，
    这就有点尴尬了，1-3年真的是一个很尴尬的存在

### 持续更新ING...
