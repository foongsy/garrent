# encoding:utf-8
import logging

from dateutil import parser

#from celery_app import celery as celery_app
from garrent.database import database_session
from garrent.models import (Stock,
                            CCASSDetails,
                            Shareholders,
                            CCASSsnapshot,
                            CCASSPlayer,
                            ShortSell,
                            Repurchase,
                            StockIPO,
                            CN_HK_Stock,
                            StockChange,
                            TopTen,
                            HkSnapshot)
from garrent import request
from garrent.utils import parse_int, is_NaN, convert_currency, convert_code, convert_float

logger = logging.getLogger(__name__)


#@celery_app.task(ignore_result=True)
def insert_ccass_stock_holding_and_snapshot(code, date):
    """
    :return:
    """
    snapshot_frame, stock_holding_frame = request.get_CCASS_stock_holding_and_snapshot(code, date)

    try:
        if snapshot_frame is not None and not snapshot_frame.empty:

            if not CCASSsnapshot.exist(code, date):

                snapshot_model = CCASSsnapshot()
                snapshot_model.code = code
                snapshot_model.date = date
                if "願意披露的投資者戶口持有人" in snapshot_frame.index:
                    named_investors = snapshot_frame["於中央結算系統的持股量"]["願意披露的投資者戶口持有人"]
                else:
                    named_investors = None
                if "不願意披露的投資者戶口持有人" in snapshot_frame.index:
                    unname_investors = snapshot_frame["於中央結算系統的持股量"]["不願意披露的投資者戶口持有人"]
                else:
                    unname_investors = None
                if "市場中介者" in snapshot_frame.index:
                    players_total = snapshot_frame["於中央結算系統的持股量"]["市場中介者"]  # Market Intermediaries
                else:
                    players_total = None
                if "總數" in snapshot_frame.index:

                    total_in_ccass = snapshot_frame["於中央結算系統的持股量"]["總數"]  # Shareholding in CCASS Total
                else:
                    total_in_ccass = None
                if "已發行股份/權證  (最近更新數目)" in snapshot_frame.index:
                    total_outstanding = snapshot_frame["於中央結算系統的持股量"]["已發行股份/權證  (最近更新數目)"]
                else:
                    total_outstanding = None

                # Total number of Issued Shares/Warrants (last updated figure)

                # players_total = Market Intermediaries,
                # named_investors = Consenting Investor Participants,
                # unnamed_investors = Non-consenting Investor Participants,
                # total_in_ccass = Total,
                # total_outstanding = Total number of Issued Shares/Warrants (last updated figure)

                snapshot_model.players_total = players_total
                snapshot_model.total_in_ccass = total_in_ccass
                snapshot_model.total_outstanding = total_outstanding
                snapshot_model.unnamed_investors = unname_investors
                snapshot_model.named_investors = named_investors

                database_session.add(snapshot_model)
                database_session.commit()

        stock_holding_list = []

        if stock_holding_frame is not None and not stock_holding_frame.empty:

            for index, row in stock_holding_frame.iterrows():
                if index != 0:
                    player_id = row[0]
                    player_name = row[1]
                    holding = row[3]

                    if not CCASSDetails.exist(code, date, player_id):
                        detail_model = CCASSDetails()
                        detail_model.date = date
                        detail_model.code = code
                        detail_model.holding = holding
                        detail_model.player_id = player_id
                        detail_model.player_name = player_name

                        stock_holding_list.append(detail_model)

            database_session.bulk_save_objects(stock_holding_list)
            database_session.commit()
    except Exception as e:
        logger.exception(e)


#@celery_app.task(ignore_result=True)
def insert_share_holding(code, start_date, end_date):
    """
    :return:
    """
    holding_frame = request.get_disclosure_interests(code, start_date, end_date)

    try:
        if holding_frame is not None and not holding_frame.empty:
            holding_list = []
            for index, row in holding_frame.iterrows():
                if index != 0:
                    shareholder = row[0].strip()
                    holding = parse_int(row[1])
                    last_reported = parser.parse(row[3]).date()

                    model = Shareholders()
                    model.code = code
                    model.last_reported = last_reported
                    model.shareholder = shareholder
                    model.holding = holding
                    model.date = end_date  # mark the date as end_date

                    holding_list.append(model)

            database_session.bulk_save_objects(holding_list)
            database_session.commit()
    except Exception as e:
        logger.exception(e)


