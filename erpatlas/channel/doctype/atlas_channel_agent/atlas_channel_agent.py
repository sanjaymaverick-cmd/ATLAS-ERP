import frappe
from frappe import _
from frappe.model.document import Document

from erpatlas.channel.roster import refuse_bind


class AtlasChannelAgent(Document):
	def validate(self):
		err = refuse_bind(user=self.user, channel_company=self.channel_company)
		if err:
			frappe.throw(_(err))

	def after_insert(self):
		_bind_permission(self.user, self.channel_company)
		_ensure_agent_role(self.user)

	def on_update(self):
		_bind_permission(self.user, self.channel_company)


def _bind_permission(user: str, channel_company: str):
	"""Runtime User Permission. Not a fixture."""
	exists = frappe.db.exists(
		"User Permission",
		{"user": user, "allow": "Atlas Channel Company", "for_value": channel_company},
	)
	if exists:
		return
	frappe.get_doc(
		{
			"doctype": "User Permission",
			"user": user,
			"allow": "Atlas Channel Company",
			"for_value": channel_company,
			"apply_to_all_doctypes": 1,
		}
	).insert(ignore_permissions=True)


def _ensure_agent_role(user: str):
	doc = frappe.get_doc("User", user)
	if any(r.role == "Atlas Channel Agent" for r in doc.roles):
		return
	doc.append("roles", {"role": "Atlas Channel Agent"})
	doc.save(ignore_permissions=True)
