from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session

DATABASE = "mysql+pymysql://root:root@localhost/garrent?charset=utf8"

engine = create_engine(DATABASE, encoding="utf-8", echo=False)
_Session = scoped_session(sessionmaker(bind=engine,autoflush=True))

# the query session create
database_session = _Session()
