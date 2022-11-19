from typing import List
from datetime import date
import pandas as pd
from biz.annual_report import annual_report_result_v2
from model.core import AreaEconomyInfo
import re
from bs4 import BeautifulSoup

from util.email import send_html_as_attachment

style = '''
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta charset=utf-8>
</head>
<style>
    body {
        margin-left: 200px;
    }

    aside {
        left: 0px;
        top: 0px;
        position: fixed;
        width: 200px;
        height: 100%;
        z-index: 301;
        background-color: white;
        padding-top: 200px;
        line-height: 30px;
    }
    .stat_head {font-weight: bold;}
    .stat_detail {padding: 0 24px 2px;}
    .stat_detail_head {font-size: 13px;font-weight: bold;}

    table,table tr th, table tr td { border:1px solid #CDB7B5; font-family: Times, TimesNR, 'New Century Schoolbook',
    Georgia, 'New York', serif;}
    tr {height: 24px;font-size: 15px;}
    td {word-break: keep-all; padding: 0 8px 2px;}
    table {
        width: 100%;
        line-height: 24px;
        text-align: center;
        border-collapse: collapse;
        padding:2px;
    }
    table th {
        font-size: 16px;
        font-weight: bold;
        line-height: 17px;
        padding: 0 8px 2px;
        text-align:center;
        background-color: #DCDCDC;
        position: sticky;
        top: 0;
        left: 200px;
    }

    .blank {
        z-index: 301;
        background-color: #DCDCDC;
    }

    table tr:nth-child(even){
        background: #f2f2f2;
    }
    tr td:first-child{
        font-size: 13px;
        font-weight: bold;
        line-height: 14px;
        padding: 0 8px 2px;
        text-align:center;
    }
    caption{
        font-size: 150%;
        margin: 10px;
    }
</style>
'''

_RENAME_DICT = {
    'last_data_year': '数据年份',
    'population_ten_year_growth_rate': '10年来平均每年人口增长率',
    'ten_year_population': '10年前人口数（万）',
    'cur_population': '当前人口数（万）',
    'cur_gdp': '当前GDP（亿元）',
    'cur_gdp_per_capita': '当前人均GDP（万元）',
    'population_one_year_growth_rate': '人口最近1年增长率',
    'one_year_population': '上一年人口数（万）',
    'gdp_ten_year_growth_rate': '10年来平均每年GDP增长率',
    'ten_year_gdp': '10年前GDP（亿元）',
    'ten_year_gdp': '10年前GDP（亿元）',
    'gdp_one_year_growth_rate': 'GDP最近1年增长率',
    'one_year_gdp': '上一年GDP（亿元）',
}

_REVERSE_RENAME_DICT = {}


def _get_origin_name_before_rename(human_name):
    if len(_REVERSE_RENAME_DICT) == 0:
        for k in _RENAME_DICT:
            _REVERSE_RENAME_DICT[_RENAME_DICT[k]] = k
    return _REVERSE_RENAME_DICT.get(human_name, '')


def color_non_zero_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    return 'color: #111111; font-weight: bold' if val > 0 else ''


def highlight_cols(s, col_list):
    if _get_origin_name_before_rename(s.name) in col_list:
        # return ['background-color: grey'] * len(s)
        return ['font-weight:bold;'] * len(s)
    return [''] * len(s)


def mark_qualitle_cols(s, mark_quantile, quantile_info):
    result = []
    origin_name = _get_origin_name_before_rename(s.name)
    if mark_quantile and origin_name in quantile_info:
        tmp_q_info = quantile_info[origin_name]
        for v in s:
            if v >= tmp_q_info['75%']:
                result.append('color: red;')
            elif v >= tmp_q_info['50%']:
                result.append('color: rgb(255, 154, 154);')
            elif v >= tmp_q_info['25%']:
                result.append('color: rgb(129, 174, 129);')
            else:
                result.append('color: green;')
        return result
    return [''] * len(s)