#@celery_app.task(ignore_result=True)
def inster_stock_IPO_info(code):
    """
    :param code:
    :return:
    """
    ipo_summary = request.get_company_summary(code)

    if ipo_summary:

        price_range = ipo_summary["price_range"].split("-")
        price_range = list(map(float, price_range))
        if not StockIPO.exist(code):
            instance = StockIPO()
            instance.code = code
            instance.fix_price_date = ipo_summary["fixed_date"]
            instance.industry = ipo_summary["industry"]
            instance.website = ipo_summary["website"]
            instance.lot = ipo_summary["lot_size"]
            instance.sponsors = ipo_summary["sponsor"]
            instance.underwriters = ipo_summary["underwriters"]
            instance.result_date = ipo_summary["result_date"]
            instance.po_ratio = ipo_summary["po_percentage"]
            instance.po_size = ipo_summary["po_size"]
            instance.ipo_date = ipo_summary["ipo_date"]
            instance.open_date_during = [ipo_summary["application_date_start"], ipo_summary["aplication_date_end"]]
            instance.price_range = price_range
            database_session.add(instance)
            database_session.commit()

        else:
            StockIPO.update(code, **{
                "fix_price_date": ipo_summary["fixed_date"],
                "industry": ipo_summary["industry"],
                "website": ipo_summary["website"],
                "lot": ipo_summary["lot_size"],
                "sponsors": ipo_summary["sponsor"],
                "underwriters": ipo_summary["underwriters"],
                "result_date": ipo_summary["result_date"],
                "po_ratio": ipo_summary["po_percentage"],
                "po_size": ipo_summary["po_size"],
                "ipo_date": ipo_summary["ipo_date"],
                "open_date_during": [ipo_summary["application_date_start"], ipo_summary["aplication_date_end"]],
                "price_range": price_range
            })


""" daily tasks """


def handler_stock(data_frame, board="M"):
    """
    :param data_frame:
    :param board:
    :return:
    """
    stocks = []

    for index, row in data_frame.iterrows():
        if index != 0:
            code = row[0]
            name = row[1]
            lot = row[2]
            # shortable = 1 when remark has H
            # hasoptions = 1 when remark has O
            shortable = True if row[4] == "H" else False
            hasoptions = True if row[5] == "O" else False

            if not Stock.exist(code):
                model = Stock()
                model.code = code
                model.name = name
                model.lot = lot
                model.board = board
                model.hasoptions = hasoptions
                model.shortable = shortable
                model.active = True
                stocks.append(model)
    return stocks


#@celery_app.task(ignore_result=True)
def insert_stock():
    """
    insert stock info data
    :return:
    """
    main_board_frame = request.get_main_board_info()
    gem_board_frame = request.get_GEM_board_info()

    try:
        if main_board_frame is not None and not main_board_frame.empty:
            main_stocks = handler_stock(main_board_frame, "M")
            database_session.bulk_save_objects(main_stocks)
        if gem_board_frame is not None and not gem_board_frame.empty:
            gem_stocks = handler_stock(gem_board_frame, "G")
            database_session.bulk_save_objects(gem_stocks)

        database_session.commit()
    except Exception as e:
        logger.exception(e)


# daily
#@celery_app.task(ignore_result=True)
def insert_ccass_player():
    """
    :return:
    """
    CCASS_frame = request.get_CCASS_participant_list()

    if CCASS_frame is not None and not CCASS_frame.empty:
        try:
            ccass_list = []
            for index, row in CCASS_frame.iterrows():
                if index != 0:
                    ccass_id = row[0]  # ccass id
                    name = row[1]  # ccass name

                    model = CCASSPlayer()
                    if not is_NaN(ccass_id) and not CCASSPlayer.exist(ccass_id):
                        model.ccass_id = ccass_id
                        model.name = name
                    else:
                        model.name = name
                    ccass_list.append(model)

            database_session.bulk_save_objects(ccass_list)
            database_session.commit()
        except Exception as e:
            logger.exception(e)


