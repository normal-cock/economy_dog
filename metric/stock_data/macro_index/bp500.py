'''
方案1 手动下载.通过macrotrends下载
* 访问https://www.macrotrends.net/2324/sp-500-historical-chart-data
* 然后通过console输出originalData
* 然后copy object到本地

方案2 尝试selenium
    https://www.google.com/search?q=linux+web+driver+for+selenium&sca_esv=fa927a4af76fe362&sxsrf=AHTn8zpctfeItgIB4iAwgEorCI2IZADjlw%3A1742551849381&ei=KTvdZ4TrFvHG0-kPi6Cp8Q0&ved=0ahUKEwjEo_C_95qMAxVx4zQHHQtQKt4Q4dUDCBA&uact=5&oq=linux+web+driver+for+selenium&gs_lp=Egxnd3Mtd2l6LXNlcnAiHWxpbnV4IHdlYiBkcml2ZXIgZm9yIHNlbGVuaXVtMggQABgIGA0YHjILEAAYgAQYhgMYigUyCxAAGIAEGIYDGIoFMgUQABjvBTIIEAAYgAQYogQyBRAAGO8FMgUQABjvBUjSPFCjCljDEHAAeAKQAQCYAaABoAHfBqoBAzAuNrgBA8gBAPgBAZgCBaACugTCAgQQABhHwgIHEAAYgAQYDcICBhAAGA0YHsICCBAAGAUYDRgewgIIECEYoAEYwwSYAwCIBgGQBgiSBwMxLjSgB4glsgcDMC40uAe4BA&sclient=gws-wiz-serp
    待进一步研究

方案3 requests_html以及类似的库
    底层用的库`pyppeteer`已经不维护了

方案4 Playwright
    https://github.com/microsoft/playwright-python?tab=readme-ov-file

'''
from akshare import stock_index_pe_lg

if __name__ == '__main__':
    # print(stock_index_pe_lg())
    # with pd.option_context('display.max_columns', None):
    # import akshare as ak

    # 获取标普500 ETF (SPY) 的实时行情数据
    # stock_individual_spot_xq_df = ak.stock_individual_spot_xq(symbol="SPY")
    # print(stock_individual_spot_xq_df)

    from requests_html import HTMLSession
    session = HTMLSession()
    r = session.get('https://python.org/')

    r.html.render()
    print(r.html.html)

from playwright.sync_api import sync_playwright


def get_js_variable(url, variable_name):
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch()
        page = browser.new_page()

        # 打开目标网页
        page.goto(url)

        # 执行 JavaScript 获取变量的值
        variable_value = page.evaluate(f"() => {{ return {variable_name}; }}")

        # 打印变量的值
        print(f"变量 {variable_name} 的值: {variable_value}")

        # 关闭浏览器
        browser.close()


# 使用示例
url = 'https://www.macrotrends.net/2577/sp-500-pe-ratio-price-to-earnings-chart'
variable_name = 'originalData'
get_js_variable(url, variable_name)