def _render_aei_list(
    aei_list: List[AreaEconomyInfo],
    table_title: str,
    column_list: List[str],
    highlight_col_list: List[str],
    mark_quantile: bool = False,
    quantile_info: dict = {},
) -> str:
    dict_list = [item.gen_dict() for item in aei_list]
    index_list = [item['area'] for item in dict_list]
    aei_list_df = pd.DataFrame(
        dict_list,
        index=index_list
    )
    aei_list_df = aei_list_df[column_list]
    aei_list_df.rename(columns=_RENAME_DICT, inplace=True)
    html = (
        aei_list_df.style.format(precision=2).
        apply(
            mark_qualitle_cols, mark_quantile=mark_quantile, quantile_info=quantile_info).
        apply(
            highlight_cols, col_list=highlight_col_list).
        set_caption(table_title).to_html()
    )

    return html


def _gen_toc(html, ignore_h1_in_toc=False):
    if ignore_h1_in_toc:
        first_level = 2
    else:
        first_level = 1

    soup = BeautifulSoup(html, 'html.parser')
    headers = soup.findAll(re.compile('^h[%d-6]' % first_level))
    output = []
    for header in headers:
        hid = header.get('id')
        title = header.text
        level = int(header.name[-1])
        if hid:
            output.append('%s<a href="#%s">%s</a>' % (
                (level - first_level) * 4 * '&nbsp;', hid, title))
        else:
            output.append('%s%s' %
                          ((level - first_level) * 4 * '&nbsp;', title))
    return '<br/>\n'.join(output)