# daily
#@celery_app.task(ignore_result=True)
def insert_repurchases_report(date):
    """
    :return:
    """
    report_frame = request.get_daily_repurchases_report(date)

    if report_frame is not None and not report_frame.empty:

        try:
            report_list = []

            for index, row in report_frame.iterrows():
                code = row[1]
                trade_date = parser.parse(row[3]).date()
                vol = row[4]
                price_per_share = convert_currency(row[5])
                lowest_px = convert_currency(row[6])

                total_paid = convert_currency(row[7])
                ytd_vol = row[9]
                percent_of_mandate = row[10]

                if not Repurchase.exist(code, trade_date):
                    model = Repurchase()
                    model.code = code
                    model.date = date
                    model.total_paid = total_paid
                    model.percent_of_mandate = percent_of_mandate
                    model.trading_date = trade_date
                    model.ytd_vol = ytd_vol
                    model.vol = vol
                    model.lowest_px = lowest_px
                    model.price_per_share = price_per_share

                    report_list.append(model)

            database_session.bulk_save_objects(report_list)
            database_session.commit()
        except Exception as e:
            logger.exception(e)


#@celery_app.task(ignore_result=True)
def insert_short_sell(date):
    """
    :return:
    """
    short_sell_frame = request.get_daily_short_sell(date)

    if short_sell_frame is not None and not short_sell_frame.empty:
        try:
            short_sell_list = []
            for index, row in short_sell_frame.iterrows():
                row_date = parser.parse(row["Date"])
                code = convert_code(row["Code"])
                short_vol = int(row["Short Vol.  (No. of Share)"])
                short_to = int(row["Short  Turnover  (HKD)"])
                vol = int(row["Total Vol.  (No. of Share)"])
                to = int(row["Total  Turnover  (HKD)"])

                if not ShortSell.exist(code, row_date):
                    model = ShortSell()
                    # short_vol = Total Short Selling Turnover (sh),
                    # short_to = Total Short Selling Turnover ($),
                    # vol = Total Turnover (SH),
                    # to = Total Turnover ($)
                    model.code = code
                    model.date = row_date
                    model.short_to = short_to
                    model.short_vol = short_vol
                    model.to = to
                    model.vol = vol

                    short_sell_list.append(model)

            database_session.bulk_save_objects(short_sell_list)
            database_session.commit()
        except Exception as e:
            logger.exception(e)


def insert_sz_hk_stock():
    """
    :return:
    """
    dataframe = request.get_sz_hk_stock()



    if dataframe is not None and not dataframe.empty:
        stock_list = []
        for index, row in dataframe.iterrows():
            code = row["港股代码"]
            cn_name = row["中文简称"]

            if not CN_HK_Stock.exist(code):
                instance = CN_HK_Stock()
                instance.code = code
                instance.cn_name = cn_name
                instance.market = "SZ"
                stock_list.append(instance)

        database_session.bulk_save_objects(stock_list)
        database_session.commit()


def insert_sz_hk_stock_change():
    """

    :return:
    """
    dataframe = request.get_sz_hk_change()

    if dataframe is not None and not dataframe.empty:
        stock_list = []
        for index, row in dataframe.iterrows():
            code = row["港股代码"]
            cn_name = row["中文简称"]

            change_date = parser.parse(row["调整生效日期"])
            change = "IN" if row["调整内容"] == "调入" else "OUT"

            if not StockChange.exist(code, change_date, change):
                instance = StockChange()
                instance.code = code
                instance.change_date = change_date
                instance.cn_name = cn_name
                instance.change = change
                instance.market = "SZ"
                stock_list.append(instance)

        database_session.bulk_save_objects(stock_list)
        database_session.commit()


# @celery_app.task(ignore_result=True)
def insert_sse_hk_stock():
    """
    :return:
    """
    sse_frame = request.get_sse_hk_stock()

    if sse_frame is not None and not sse_frame.empty:

        stock_list = []
        for index, row in sse_frame.iterrows():

            code = row["证券代码"]
            cn_name = row["中文简称"]

            if not CN_HK_Stock.exist(code):
                instance = CN_HK_Stock()
                instance.code = code
                instance.cn_name = cn_name
                instance.market = "SH"
                stock_list.append(instance)
        database_session.bulk_save_objects(stock_list)
        database_session.commit()


# @celery_app.task(ingore_result=True)
def insert_hk_stock_change():
    """
    :return:
    """
    change_frame = request.get_sse_hk_stock_change()

    if change_frame is not None and not change_frame.empty:
        stock_list = []
        for index, row in change_frame.iterrows():
            code = row["港股代码"]
            cn_name = row["中文简称"]

            change_date = parser.parse(row["生效日期"])

            change = "IN" if row["调整内容"] == "调入" else "OUT"

            if not StockChange.exist(code, change_date, change):
                instance = StockChange()
                instance.code = code
                instance.change_date = change_date
                instance.cn_name = cn_name
                instance.change = change
                instance.market = "SH"
                stock_list.append(instance)

        database_session.bulk_save_objects(stock_list)
        database_session.commit()


