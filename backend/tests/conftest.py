import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pytest
from app.database import Base, engine

@pytest.fixture(autouse=True)
def setup_test_database():
    # Create all tables before tests run
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after tests run
    Base.metadata.drop_all(bind=engine)