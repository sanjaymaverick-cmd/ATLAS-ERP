"""Sales Order / collect posting payloads — research/02 + /06. No site."""

from decimal import Decimal

from erpatlas.books.payment_gst import GST_NONE, ON_INVOICE, ON_RECEIPT, money
from erpatlas.books.posting import collect_posting, payment_entry_payload, sales_order_payload


def test_sales_order_payload_links_booking_and_unit_non_stock_line():
	steps = [
		{"percent": money("10"), "gross": money("105000"), "due_date": "2026-09-01"},
		{"percent": money("90"), "gross": money("945000"), "due_date": "2026-12-01"},
	]
	payload = sales_order_payload(
		customer="CUST-YADAV",
		company="Dukia",
		project="PROJ-1",
		item_code="ATLAS-UNIT",
		unit_code="A-101",
		booking="ABK-00001",
		unit="AUN-00001",
		taxable_total="1000000",
		steps=steps,
		transaction_date="2026-08-24",
		delivery_date="2026-08-24",
	)
	assert payload["doctype"] == "Sales Order"
	assert payload["atlas_booking"] == "ABK-00001"
	assert payload["atlas_unit"] == "AUN-00001"
	assert payload["items"][0]["qty"] == 1
	assert payload["items"][0]["item_code"] == "ATLAS-UNIT"
	assert payload["items"][0]["rate"] == 1000000.0
	assert payload["payment_schedule"][0]["payment_amount"] == 105000.0
	assert sum(s["invoice_portion"] for s in payload["payment_schedule"]) == 100.0


def test_on_receipt_collect_posts_sales_invoice_then_payment():
	posting = collect_posting(
		policy=ON_RECEIPT,
		receipt="105000",
		grand_total="1050000",
		sales_order="SAL-ORD-1",
	)
	assert posting["path"] == "sales_invoice_then_payment"
	assert posting["against"] == "Sales Invoice"
	assert posting["invoice_qty"] == Decimal("0.100000")
	assert posting["amount"] == money("105000")


def test_on_invoice_and_none_collect_against_sales_order():
	for policy in (ON_INVOICE, GST_NONE):
		posting = collect_posting(
			policy=policy, receipt="50", grand_total="100", sales_order="SO-1"
		)
		assert posting["against"] == "Sales Order"
		assert posting["reference"] == "SO-1"
		assert posting["path"] == "payment_against_sales_order"


def test_payment_entry_is_receive_against_customer_never_commission():
	pe = payment_entry_payload(
		company="Dukia",
		customer="CUST-YADAV",
		amount="105000",
		against_doctype="Sales Invoice",
		against_name="SINV-1",
		booking="ABK-1",
		mode_of_payment="Cash",
		paid_from="Debtors",
		paid_to="Cash",
		posting_date="2026-08-24",
	)
	assert pe["payment_type"] == "Receive"
	assert pe["party_type"] == "Customer"
	assert pe["atlas_booking"] == "ABK-1"
	assert "commission" not in str(pe).lower()
	assert pe["references"][0]["reference_doctype"] == "Sales Invoice"
