"""Customer 360 from Lead + Booking + Commission. No writes."""

from __future__ import annotations

from typing import Iterable, Mapping

from erpatlas.pipeline.ingest import normalize_phone


def customer_file(
	*,
	phone: str | None,
	leads: Iterable[Mapping] = (),
	bookings: Iterable[Mapping] = (),
	commissions: Iterable[Mapping] = (),
) -> dict:
	key = normalize_phone(phone)
	return {
		"phone": key,
		"leads": [dict(r) for r in leads],
		"bookings": [dict(r) for r in bookings],
		"commissions": [dict(r) for r in commissions],
		"creates_payment_entry": False,
		"writes_unit": False,
		"decides_approval": False,
	}
