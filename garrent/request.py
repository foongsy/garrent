# encoding:utf-8
import datetime
import io
import logging
import os
import time
import re

import execjs
import pandas
import requests
from bs4 import BeautifulSoup
from dateutil import parser
from selenium import webdriver

from garrent.utils import convert_code, parse_int

os.environ["EXECJS_RUNTIME"] = "PhantomJS"

logger = logging.getLogger(__name__)


class RequestError(Exception):
    pass


def _parser_board_info(url: str):
    """
    :param url:
    :return:
    """
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "lxml")
        table = soup.find("table", class_="table_grey_border")

        board_data = pandas.read_html(table.prettify(), flavor="bs4")

        board_data = board_data[0]

        return board_data
    else:
        logger.error("request error url", url)


def get_main_board_info():
    """
    http://www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdeqty_c.htm
    :return:DataFrame
    """

    url = "http://www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdeqty_c.htm"
    board_data = _parser_board_info(url)
    return board_data


def get_GEM_board_info():
    """
    http://www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdgems_c.htm
    :return: DataFrame
    """
    url = "http://www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdgems_c.htm"

    board_data = _parser_board_info(url)
    return board_data


def get_daily_short_sell(date: datetime.date):
    """

    :param date:
    :return: DataFrame
    """
    if isinstance(date, str):
        date = parser.parse(date).date()

    date_format = date.strftime("%Y%m%d")
    url = ("http://www.analystz.hk/short/short-selling-ratio-ranking.php"
           "?d1={date}&d2={date}&stolim=0&ratio=0".format(date=date_format))

    response = requests.get(url)

    if response.status_code == 200:

        soup = BeautifulSoup(response.content, "lxml")
        div = soup.find(id="pageContent")

        table = div.findAll("table")
        sell_table = table[2]

        sell_data = pandas.read_html(sell_table.prettify(), header=0,
                                     converters={"Code": str, "Total  Turnover  (HKD)": int},
                                     skiprows=[1, 2], flavor="bs4")
        sell_data = sell_data[0]

        sell_data = sell_data[:-1]  # drop last row

        return sell_data

    elif response.status_code == 404:
        return None
    else:
        logger.error("request error :", url)


# def get_daily_short_sell(date: datetime.date, tag_name="short_selling"):
#     """
#     http://www.hkex.com.hk/eng/stat/smstat/dayquot/qtn.asp
#
#
#     http://www.hkex.com.hk/chi/stat/smstat/dayquot/d170202c.htm
#
#     http://sc.hkex.com.hk/gb/www.hkex.com.hk/chi/stat/smstat/dayquot/d170103c.htm#short_selling
#     :return:
#     """
#     date_format = date.strftime("%y%m%d")
#     url = "http://www.hkex.com.hk/chi/stat/smstat/dayquot/d{date}c.htm".format(date=date_format)
#
#     response = requests.get(url)
#
#     if response.status_code == 200:
#
#         soup = BeautifulSoup(response.content, "lxml")
#
#         tag_data = soup.find("a", attrs={"name": tag_name})
#         print(tag_data.content)
#         print(tag_data.find_next_sibling())
#         print(tag_data.find_next())
#
#         print(dir(tag_data))
#
#     elif response.status_code == 404:
#         return None
#     else:
#         raise RequestError("request url error", url)


def get_CCASS_participant_list():
    """
    http://www.hkexnews.hk/sdw/search/partlist_c.aspx?SortBy=PartID&ShareholdingDate=20170202
    :return: DataFrame
    """
    url = "http://www.hkexnews.hk/sdw/search/partlist_c.aspx?SortBy=PartID"

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "lxml")
        table = soup.find("table")
        table_data = pandas.read_html(table.prettify(), skiprows=[0], flavor="bs4", na_values=None)
        return table_data[0]
    elif response.status_code == 404:
        return None
    else:
        logger.info("request error", url)


