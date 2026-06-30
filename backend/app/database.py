"""数据库连接与会话管理"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.app.config import get_settings

settings = get_settings()
DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):
    """SQLite 优化配置"""
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """所有模型的基类"""
    pass


def get_db():
    """FastAPI 依赖注入 - 数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建所有表"""
    # 导入所有模型确保注册
    import backend.app.models.user  # noqa
    import backend.app.models.chat  # noqa
    import backend.app.models.product  # noqa
    import backend.app.models.influencer  # noqa
    Base.metadata.create_all(bind=engine)
