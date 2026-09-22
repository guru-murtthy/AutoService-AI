import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.all_models import User, Business, Lead, Quotation
from app.core.security import verify_business_access

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_multi_tenant_resource_isolation_audit(db_session):
    u1 = User(id="u1", name="Owner 1", email="u1@test.com", password_hash="hash", role="owner")
    b1 = Business(id="b1", name="Business 1", owner_id="u1")
    l1 = Lead(id="l1", business_id="b1", customer_id="c1", destination="Coorg")

    u2 = User(id="u2", name="Owner 2", email="u2@test.com", password_hash="hash", role="owner")
    b2 = Business(id="b2", name="Business 2", owner_id="u2")
    l2 = Lead(id="l2", business_id="b2", customer_id="c2", destination="Mysore")

    db_session.add_all([u1, b1, l1, u2, b2, l2])
    db_session.commit()

    # Owner 1 accessing Business 1 -> Authorized
    assert verify_business_access("b1", user=u1, db=db_session) == True

    # Owner 1 accessing Business 2 -> Forbidden HTTP 403
    with pytest.raises(HTTPException) as exc:
        verify_business_access("b2", user=u1, db=db_session)
    assert exc.value.status_code == 403

    # Owner 2 accessing Business 1 -> Forbidden HTTP 403
    with pytest.raises(HTTPException) as exc:
        verify_business_access("b1", user=u2, db=db_session)
    assert exc.value.status_code == 403
