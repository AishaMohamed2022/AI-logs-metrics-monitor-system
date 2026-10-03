import os
import sys
from pathlib import Path

# 1. فرض متغير البيئة للتستات
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# 2. إضافة فولدر backend للـ Python Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 3. تجاوز ملف .env وتحديث الـ settings مباشرة لمنع أي تضارب
from app.config import settings
settings.DATABASE_URL = "sqlite:///./test.db"

# 4. إعادة بناء الـ Engine و SessionLocal في app.database لضمان استخدام test.db
import app.database
app.database.engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
app.database.SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=app.database.engine
)

import app.models  # noqa: F401 (تسهيل تسجيل الـ Models مثل Order)
from app.database import Base

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    # حذف ملف الداتابيز القديم لو موجود لضمان نظافة البيئة
    db_file = Path("test.db")
    if db_file.exists():
        db_file.unlink()

    # إنشاء الجداول على الـ Engine الجديد
    Base.metadata.create_all(bind=app.database.engine)
    yield
    Base.metadata.drop_all(bind=app.database.engine)

    # تنظيف الملف بعد انتهاء كل التيستات
    if db_file.exists():
        db_file.unlink()