import os
import sys
from pathlib import Path

# 1. تعيين قاعدة البيانات للتستات لتكون ملف مؤقت ثابت قبل أي استيراد
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# 2. إضافة فولدر backend للـ Python Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pytest
import app.models  # noqa: F401 (registers Order on Base.metadata)
from app.database import Base, engine

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    # حذف ملف الداتابيز القديم لو موجود لضمان نظافة البيئة
    db_file = Path("test.db")
    if db_file.exists():
        db_file.unlink()

    # إنشاء الجداول
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

    # تنظيف الملف بعد انتهاء كل التيستات
    if db_file.exists():
        db_file.unlink()