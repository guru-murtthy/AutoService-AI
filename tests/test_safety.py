import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.services.emergency_stop import activate_emergency_stop, deactivate_emergency_stop, is_emergency_stop_active
from agent.policies.safety import SafetyPolicyEngine, SafetyPolicyViolation

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_emergency_stop_killswitch(db_session):
    policy = SafetyPolicyEngine(db_session)

    # Initial state should be inactive
    assert is_emergency_stop_active(db_session) == False
    assert policy.validate_action("search_leads", {}) == True

    # Activate emergency stop
    activate_emergency_stop(reason="Test killswitch", actor="test_user", db=db_session)
    assert is_emergency_stop_active(db_session) == True

    # Validate action must raise SafetyPolicyViolation
    with pytest.raises(SafetyPolicyViolation):
        policy.validate_action("search_leads", {})

    # Deactivate and verify normal operation resumes
    deactivate_emergency_stop(actor="test_user", db=db_session)
    assert is_emergency_stop_active(db_session) == False
    assert policy.validate_action("search_leads", {}) == True
