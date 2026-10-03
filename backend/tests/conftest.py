import os
import sys
from pathlib import Path

# 1. تعيين قاعدة البيانات للتستات لتكون SQLite in-memory قبل استيراد أي موديل أو داتابيز
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# 2. إضافة فولدر backend للـ Python Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pytest
import app.models  # noqa: F401 (registers Order on Base.metadata)
from app.database import Base, engine

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)