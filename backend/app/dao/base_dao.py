from sqlalchemy import create_engine
from app.config import globalAppSettings
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import  Optional
from .models import Base
from .models.trigger import create_trigger

Session: Optional[sessionmaker] = None

def init_db() -> None:
    global Session
    if Session is None:
        # 创建引擎
        engine = create_engine(
            globalAppSettings.db_dsn,
            echo=globalAppSettings.db_echo_sql,  # 是否打印SQL
            pool_size=globalAppSettings.db_pool_size,  # 连接池的大小，指定同时在连接池中保持的数据库连接数，默认:5
            max_overflow=globalAppSettings.db_max_overflow,  # 超出连接池大小的连接数，超过这个数量的连接将被丢弃,默认: 5
        )
        # 初始化表
        Base.metadata.create_all(engine)

        create_trigger(engine)
        # 封装获取会话
        Session = sessionmaker(bind=engine, expire_on_commit=False)

@contextmanager
def getDatabaseSession(autoCommitByExit=True):
    _session = Session()
    try:
        yield _session
        # 退出时，是否自动提交
        if autoCommitByExit:
            _session.commit()
    except Exception as e:
        _session.rollback()
        raise e
    finally:
        _session.close()
