from datetime import datetime, timezone
from core.domain.models import Customer, Invoice

def test_customer_creation():
    c = Customer(
        id="c1",
        tenant_id="t1",
        name="Acme Corp",
        contact_person="John",
        phone="1234567890",
        segment="retail",
        credit_limit_paise=100000,
        is_business_buyer=True
    )
    assert c.id == "c1"
    assert c.language == "en"

def test_invoice_creation():
    i = Invoice(
        id="i1",
        tenant_id="t1",
        customer_id="c1",
        number="INV-001",
        issued_on=datetime.now(timezone.utc),
        due_on=datetime.now(timezone.utc),
        amount_paise=50000,
        status="open"
    )
    assert i.paid_paise == 0
