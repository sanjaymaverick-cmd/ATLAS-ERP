from erpatlas.commercial.vendor import refuse_purchase_order, refuse_vendor_active


def test_po_refused_until_vendor_active():
	assert refuse_purchase_order(atlas_stage=None) is None
	assert "Active" in refuse_purchase_order(atlas_stage="Draft")
	assert "Active" in refuse_purchase_order(atlas_stage="Approval")
	assert refuse_purchase_order(atlas_stage="Active") is None


def test_active_needs_gstin():
	assert "GSTIN" in refuse_vendor_active(gstin=None)
	assert "GSTIN" in refuse_vendor_active(gstin="  ")
	assert refuse_vendor_active(gstin="27AAAAA0000A1Z5") is None