def get_CCASS_stock_holding_and_snapshot(code, date):
    """

    http://www.hkexnews.hk/sdw/search/searchsdw_c.aspx
    find the CCASS data and the CCASS snapshot
    :param code:
    :param date:
    :return: dataframe(ccass snapshot), dataframe(holding data), or None, None
    """

    if isinstance(date, str):
        date = parser.parse(date).date()

    url = "http://www.hkexnews.hk/sdw/search/searchsdw_c.aspx"
    response = requests.get(url)

    if response.status_code == 200:
        form_soup = BeautifulSoup(response.content, "lxml")

        view_state = form_soup.find(id="__VIEWSTATE")["value"]
        view_stage_generator = form_soup.find(id="__VIEWSTATEGENERATOR")["value"]
        event_validation = form_soup.find(id="__EVENTVALIDATION")["value"]

        today = datetime.date.today()
        headers = {"Host": "www.hkexnews.hk",
                   "Origin": "http://www.hkexnews.hk",
                   "Referer": url}

        data = {"today": today.strftime("%Y%m%d"),
                "__VIEWSTATE": view_state,
                "__VIEWSTATEGENERATOR": view_stage_generator,
                "__EVENTVALIDATION": event_validation,
                "txtStockCode": code,
                "ddlShareholdingDay": date.strftime("%d"),
                "ddlShareholdingMonth": date.strftime("%m"),
                "ddlShareholdingYear": date.strftime("%Y"),
                "btnSearch.x": "24",
                "btnSearch.y": "11"}

        stock_request = requests.post(url, headers=headers, data=data)
        if stock_request.status_code == 200:
            soup = BeautifulSoup(stock_request.content, "lxml")
            holding_table = soup.find("table", id="participantShareholdingList")

            snapshot = soup.find(id="pnlResultSummary")

            snapshot_table = snapshot.find("table")

            if snapshot_table:
                snapshot_data = pandas.read_html(snapshot_table.prettify(), header=0, index_col=0,
                                                 converters={"於中央結算系統的持股量": int, "參與者數目": int}, flavor="bs4")
                snapshot_data = snapshot_data[0]
            else:
                snapshot_data = None

            if holding_table:
                holding_data = pandas.read_html(holding_table.prettify(), flavor="bs4", keep_default_na=True)
                holding_data = holding_data[0].dropna()
            else:
                holding_data = None
            return snapshot_data, holding_data
        elif stock_request.status_code == 404:
            return None, None
        else:
            logger.error("request error", url, "post data=>", data)
    else:
        logger.error("request error", url)


def get_daily_repurchases_report(date: datetime.date):
    """
    :param date:
    :return: pandas.Dataframe or None
    """
    if isinstance(date, str):
        date = parser.parse(date).date()
    date_format = date.strftime("%Y%m%d")
    url = "http://www.hkexnews.hk/reports/sharerepur/documents/SRRPT{date}.xls".format(date=date_format)

    response = requests.get(url)
    if response.status_code == 200:
        excel_data = io.BytesIO(response.content)
        # try to escape row in the col
        data_frame = pandas.read_excel(excel_data, header=1, skiprows=[1, 3, 4], thousands=',', keep_default_na=True)

        data_frame[[data_frame.columns[1]]] = data_frame[[data_frame.columns[1]]].astype(str)  # convert stock code

        data_frame = data_frame.dropna()

        for index, row in data_frame.iterrows():
            code = row[1]  # stock code
            code = str(int(float(code)))
            new_code = convert_code(code)
            #  Stock code
            data_frame.set_value(index, data_frame.columns[1], new_code)

        data_frame = data_frame.replace(["-"], [None])

        return data_frame
    elif response.status_code == 404:
        return None
    else:
        logger.error("request error", url)


