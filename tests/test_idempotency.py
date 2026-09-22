import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.idempotency import check_and_store_idempotency_key

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_idempotency_key_deduplication(db_session):
    token = "req_token_abc_123"
    action = "CREATE_QUOTE"

    # First attempt with unique key should succeed
    res1 = check_and_store_idempotency_key(token, action, db_session)
    assert res1 == True

    # Duplicate attempt with same key must return False
    res2 = check_and_store_idempotency_key(token, action, db_session)
    assert res2 == False
