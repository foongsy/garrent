from peewee import *

database = MySQLDatabase('garrent', **{'user': 'root', 'password': 'root'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class CcassDetails(BaseModel):
    code = CharField(index=True)
    date = DateField(null=True)
    holding = BigIntegerField(null=True)
    player = CharField(db_column='player_id', null=True)
    player_name = CharField(null=True)

    class Meta:
        db_table = 'ccass_details'
        indexes = (
            (('code', 'date', 'player'), True),
        )

class CcassPlayer(BaseModel):
    ccass = CharField(db_column='ccass_id', null=True)
    enname = CharField(null=True)
    last_updated = DateTimeField(null=True)
    name = CharField(null=True)

    class Meta:
        db_table = 'ccass_player'

class CcassSnapshot(BaseModel):
    code = CharField(index=True)
    date = DateField(null=True)
    named_investors = BigIntegerField(null=True)
    players_total = BigIntegerField(null=True)
    total_in_ccass = BigIntegerField(null=True)
    total_outstanding = BigIntegerField(null=True)
    unnamed_investors = BigIntegerField(null=True)

    class Meta:
        db_table = 'ccass_snapshot'
        indexes = (
            (('code', 'date'), True),
        )

class HkSnapshot(BaseModel):
    capital_inflow = FloatField(null=True)
    date = DateField()
    market = CharField(null=True)
    net_bid_flow = FloatField(null=True)
    quota_left = FloatField(null=True)
    quota_left_percent = FloatField(null=True)
    total_buy = FloatField(null=True)
    total_sell = FloatField(null=True)

    class Meta:
        db_table = 'hk_snapshot'
        indexes = (
            (('date', 'market'), True),
        )

class HkTopten(BaseModel):
    buy = BigIntegerField(null=True)
    code = CharField(null=True)
    date = DateField()
    market = CharField(null=True)
    name = CharField(null=True)
    rank = IntegerField(null=True)
    sell = BigIntegerField(null=True)
    total = BigIntegerField(null=True)

    class Meta:
        db_table = 'hk_topten'
        indexes = (
            (('date', 'code'), True),
        )

class Repurchase(BaseModel):
    code = CharField(index=True)
    date = DateField(null=True)
    lowest_px = FloatField(null=True)
    percent_of_mandate = FloatField(null=True)
    price_per_share = FloatField(null=True)
    total_paid = FloatField(null=True)
    trading_date = DateField(null=True)
    vol = BigIntegerField(null=True)
    ytd_vol = BigIntegerField(null=True)

    class Meta:
        db_table = 'repurchase'
        indexes = (
            (('code', 'trading_date'), True),
        )

class SbStock(BaseModel):
    cn_name = CharField(null=True)
    code = CharField(null=True, unique=True)
    date = DateField(null=True)

    class Meta:
        db_table = 'sb_stock'

class SbStockchange(BaseModel):
    change = CharField(null=True)
    change_date = DateField(null=True)
    cn_name = CharField(null=True)
    code = CharField(null=True)
    date = DateField(null=True)

    class Meta:
        db_table = 'sb_stockchange'
        indexes = (
            (('change_date', 'code', 'change'), True),
        )

class Shareholders(BaseModel):
    code = CharField(index=True)
    date = DateField(null=True)
    holding = BigIntegerField(null=True)
    last_reported = DateField(null=True)
    shareholder = CharField(null=True)

    class Meta:
        db_table = 'shareholders'

class Shortsell(BaseModel):
    code = CharField(index=True)
    date = DateField(null=True)
    short_to = BigIntegerField(null=True)
    short_vol = BigIntegerField(null=True)
    to = BigIntegerField(null=True)
    vol = BigIntegerField(null=True)

    class Meta:
        db_table = 'shortsell'
        indexes = (
            (('code', 'date'), True),
        )

class Stock(BaseModel):
    active = IntegerField(null=True)
    board = CharField(null=True)
    code = CharField(null=True, unique=True)
    enname = CharField(null=True)
    hasoptions = IntegerField(null=True)
    last_updated = DateTimeField(null=True)
    lot = IntegerField(null=True)
    name = CharField(null=True)
    shortable = IntegerField(null=True)

    class Meta:
        db_table = 'stock'

class StockIpo(BaseModel):
    code = CharField(unique=True)
    company_name = CharField(null=True)
    fix_price_date = DateField(null=True)
    industry = CharField(null=True)
    ipo_date = DateField(null=True)
    ipo_price = FloatField(null=True)
    lot = IntegerField(null=True)
    mintoget = IntegerField(null=True)
    mintoget_ratio = FloatField(null=True)
    open_date_during = CharField(null=True)
    po_ratio = FloatField(null=True)
    po_size = BigIntegerField(null=True)
    price_range = CharField(null=True)
    result_date = DateField(null=True)
    sponsors = CharField(null=True)
    sub_multiple = FloatField(null=True)
    underwriters = CharField(null=True)
    website = CharField(null=True)

    class Meta:
        db_table = 'stock_ipo'

