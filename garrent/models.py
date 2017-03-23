from sqlalchemy.ext.declarative import declarative_base
from datetime import date as py_date
from datetime import datetime
from sqlalchemy import (Column, Integer,
                        String, Boolean,
                        Enum, BigInteger,
                        DateTime, Date,
                        Float, UniqueConstraint,
                        SmallInteger, NVARCHAR)
from sqlalchemy.sql import exists, and_
from sqlalchemy.sql.expression import true
from sqlalchemy_utils import NumericRangeType, DateRangeType

from garrent.database import database_session

Base = declarative_base()

class BaseMixin(object):
    """
    """
    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, index=True)

class BaseMixin2(object):
    """
    """
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)

class Stock(Base):
    """

    -- shortable = 1 when remark has H
    -- hasoptions = 1 when remark has O

    """
    __tablename__ = "stock"
    id = Column(Integer, primary_key=True)
    code = Column(String(10), index=True, unique=True)
    name = Column(String(200))
    enname = Column(String(200))
    lot = Column(Integer)
    shortable = Column(Boolean)
    hasoptions = Column(Boolean)
    board = Column(Enum("M", "G"))
    active = Column(Boolean)
    last_updated = Column(DateTime, default=datetime.now)

    @classmethod
    def exist(cls, code):
        """
        :param code:
        :return: bool
        """
        return database_session.query(exists().where(cls.code == code)).scalar()

    @classmethod
    def query(cls, code):
        """
        query the stock by code
        :param code: str
        :return: class instance
        """
        result = database_session.query(cls).filter(cls.code == code).filter(cls.active == true()).one()
        return result

    @classmethod
    def update_active(cls, code, active):
        """
        :param code: str
        :param active: bool
        :return: None
        """
        database_session.query(cls).filter(cls.code == code).update({cls.active: active})
        database_session.commit()

    @classmethod
    def all(cls):
        """
        :return: list
        """
        result = database_session.query(cls.code).all()
        return result


class Shareholders(Base, BaseMixin):
    """
    """
    __tablename__ = "shareholders"

    date = Column(Date)  # end_date
    shareholder = Column(String(200))
    holding = Column(BigInteger)  # 796,529,786(L)
    last_reported = Column(Date)


class ShortSell(Base, BaseMixin):
    """
    short_vol = Total Short Selling Turnover (sh),
    short_to = Total Short Selling Turnover ($),
    vol = Total Turnover (SH),
    to = Total Turnover ($)

    """
    __tablename__ = "shortsell"
    short_vol = Column(BigInteger)
    short_to = Column(BigInteger)
    vol = Column(BigInteger)
    to = Column(BigInteger)
    date = Column(Date)

    # set unique with
    __table_args__ = (UniqueConstraint("code", "date", name="_code_date"),)

    @classmethod
    def exist(cls, code, date):
        """
        :param code: stock code
        :param date: datetime date
        :return: bool
        """
        return database_session.query(exists().where(and_(cls.code == code,
                                                          cls.date == date))).scalar()


class CCASSPlayer(Base):
    """
    """
    __tablename__ = "ccass_player"
    id = Column(Integer, primary_key=True)
    ccass_id = Column(String(20))
    name = Column(String(200))
    enname = Column(String(200))
    last_updated = Column(DateTime, default=datetime.now)

    @classmethod
    def exist(cls, ccass_id):
        """
        :param ccass_id:
        :return: bool
        """
        return database_session.query(exists().where(cls.ccass_id == ccass_id)).scalar()


class CCASSsnapshot(Base, BaseMixin):
    """
    code = stock code,
    date = data date,
    players_total = Market Intermediaries,
    named_investors = Consenting Investor Participants,
    unnamed_investors = Non-consenting Investor Participants,
    total_in_ccass = Total,
    total_outstanding = Total number of Issued Shares/Warrants (last updated figure)

    """
    __tablename__ = "ccass_snapshot"
    date = Column(Date)
    players_total = Column(BigInteger)
    named_investors = Column(BigInteger)
    unnamed_investors = Column(BigInteger)
    total_in_ccass = Column(BigInteger)
    total_outstanding = Column(BigInteger)

    # set unique with
    __table_args__ = (UniqueConstraint("code", "date", name="_code_date"),)

    @classmethod
    def exist(cls, code, date):
        """
        :param code:
        :param date:
        :return: bool
        """
        return database_session.query(exists().where(and_(cls.code == code, cls.date == date))).scalar()


