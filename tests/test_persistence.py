import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.all_models import Business, Customer, Lead, Quotation, Booking, AuditLog

def test_database_persistence(tmp_path):
    db_file = tmp_path / "test_persist.db"
    db_url = f"sqlite:///{db_file}"

    # Phase 1: Write records in session 1
    engine1 = create_engine(db_url)
    Base.metadata.create_all(bind=engine1)
    Session1 = sessionmaker(bind=engine1)
    s1 = Session1()

    b = Business(id="b_persist", name="Persistent Travel", owner_id="o1")
    c = Customer(id="c_persist", business_id="b_persist", name="Persistent Customer", phone="+919000000000")
    l = Lead(id="l_persist", business_id="b_persist", customer_id="c_persist", destination="Ooty", status="QUALIFIED")
    q = Quotation(id="q_persist", lead_id="l_persist", quotation_number="QT-PERSIST-1", subtotal=5000.0, tax=250.0, total=5250.0, status="APPROVED")
    a = AuditLog(id="a_persist", actor_type="system", action="TEST_PERSISTENCE", resource_type="test", resource_id="1")

    s1.add_all([b, c, l, q, a])
    s1.commit()
    s1.close()
    engine1.dispose()

    # Phase 2: Open session 2 on same database file and verify persistence
    engine2 = create_engine(db_url)
    Session2 = sessionmaker(bind=engine2)
    s2 = Session2()

    assert s2.query(Business).filter(Business.id == "b_persist").first() is not None
    assert s2.query(Customer).filter(Customer.id == "c_persist").first().name == "Persistent Customer"
    assert s2.query(Lead).filter(Lead.id == "l_persist").first().destination == "Ooty"
    assert s2.query(Quotation).filter(Quotation.id == "q_persist").first().total == 5250.0
    assert s2.query(AuditLog).filter(AuditLog.id == "a_persist").first() is not None

    s2.close()
    engine2.dispose()
