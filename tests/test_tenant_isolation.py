import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.all_models import User, Business
from app.core.security import verify_business_access

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_tenant_isolation_enforcement(db_session):
    # Owner 1 & Business 1
    u1 = User(id="user_1", name="Owner 1", email="u1@agency.com", password_hash="hash", role="owner")
    b1 = Business(id="biz_1", name="Agency 1", owner_id="user_1")
    
    # Owner 2 & Business 2
    u2 = User(id="user_2", name="Owner 2", email="u2@agency.com", password_hash="hash", role="owner")
    b2 = Business(id="biz_2", name="Agency 2", owner_id="user_2")

    db_session.add_all([u1, b1, u2, b2])
    db_session.commit()

    # User 1 accessing Business 1 should succeed
    assert verify_business_access(business_id="biz_1", user=u1, db=db_session) == True

    # User 1 trying to access Business 2 MUST raise HTTP 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        verify_business_access(business_id="biz_2", user=u1, db=db_session)
    assert exc_info.value.status_code == 403
    assert "Forbidden" in exc_info.value.detail