class CCASSDetails(Base, BaseMixin):
    """
    """
    __tablename__ = "ccass_details"
    date = Column(Date)
    player_id = Column(String(20))

    player_name = Column(String(200))
    holding = Column(BigInteger)

    # set unique with
    __table_args__ = (UniqueConstraint("code", "date", "player_id", name="_code_date_player_id"),)

    @classmethod
    def exist(cls, code, date, player_id):
        """
        :param code:
        :param date:
        :param player_id:
        :return: bool
        """
        return database_session.query(
            exists().where(and_(cls.code == code, cls.date == date, cls.player_id == player_id))).scalar()


class Repurchase(Base, BaseMixin):
    """

    code = stock code,
    date = data date,
    trading_date = Trading Date,
    vol = Number of securities purchased
    lowest_px = Lowest price paid ($),
    total_paid = Total paid
    ytd_vol = Number of such securities purchased on the Exchange in the year to date (since ordinary resolution)
    percent_of_mandate = % of number of shares in issue at time ordinary resolution passed acquired on the Exchange since date of resolution

    price_per_share= "Price per share or highest price paid($)"

    this table is updated daily, just insert new records and leave the existing alone

    """
    __tablename__ = "repurchase"
    date = Column(Date)
    trading_date = Column(Date)
    vol = Column(BigInteger)
    lowest_px = Column(Float(precision=2))
    total_paid = Column(Float(precision=2))
    ytd_vol = Column(BigInteger)
    percent_of_mandate = Column(Float(precision=3))

    price_per_share = Column(Float(precision=2))

    # set unique with
    __table_args__ = (UniqueConstraint("code", "date", "trading_date", name="_code_dates"),)

    @classmethod
    def exist(cls, code, date, trade_date):
        """
        :param code:
        :param trade_date:
        :return: bool
        """
        return database_session.query(exists().where(and_(cls.code == code,
                                                          cls.date == date,
                                                          cls.trading_date == trade_date))).scalar()


class StockIPO(Base, BaseMixin):
    """
    ipo_date: 上市日期
    code: 上市編號
    name: 公司名稱
    industry: 行業
    ipo_price: 招股價
    sub_multiple: 超額倍數
    mintoget: 穩中一手
    mintoget_ratio: 中籤率(%)
    open_date: 招股日期
    fix_price_date: 定價日期
    result_date: 公佈售股結果日期
    website: 網址
    lot: 每手股數
    price_range (seperated by hyphen): 招股價(範圍)
    po_size: 香港配售股份數目
    po_ratio: 香港配售股份數目(%)
    sponsors (seperated by commas): 保薦人 (strip "(相關往績)")
    underwriters (seperated by commas): 包銷商

    """

    __tablename__ = "stock_ipo"
    code = Column(String(10), nullable=False, unique=True, index=True)
    ipo_date = Column(Date)
    open_date_during = Column(DateRangeType)
    fix_price_date = Column(Date)
    result_date = Column(Date)
    company_name = Column(String(100))
    industry = Column(String(100))
    ipo_price = Column(Float(precision=4))
    sub_multiple = Column(Float(precision=1))
    mintoget = Column(Integer)
    mintoget_ratio = Column(Float(precision=2))  # %

    website = Column(String(200))
    lot = Column(Integer)
    price_range = Column(NumericRangeType)
    po_size = Column(BigInteger)

    po_ratio = Column(Float(precision=2))  # %
    sponsors = Column(String(200))
    underwriters = Column(String(200))

    @classmethod
    def exist(cls, code):
        """
        :param code:
        :return:
        """
        return database_session.query(exists().where(cls.code == code)).scalar()

    @classmethod
    def update(cls, code, **kwargs):
        database_session.query(cls).filter(cls.code == code).update(kwargs)
        database_session.commit()