def get_disclosure_interests(code, start_date: datetime.date, end_date: datetime.date):
    """
    http://sdinotice.hkex.com.hk/di/NSSrchCorp.aspx?src=MAIN&lang=ZH&in=1&
    :param code:
    :param start_date: datetime.date
    :param end_date: datetime.date
    :return: DataFrame or None
    """

    if isinstance(start_date, str):
        start_date = parser.parse(start_date).date()
    if isinstance(end_date, str):
        end_date = parser.parse(end_date).date()

    base_link = "http://sdinotice.hkex.com.hk/di/"
    url = ("http://sdinotice.hkex.com.hk/di/NSSrchCorpList.aspx?"
           "sa1=cl&"
           "scsd={start_date}&"
           "sced={end_date}&"
           "sc={code}&src=MAIN&lang=ZH").format(start_date=start_date.strftime("%d/%m/%Y"),
                                                end_date=end_date.strftime("%d/%m/%Y"),
                                                code=code)
    response = requests.get(url)
    if response.status_code == 200:
        search_soup = BeautifulSoup(response.content, "lxml")
        print(response.content)
        table = search_soup.find(id="grdPaging")
        if table:
            tag_a = table.find("a", text="大股東名單")
            if tag_a:
                link = base_link + tag_a["href"]
                disclosure_response = requests.get(link)
                if disclosure_response.status_code == 200:
                    soup = BeautifulSoup(disclosure_response.content, "lxml")
                    disclosure_table = soup.find("table", id="grdPaging")
                    disclosure_data = pandas.read_html(disclosure_table.prettify(), flavor="bs4")
                    disclosure_data = disclosure_data[0]
                    return disclosure_data
                else:
                    logger.error("request error", link)

    elif response.status_code == 404:
        return None
    else:
        logger.error("request error", url)


def _parser_connect(url, format_url, ):
    """
    :return:
    """
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "lxml")
        page = soup.find("span", class_="page_info")
        num = page.text
        total = int(num.split("/")[1])

        data_list = []

        for i in range(1, total + 1):
            page_response = requests.get(format_url.format(i))
            if page_response.status_code == 200:
                soup = BeautifulSoup(page_response.content, "lxml")
                table = soup.find("table")
                table_frame = pandas.read_html(table.prettify(), flavor="bs4")
                table_frame = table_frame[0]

                table_frame.columns = table_frame.columns.str.replace("\n", "")
                table_frame.columns = table_frame.columns.str.strip()
                table_frame.columns = table_frame.columns.str.replace(" ", "")

                data_list.append(table_frame)

        return pandas.concat(data_list, ignore_index=True)


def get_sh_hk_connect():
    """
    http://www.aastocks.com/tc/cnhk/market/quota-balance/sh-hk-connect

    http://data.10jqka.com.cn/hgt/ggtb/board/getGgtPage/page/1
    :return: pandas.Dataframe
    """
    url = "http://data.10jqka.com.cn/hgt/ggtb/board/getGgtPage/page/1"
    format_url = "http://data.10jqka.com.cn/hgt/ggtb/board/getGgtPage/page/{0}"

    return _parser_connect(url, format_url)


def get_sz_hk_connect():
    """
    http://data.10jqka.com.cn/hgt/ggtb/board/getGgtPage/page/1
    :return:
    """
    url = "http://data.10jqka.com.cn/hgt/ggtbs/board/getGgtsPage/page/1"
    format_url = "http://data.10jqka.com.cn/hgt/ggtbs/board/getGgtsPage/page/{0}"
    return _parser_connect(url, format_url)


def _parser_top_10(items):
    """
    :param items:
    :return:
    """
    for inner in items:
        if inner["style"] == 2:
            table = inner["table"]
            columns = table["schema"][0]
            rows = []
            for value in table["tr"]:
                rows.append(value["td"][0])
            data_frame = pandas.DataFrame(rows, columns=columns)

            return data_frame


