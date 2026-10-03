import os
import sys
from pathlib import Path

# 1. إضافة فولدر backend للـ Python Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# 2. تعيين قاعدة البيانات للتستات لتكون SQLite in-memory
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
import app.database as db_module

# إنشاء Engine خاص بالـ Tests يعتمد على SQLite في الذاكرة
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# استبدال الـ engine الرئيسي بـ engine التستات
db_module.engine = test_engine

@pytest.fixture(autouse=True)
def setup_test_database():
    # إنشاء الجداول قبل كل تست
    db_module.Base.metadata.create_all(bind=test_engine)
    yield
    # مسح الجداول بعد ما التست يخلص
    db_module.Base.metadata.drop_all(bind=test_engine)