class HkSnapshot(Base, BaseMixin2):
    """
    即沪股通是130亿元人民币，港股通是105亿元人民币
    """
    __tablename__ = "hk_snapshot"

    total_buy = Column(Float(precision=2))  # 買入成交額(RMB） 億
    total_sell = Column(Float(precision=2))  # 賣出成交額(RMB)  億
    quota_left = Column(Float(precision=2))  # 剩餘額度(RMB)  億
    capital_inflow = Column(Float(precision=2))  # 當日資金流入(元) 億
    net_bid_flow = Column(Float(precision=2))  # 當日成交凈買入額(元) 億
    quota_left_percent = Column(Float(precision=2))  # (佔額度)
    market = Column(Enum("SH", "SZ"))

    __table_args__ = (UniqueConstraint("date", "market", name="_date_market"),)

    @classmethod
    def exist(cls, date, market):
        """
        :param date:
        :param market:
        :return:
        """
        return database_session.query(exists().where(and_(cls.market == market, cls.date == date))).scalar()


class TopTen(Base, BaseMixin2):
    """
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `date` DATE NULL,
  `rank` SMALLINT UNSIGNED NULL,
  `code` VARCHAR(45) NULL,
  `name` VARCHAR(45) NULL,
  `buy` INT UNSIGNED NULL,
  `sell` INT UNSIGNED NULL,
    """
    __tablename__ = "hk_topten"

    rank = Column(SmallInteger)
    code = Column(String(20))
    name = Column(NVARCHAR(100))
    buy = Column(BigInteger)  # 買入金額(HKD)
    sell = Column(BigInteger)  # 賣出金額(HKD)
    market = Column(Enum("SH", "SZ"))  # Shanghai, Shenzhen
    total = Column(BigInteger)  # HKD

    __table_args__ = (UniqueConstraint("date", "code", "market", name="_date_code_market"),)

    @classmethod
    def exist(cls, date, code, market):
        """
        :param date:
        :param code:
        :return:
        """
        return database_session.query(exists().where(and_(cls.code == code,
                                                          cls.date == date,
                                                          cls.market == market))).scalar()



class StockChange(Base, BaseMixin2):
    """
    # `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    #   `date` DATE NULL,
    #   `code` VARCHAR(45) NULL,
    #   `change` ENUM('IN','OUT') NULL,
    #   `change_date` DATE NULL,

    """
    __tablename__ = "sb_stockchange"
    code = Column(String(20))
    cn_name = Column(NVARCHAR(50))
    change = Column(Enum("IN", "OUT"))
    change_date = Column(Date)
    date = Column(Date, default=py_date.today)
    market = Column(Enum("SH", "SZ"))

    __table_args__ = (UniqueConstraint("change_date", "code", "change", name="_change_date_code_change"),)

    @classmethod
    def exist(cls, code, change_date, change):
        """
        """
        return database_session.query(exists().where(and_(cls.code == code,
                                                          cls.change_date == change_date,
                                                          cls.change == change))).scalar()


class CN_HK_Stock(Base, BaseMixin2):
    """
    """
    __tablename__ = "sb_stock"
    code = Column(String(20))
    cn_name = Column(NVARCHAR(50))
    date = Column(Date, default=py_date.today)
    market = Column(Enum("SH", "SZ"))
    @classmethod
    def exist(cls, code, market):
        """
        :param code:
        :return:
        """
        return database_session.query(exists().where(and_(cls.code == code, cls.market == market))).scalar()

class SBHolding(Base):
    __tablename__ = "sb_holding"
    id = Column(Integer, primary_key=True)
    code =Column(String(20))
    date = Column(Date, default=py_date.today)
    holding = Column(BigInteger)
    percent = Column(Float)
    changes = Column(BigInteger)
    @classmethod
    def exist(date, code):
        return database_session.query(exists()).where(and_(cls.code == code, cls.date == date)).scalar()