def get_stock_top_10(date: datetime.date):
    """
    http://www.hkex.com.hk/chi/csm/chinaconndstat_daily.htm

    url ="http://www.hkex.com.hk/chi/csm/DailyStat/data_tab_daily_20170217c.js"

    ["Rank", "Stock Code", "Stock Name", "Buy Turnover", "Sell Turnover", "Total Turnover"]

    :return:
    """
    if isinstance(date, str):
        date = parser.parse(date).date()

    url = "http://www.hkex.com.hk/chi/csm/DailyStat/data_tab_daily_{date}c.js".format(date=date.strftime("%Y%m%d"))

    response = requests.get(url)
    if response.status_code == 200:
        content = response.content.decode("utf-8")
        stock_data = execjs.eval(content)  # js compile

        sse_hk, szse_hk = None, None
        for item in stock_data:
            if item["market"] == "SSE Southbound":  # 港股通（滬）
                sse_hk = _parser_top_10(item["content"])
            elif item["market"] == "SZSE Southbound":  # 港股通（深)
                szse_hk = _parser_top_10(item["content"])
        return sse_hk, szse_hk


def get_sse_hk_stock():
    """
    港股通股票名单
    :return: dataframe
    """
    driver = webdriver.PhantomJS()
    url = "http://www.sse.com.cn/services/hkexsc/disclo/eligible/"
    driver.get(url)

    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "lxml")
    table = soup.find("table")
    data_frame = pandas.read_html(table.prettify(), header=0, converters={"证券代码": str}, flavor="bs4",
                                  na_values=" ", keep_default_na=False)

    return data_frame[0]


def get_sse_hk_stock_change():
    """
    港股通股票调整信息
    http://www.sse.com.cn/services/hkexsc/disclo/eligiblead/
    :return: dataframe
    """
    url = "http://www.sse.com.cn/services/hkexsc/disclo/eligiblead/"
    driver = webdriver.PhantomJS()

    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "lxml")
    table = soup.find("table")
    data_frame = pandas.read_html(table.prettify(), header=0, converters={"港股代码": str}, flavor="bs4")
    return data_frame[0]


def get_HK_IPO():
    """
    新股頻道 IPO - 半新股資訊
    http://www.aastocks.com/tc/ipo/ListedIPO.aspx?iid=ALL&orderby=DA&value=DESC&index=3
    :return:
    """
    url = "http://www.aastocks.com/tc/ipo/ListedIPO.aspx?iid=ALL&orderby=DA&value=DESC"
    response = requests.get(url)
    if response.status_code == 200:
        content = response.content
        soup = BeautifulSoup(content, "lxml")
        page = soup.find(id="paging")

        num_text = page.find(attrs={"style": "float:left"})

        num = re.findall(r"共(\d+)頁", num_text.text)[0]

        num = int(num)

        data_list = []

        for i in range(1, num + 1):
            request_url = "http://www.aastocks.com/tc/ipo/ListedIPO.aspx?iid=ALL&orderby=DA&value=DESC&index={0}".format(
                i)

            page_response = requests.get(request_url)
            if page_response.status_code == 200:
                inner_soup = BeautifulSoup(page_response.content, "lxml")

                table = inner_soup.find("table", class_="newIPOTable")

                dataframe = pandas.read_html(table.prettify(), header=0, flavor="bs4", skiprows=[0, 2],
                                             converters={"上市編號": str})

                dataframe = dataframe[0]

                data_list.append(dataframe)

        result_frame = pandas.concat(data_list, ignore_index=True)

        return result_frame


