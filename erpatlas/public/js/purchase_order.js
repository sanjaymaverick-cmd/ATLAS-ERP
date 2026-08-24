frappe.ui.form.on("Purchase Order", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.docstatus !== 0) return;
		frm.add_custom_button(__("Send for approval"), () => {
			frappe.call({
				method: "erpatlas.commercial.intake.request_po_approval",
				args: { po: frm.doc.name },
				freeze: true,
				callback: (r) => {
					frappe.msgprint(__("Waiting in Approvals: {0}", [(r.message || {}).approval || ""]));
					frm.reload_doc();
				},
			});
		}).addClass("btn-primary");
	},
});
