from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
import pymysql

DATABASE = "mysql+pymysql://root:root@localhost/garrent?charset=utf8"

engine = create_engine(DATABASE, encoding="utf-8", echo=False)
_Session = scoped_session(sessionmaker(bind=engine,autoflush=True))

# the query session create
database_session = _Session()

def pymysql_conn():
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='root',
                           db='garrent',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    return(conn)