def get_compay_summary(code):
    """
    http://www.aastocks.com/tc/ipo/companysummary.aspx?symbol=02293&view=1
    :param code:
    :return:
    """
    url = "http://www.aastocks.com/tc/ipo/companysummary.aspx?symbol={code}&view=1".format(code=code)

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "lxml")

        table = soup.find(id="ctl00_ctl00_cphContent_cphContent_divContent")

        application_date_td = table.find("td", text=re.compile(r"招股日期"))
        application_date = application_date_td.findNext().text.strip()

        if "N/A" not in application_date:

            application_date_start = application_date.split("-")[0]
            application_date_end = application_date.split("-")[1]
            application_date_start = parser.parse(application_date_start)
            application_date_end = parser.parse(application_date_end)
        else:
            application_date_start = None
            application_date_end = None

        fixed_date_td = table.find("td", text=re.compile(r"定價日期"))
        fixed_date = fixed_date_td.findNext().text.strip()

        if "N/A" not in fixed_date:
            fixed_date = parser.parse(fixed_date)
        else:
            fixed_date = None

        result_date_td = table.find("td", text=re.compile(r"公佈售股結果日期"))
        result_date = result_date_td.findNext().text.strip()

        if "N/A" not in result_date:

            result_date = parser.parse(result_date)
        else:
            result_date = None

        ipo_date_td = table.find("td", text=re.compile(r"上市日期"))
        ipo_date = ipo_date_td.findNext().text.strip()

        if "N/A" not in ipo_date:
            ipo_date = parser.parse(ipo_date)
        else:
            ipo_date = None

        industry_td = table.find("td", text=re.compile(r"行業"))
        industry = industry_td.findNext().text.strip()

        if "N/A" in industry:
            industry = None

        website_td = table.find("td", text=re.compile(r"網址"))
        website = website_td.findNext().text.strip()

        if "N/A" in website:
            website = None

        lot_size_td = table.find("td", text=re.compile(r"每手股數"))
        lot_size = lot_size_td.findNext().text.strip()

        if "N/A" in lot_size:
            lot_size = None
        else:
            lot_size = int(lot_size)

        price_range_td = table.find("td", text=re.compile(r"招股價"))
        price_range  = price_range_td.findNext().text.strip()

        if "N/A" in price_range:
            ipo_price = None

        def sear_shares(tag):
            return tag.name == "td" and "香港配售股份數目" in tag.text

        hk_shares_td = table.find(sear_shares, class_="defaulttitle")
        hk_shares = hk_shares_td.findNextSibling().text.strip()

        if "N/A" not in hk_shares:
            po_size, po_percentage = hk_shares.split()
            po_size = parse_int(po_size)
            po_percentage = re.match(r"\((.*)%\)", po_percentage).group(1)
            po_percentage = float(po_percentage)
        else:
            po_size = None
            po_percentage = None

        sponsor_td = table.find("td", text=re.compile(r"保薦人"))
        sponsor = sponsor_td.findNext().text.replace("(相關往績)", "").strip()

        if "N/A" in sponsor:
            sponsor = None

        underwriters_td = table.find("td", text=re.compile(r"包銷商"))
        underwriters = underwriters_td.findNext().text.strip()

        if "N/A" in underwriters:
            underwriters = None

        return {
            "code": code,
            "application_date_start": application_date_start,
            "aplication_date_end": application_date_end,
            "fixed_date": fixed_date,
            "result_date": result_date,
            "ipo_date": ipo_date,
            "industry": industry,
            "website": website,
            "lot_size": lot_size,
            "price_range": price_range,
            "po_size": po_size,
            "po_percentage": po_percentage,
            "sponsor": sponsor,
            "underwriters": underwriters
        }

def get_sz_hk_stock():
    """
    港股通标的证券名单
    http://www.szse.cn/main/szhk/ggtywxx/bdzqmd/
    :return:
    """
    url = ("http://www.szse.cn/szseWeb/ShowReport.szse?"
           "SHOWTYPE=xlsx&CATALOGID=SGT_GGTBDQD&tab1PAGENUM=1&ENCODE=1&TABKEY=tab1")

    data_frame =  pandas.read_excel(url,converters={"港股代码":str})
    return data_frame

def get_sz_hk_change():
    """
    深港通名單變動
    http://www.szse.cn/main/szhk/ggtywxx/bdzqtz/
    :return:
    """
    url = ("http://www.szse.cn/szseWeb/ShowReport.szse?"
           "SHOWTYPE=xlsx&CATALOGID=SGT_GGTBDTZ&tab1PAGENUM=1&ENCODE=1&TABKEY=tab1")

    data_frame = pandas.read_excel(url,converters={"港股代码":str})

    return data_frame

