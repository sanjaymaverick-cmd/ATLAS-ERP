import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, today

from erpatlas.property_inventory.lock import (
	AVAILABLE,
	HELD,
	HOLD_HELD,
	HOLD_RELEASED,
	channel_needs_booking_approval,
	live_unit_key,
	refuse_exclusive_hold,
	refuse_hold,
	refuse_hold_without_report,
)
from erpatlas.property_inventory.lock_adapter import expire_due_holds, try_set_status
from erpatlas.property_inventory.permissions import CHANNEL_ROLES, channel_company_for


class AtlasUnitHold(Document):
	def validate(self):
		unit = frappe.get_doc("Atlas Unit", self.unit)
		self.project = unit.project
		self.live_unit = live_unit_key(status=self.status, unit=self.unit, hold_name=self.name)
		if self.is_new():
			self._validate_new(unit)

	def after_insert(self):
		if self.status != HOLD_HELD:
			return
		err = try_set_status(self.unit, AVAILABLE, HELD, f"Hold {self.name}")
		if err:
			frappe.throw(_(err))

	def _validate_new(self, unit):
		expire_due_holds()
		unit.reload()
		err = refuse_hold(status=unit.status, code=unit.code)
		if err:
			frappe.throw(_(err))
		roles = frappe.get_roles()
		err = refuse_hold_without_report(roles=roles, has_today_report=_has_today_report())
		if err:
			frappe.throw(_(err))
		if set(roles) & CHANNEL_ROLES:
			company = channel_company_for(frappe.session.user)
			if not company:
				frappe.throw(_("Channel seats must be bound to a Channel Company."))
			self.channel_company = company
		exclusive = None
		if unit.project and frappe.get_meta("Project").has_field("atlas_exclusive_channel_company"):
			exclusive = frappe.db.get_value("Project", unit.project, "atlas_exclusive_channel_company")
		err = refuse_exclusive_hold(exclusive_channel=exclusive, hold_channel=self.channel_company)
		if err:
			frappe.throw(_(err))
		if not self.until:
			days = frappe.db.get_single_value("Atlas Settings", "default_hold_days") or 7
			self.until = add_days(today(), int(days))
		self.status = HOLD_HELD
		self.live_unit = live_unit_key(status=HOLD_HELD, unit=self.unit, hold_name=None)


def _has_today_report() -> bool:
	"""Channel Daily Report plugs `atlas_has_today_report`."""
	hook = frappe.get_hooks("atlas_has_today_report")
	if not hook:
		return True
	return bool(frappe.call(hook[0]))


@frappe.whitelist()
def place_hold(unit: str, customer_name: str, until: str | None = None, agent: str | None = None):
	doc = frappe.get_doc(
		{
			"doctype": "Atlas Unit Hold",
			"unit": unit,
			"customer_name": customer_name,
			"until": until,
			"agent": agent or frappe.session.user,
			"status": HOLD_HELD,
		}
	)
	doc.insert()
	return doc.as_dict()


@frappe.whitelist()
def release_hold(hold: str):
	doc = frappe.get_doc("Atlas Unit Hold", hold)
	if doc.status != HOLD_HELD:
		frappe.throw(_("Hold not active."))
	err = try_set_status(doc.unit, HELD, AVAILABLE, "Hold released")
	if err:
		frappe.throw(_(err))
	doc.status = HOLD_RELEASED
	doc.live_unit = live_unit_key(status=HOLD_RELEASED, unit=doc.unit, hold_name=doc.name)
	doc.save()
	return doc.as_dict()


@frappe.whitelist()
def request_booking(hold: str, value: float, steps=None):
	doc = frappe.get_doc("Atlas Unit Hold", hold)
	if doc.status != HOLD_HELD:
		frappe.throw(_("Hold not active."))
	unit = frappe.get_doc("Atlas Unit", doc.unit)
	parsed = None
	if steps:
		parsed = frappe.parse_json(steps) if isinstance(steps, str) else steps
	if channel_needs_booking_approval(doc.channel_company):
		from erpatlas.approvals.intake import raise_approval

		if doc.booking_requested:
			frappe.throw(_("This hold is already waiting in Approvals."))
		name = raise_approval(
			kind="Hold booking",
			title=f"Hold → booking · {unit.code} · {doc.customer_name}",
			project=doc.project,
			waiting_on="Sales Manager / MD",
			amount=float(value),
			ref_doctype="Atlas Unit Hold",
			ref_name=doc.name,
			context="Unit stays locked until approved.",
		)
		doc.booking_requested = 1
		doc.booking_value = value
		doc.save()
		return {"approval": name, "status": doc.status}
	from erpatlas.booking.activate import activate_from_hold

	return activate_from_hold(hold, consideration=value, steps=parsed)