def annual_report_email_v2():
    pd.options.display.float_format = '{:,.2f}'.format

    cur_date = date.today()
    cur_date = cur_date.replace(year=cur_date.year-1)
    dto = annual_report_result_v2(cur_date)

    quantile_info = {
        k: dto.common_city_df[k].describe() for k in _RENAME_DICT if k not in ['last_data_year']
    }

    # 人口1.
    # 人口1.1. 10年平均增长率
    column_list = [
        "last_data_year", "population_ten_year_growth_rate",
        "ten_year_population", "cur_population", "cur_gdp", "cur_gdp_per_capita"
    ]
    highlight_col_list = [
        'population_ten_year_growth_rate', 'ten_year_population']
    city_population_growth_rate_ten_year_top10_html = _render_aei_list(
        dto.population_ten_year_growth_rate_top10_city,
        'top city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    city_population_growth_rate_ten_year_last10_html = _render_aei_list(
        dto.population_ten_year_growth_rate_last10_city,
        'last city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    province_population_growth_rate_ten_year_top10_html = _render_aei_list(
        dto.population_ten_year_growth_rate_top10_province,
        'top province list',
        column_list,
        highlight_col_list,
    )
    province_population_growth_rate_ten_year_last10_html = _render_aei_list(
        dto.population_ten_year_growth_rate_last10_province,
        'last province list',
        column_list,
        highlight_col_list,
    )

    # 人口1.2. 1年增长率
    column_list = [
        "last_data_year", "population_one_year_growth_rate",
        "one_year_population", "cur_population", "cur_gdp", "cur_gdp_per_capita"
    ]
    highlight_col_list = [
        'population_one_year_growth_rate', 'one_year_population']

    city_population_growth_rate_one_year_top10_html = _render_aei_list(
        dto.population_one_year_growth_rate_top10_city,
        'top city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    city_population_growth_rate_one_year_last10_html = _render_aei_list(
        dto.population_one_year_growth_rate_last10_city,
        'last city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    province_population_growth_rate_one_year_top10_html = _render_aei_list(
        dto.population_one_year_growth_rate_top10_province,
        'top province list',
        column_list,
        highlight_col_list,
    )
    province_population_growth_rate_one_year_last10_html = _render_aei_list(
        dto.population_one_year_growth_rate_last10_province,
        'last province list',
        column_list,
        highlight_col_list,
    )

    # 人口1.3. 人口总量
    column_list = [
        "last_data_year", "cur_population",
        "population_ten_year_growth_rate", "cur_gdp", "cur_gdp_per_capita"
    ]
    highlight_col_list = [
        'cur_population', 'population_ten_year_growth_rate']
    city_population_top_list_html = _render_aei_list(
        dto.population_top_list_city,
        'top city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    city_population_last_list_html = _render_aei_list(
        dto.population_last_list_city,
        'last city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    province_population_top_list_html = _render_aei_list(
        dto.population_top_list_province,
        'top province list',
        column_list,
        highlight_col_list,
    )
    province_population_last_list_html = _render_aei_list(
        dto.population_last_list_province,
        'last province list',
        column_list,
        highlight_col_list,
    )

    # GDP
    # GDP2.1. 10年平均增长率
    column_list = [
        "last_data_year", "gdp_ten_year_growth_rate",
        "ten_year_gdp", "cur_population", "cur_gdp", "cur_gdp_per_capita",
        'population_ten_year_growth_rate',
    ]
    highlight_col_list = [
        'gdp_ten_year_growth_rate', 'ten_year_gdp']
    city_gdp_ten_year_growth_rate_top10_html = _render_aei_list(
        dto.gdp_ten_year_growth_rate_top10_city,
        'top city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    city_gdp_ten_year_growth_rate_last10_html = _render_aei_list(
        dto.gdp_ten_year_growth_rate_last10_city,
        'last city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    province_gdp_ten_year_growth_rate_top10_html = _render_aei_list(
        dto.gdp_ten_year_growth_rate_top10_province,
        'top province list',
        column_list,
        highlight_col_list,
    )
    province_gdp_ten_year_growth_rate_last10_html = _render_aei_list(
        dto.gdp_ten_year_growth_rate_last10_province,
        'last province list',
        column_list,
        highlight_col_list,
    )

    # GDP2.2. 1年增长率
    column_list = [
        "last_data_year", "gdp_one_year_growth_rate",
        "one_year_gdp", "cur_population", "cur_gdp", "cur_gdp_per_capita",
        'population_ten_year_growth_rate',
    ]
    highlight_col_list = [
        'gdp_one_year_growth_rate', 'one_year_gdp']
    city_gdp_one_year_growth_rate_top10_html = _render_aei_list(
        dto.gdp_one_year_growth_rate_top10_city,
        'top city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    city_gdp_one_year_growth_rate_last10_html = _render_aei_list(
        dto.gdp_one_year_growth_rate_last10_city,
        'last city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    province_gdp_one_year_growth_rate_top10_html = _render_aei_list(
        dto.gdp_one_year_growth_rate_top10_province,
        'top province list',
        column_list,
        highlight_col_list,
    )
    province_gdp_one_year_growth_rate_last10_html = _render_aei_list(
        dto.gdp_one_year_growth_rate_last10_province,
        'last province list',
        column_list,
        highlight_col_list,
    )

    # GDP2.3. GDP总量
    column_list = [
        "last_data_year", "cur_population",
        "cur_gdp", "gdp_ten_year_growth_rate", "cur_gdp_per_capita",
        'population_ten_year_growth_rate',
    ]
    highlight_col_list = [
        'cur_gdp', 'gdp_ten_year_growth_rate']
    city_gdp_top_list_html = _render_aei_list(
        dto.gdp_top_list_city,
        'top city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    city_gdp_last_list_html = _render_aei_list(
        dto.gdp_last_list_city,
        'last city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    province_gdp_top_list_html = _render_aei_list(
        dto.gdp_top_list_province,
        'top province list',
        column_list,
        highlight_col_list,
    )
    province_gdp_last_list_html = _render_aei_list(
        dto.gdp_last_list_province,
        'last province list',
        column_list,
        highlight_col_list,
    )

    # GDP2.4. 人均GDP
    column_list = [
        "last_data_year", "cur_population",
        "cur_gdp", "cur_gdp_per_capita", "gdp_ten_year_growth_rate",
        'population_ten_year_growth_rate',
    ]
    highlight_col_list = ['cur_gdp_per_capita', "gdp_ten_year_growth_rate"]
    city_gpc_top_list_html = _render_aei_list(
        dto.gpc_top_list_city,
        'top city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    city_gpc_last_list_html = _render_aei_list(
        dto.gpc_last_list_city,
        'last city list',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )
    province_gpc_top_list_html = _render_aei_list(
        dto.gpc_top_list_province,
        'top province list',
        column_list,
        highlight_col_list,
    )
    province_gpc_last_list_html = _render_aei_list(
        dto.gpc_last_list_province,
        'last province list',
        column_list,
        highlight_col_list,
    )

    # 3. cared city
    column_list = [
        "last_data_year", 'cur_gdp_per_capita', 'cur_population',
        'population_ten_year_growth_rate', 'gdp_ten_year_growth_rate',
        'population_one_year_growth_rate', 'gdp_one_year_growth_rate',
        'cur_gdp'
    ]

    highlight_col_list = []
    # import ipdb
    # ipdb.set_trace()
    cared_area_html = _render_aei_list(
        dto.cared_area,
        'cared city',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )

    # 4. high quality area
    column_list = [
        "last_data_year", 'cur_gdp_per_capita', 'cur_population',
        'population_ten_year_growth_rate', 'gdp_ten_year_growth_rate',
        'population_one_year_growth_rate', 'gdp_one_year_growth_rate',
        'cur_gdp'
    ]
    highlight_col_list = []
    high_quality_area_html = _render_aei_list(
        dto.high_quality_area,
        'high quality area',
        column_list,
        highlight_col_list,
        mark_quantile=True,
        quantile_info=quantile_info,
    )

    content = f'''
    <h1 id="1. 人口（单位万）">1. 人口（单位万）</h1>
    <h2 id="1.1. 10年平均增长率">1.1. 10年平均增长率</h2>
    {dto.common_city_df['population_ten_year_growth_rate'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {city_population_growth_rate_ten_year_top10_html}
    {city_population_growth_rate_ten_year_last10_html}
    {dto.common_province_df['population_ten_year_growth_rate'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {province_population_growth_rate_ten_year_top10_html}
    {province_population_growth_rate_ten_year_last10_html}
    <h2 id="1.2. 1年增长率">1.2. 1年增长率</h2>
    {dto.common_city_df['population_one_year_growth_rate'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {city_population_growth_rate_one_year_top10_html}
    {city_population_growth_rate_one_year_last10_html}
    {dto.common_province_df['population_one_year_growth_rate'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {province_population_growth_rate_one_year_top10_html}
    {province_population_growth_rate_one_year_last10_html}
    <h2 id="1.3. 人口总量">1.3. 人口总量</h2>
    {dto.common_city_df['cur_population'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {city_population_top_list_html}
    {city_population_last_list_html}
    {dto.common_province_df['cur_population'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {province_population_top_list_html}
    {province_population_last_list_html}
    <h1 id="2. GDP（单位亿）">2. GDP（单位亿）</h1>
    <h2 id="2.1. 10年平均增长率">2.1. 10年平均增长率</h2>
    {dto.common_city_df['gdp_ten_year_growth_rate'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {city_gdp_ten_year_growth_rate_top10_html}
    {city_gdp_ten_year_growth_rate_last10_html}
    {dto.common_province_df['gdp_ten_year_growth_rate'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {province_gdp_ten_year_growth_rate_top10_html}
    {province_gdp_ten_year_growth_rate_last10_html}
    <h2 id="2.2. 1年增长率">2.2. 1年增长率</h2>
    {dto.common_city_df['gdp_one_year_growth_rate'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {city_gdp_one_year_growth_rate_top10_html}
    {city_gdp_one_year_growth_rate_last10_html}
    {dto.common_province_df['gdp_one_year_growth_rate'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {province_gdp_one_year_growth_rate_top10_html}
    {province_gdp_one_year_growth_rate_last10_html}
    <h2 id="2.3. GDP总量">2.3. GDP总量</h2>
    {dto.common_city_df['cur_gdp'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {city_gdp_top_list_html}
    {city_gdp_last_list_html}
    {dto.common_province_df['cur_gdp'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {province_gdp_top_list_html}
    {province_gdp_last_list_html}
    <h2 id="2.4. 人均GDP">2.4. 人均GDP</h2>
    {dto.common_city_df['cur_gdp_per_capita'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {city_gpc_top_list_html}
    {city_gpc_last_list_html}
    {dto.common_province_df['cur_gdp_per_capita'].describe().to_frame().rename(columns=_RENAME_DICT).style.to_html()}
    {province_gpc_top_list_html}
    {province_gpc_last_list_html}
    <h1 id="3. 重点关注的城市">3. 重点关注的城市</h1>
    {cared_area_html}
    <h1 id="4. HQ城市">4. HQ城市</h1>
    {high_quality_area_html}
    <h1 id="99. 失败的area">99. 失败的area</h1>
    {dto.err_area_list}
    '''
    toc = _gen_toc(content)
    final_html = f'''
    {style}
    <body>
    <aside>
    {toc}
    </aside>
    {content}
    </body>
    '''
    send_html_as_attachment(f'[EDOG]{cur_date.year}年经济总结报告', final_html)
    # print(final_html)