def _insert_top_10(dataframe, date, market):
    """

    :return:
    """
    if dataframe is not None and not dataframe.empty:

        stock_list = []
        for index, row in dataframe.iterrows():
            # ["Rank", "Stock Code", "Stock Name", "Buy Turnover", "Sell Turnover", "Total Turnover"]

            code = convert_code(row["Stock Code"])
            buy_turnover = row["Buy Turnover"]
            sell_turnover = row["Sell Turnover"]
            total_turnover = row["Total Turnover"]
            rank = row["Rank"]
            if not TopTen.exist(date, code, market):
                instance = TopTen()
                instance.code = code
                instance.date = date
                instance.rank = int(rank)
                instance.market = market
                instance.buy = int(buy_turnover.replace(",", ""))
                instance.sell = int(sell_turnover.replace(",", ""))
                instance.total = int(total_turnover.replace(",", ""))

                stock_list.append(instance)
        database_session.bulk_save_objects(stock_list)
        database_session.commit()


#@celery_app.task(ingore_result=True)
def insert_stock_top_10(date):
    """
    :param date:
    :return:
    """
    sse_frame, szse_frame = request.get_stock_top_10(date)

    _insert_top_10(sse_frame, date, "SH")
    _insert_top_10(szse_frame, date, "SZ")


def _insert_connect(dataframe, market):
    """
    :param dateframe:
    :return:
    """
    if dataframe is not None and not dataframe.empty:

        item_list = []
        for index, row in dataframe.iterrows():
            date = parser.parse(row["日期"]).date()

            total_buy = convert_currency(row["买入成交额(元)"])
            total_sell = convert_currency(row["卖出成交额(元)"])
            quota_left = convert_currency(row["当日余额(元)"])
            capital_inflow = convert_currency(row["当日资金流入(元)"])
            net_bid_flow = convert_currency(row["当日成交净买额(元)"])

            # quota_left_percent = Column(Float(precision=2))  # (佔額度)

            if not HkSnapshot.exist(date, market):
                instance = HkSnapshot()
                instance.total_buy = total_buy
                instance.total_sell = total_sell
                instance.quota_left = quota_left
                instance.date = date
                instance.market = market
                instance.capital_inflow = capital_inflow
                instance.net_bid_flow = net_bid_flow

                item_list.append(instance)

        database_session.bulk_save_objects(item_list)
        database_session.commit()


#@celery_app.task(ignore_result=True)
def insert_stock_connect():
    """
    :return:
    """
    sh_connect = request.get_sh_hk_connect()
    sz_connect = request.get_sz_hk_connect()

    _insert_connect(sh_connect, "SH")
    _insert_connect(sz_connect, "SZ")


#@celery_app.task(ignore_result=True)
def insert_list_IPO():
    """
    HK stock ipo data
    :return:
    """
    ipo_datafame = request.get_HK_IPO()

    if ipo_datafame is not None and not ipo_datafame.empty:
        ipo_list = []

        for index, row in ipo_datafame.iterrows():

            ipo_date = row["上市日期"]
            code = row["上市編號"]
            name = row["公司名稱"]
            industry = row["行業"]
            ipo_price = row["招股價"]
            sub_multiple = row["超額倍數"]

            mintoget = row["穩中一手"]
            mintoget_ratio = row["中籤率(%)"]

            if not StockIPO.exist(code):
                instance = StockIPO()
                instance.code = code
                instance.name = name
                instance.industry = industry
                instance.ipo_date = ipo_date

                if not is_NaN(ipo_price):
                    instance.ipo_price = ipo_price
                if not is_NaN(sub_multiple):
                    sub_multiple = convert_float(sub_multiple)
                    instance.sub_multiple = sub_multiple
                if not is_NaN(mintoget):
                    instance.mintoget = mintoget
                if not is_NaN(mintoget_ratio):
                    mintoget_ratio = mintoget_ratio.replace("%", "")
                    mintoget_ratio = float(mintoget_ratio)
                    instance.mintoget_ratio = mintoget_ratio

                ipo_list.append(instance)

        database_session.bulk_save_objects(ipo_list)
        database_session.commit()
