
- [格式](#格式)
- [新关注指标](#新关注指标)
- [抓取](#抓取)
    - [思路1-zhongjing](#思路1-zhongjing)
    - [思路2-国家统计局](#思路2-国家统计局)
    - [思路3-baidu](#思路3-baidu)
    - [中国房价行情网（待研究）](#中国房价行情网待研究)
    - [世界银行数据](#世界银行数据)
    - [上交所和深交所](#上交所和深交所)
- [TODO](#todo)
    - [v0.2](#v02)
- [DONE](#done)
    - [初版v0.1](#初版v01)
  
## 格式

人口超500万的地级市+副省级+直辖市+省
* 人口
    * 1年数据（如果数据太多，用分别用0.3%和1%作为过滤条件）
        * 人口增长top10
        * 人口增长last10
    * 10年数据
        * 人口增长top10
        * 人口增长last10
    * 人口总量
        * TopList
        * LastList
* GDP
    * 1年数据
        * gdp增长top10
        * gdp增长last10
    * 10年gdp增长top10
        * gdp增长top10
        * gdp增长last10
    * GDP总量
        * TopList
        * LastList
    * 人均GDP
        * TopList
        * LastList
* 重点关注城市
    * 本年人口
    * 去年人口
    * 10年前人口
    * 1年人口增长率
    * 10年人口增长率
    * 本年gdp
    * 去年gdp
    * 10年前gdp
    * 1年gdp增长率
    * 10年gdp增长率

## 新关注指标

房价指数

## 抓取

### 思路1-zhongjing

1. 在`https://wap.ceidata.cei.cn/`页面通过`https://wap.ceidata.cei.cn/listSquences`拿到数据的ID
2. 通过查询`https://wap.ceidata.cei.cn/detail?id={id}`查询

### 思路2-国家统计局

https://data.stats.gov.cn/search.htm?s=%E6%88%90%E9%83%BD%20%E6%88%BF%E4%BB%B7%E6%8C%87%E6%95%B0

### 思路3-baidu

城市列表自己挑选
使用baidu的web端接口

### 中国房价行情网（待研究）

相关指标：
房价、租房价、租售比

https://zhuanlan.zhihu.com/p/50158234

### 世界银行数据

人口: https://data.worldbank.org.cn/indicator/SP.POP.65UP.TO.ZS?locations=US&most_recent_value_desc=true

### 上交所和深交所

A股总市值
上交所：http://www.sse.com.cn/market/view/
深交所：http://www.szse.cn/market/overview/index.html

## TODO

### v0.2

人口和GDP中，省份和城市分开统计——Done
使用df.rename(columns={'xxx':'readable name'}, inplace=True)来展示列名——Done
日报：——Done
    A股总市值可以用上交所总市值代替，看比例都是一样的。观察当前proportion在过去十年的50分位的对比
    大趋势：A股总市值/上一年GDP。关注相同月份的年同比变化
cased city中标出每个指标的强、中、弱（强代表超过>=75分位，中代表75分位> >25分位，弱代表低于<=25分位）——Done
70城房价指数

## DONE

### 初版v0.1

DB中增加每个area_code的最新更新时间（直接根据当前库中的changed_time来决定），在core_model中增加`changed_time`，若干查询该area_code时发现数据过老或者没有数据，自动下载。已经下载过的就不用自动下载了——Done
通过`full_name`添加cared_city——Done
通过命令行区分下载和生成报表——Done
html的目录、表头的悬浮——Done
重点关注城市。500万人口以上，且1年gdp增速、10年gdp增速在50%以上，1年人口增速、10年人口增速在75%以上的城市——Done
发邮件。用附件发送html，能够预览，然后用css限制mobile情况下的body的width，方便左右滑动——DONE

