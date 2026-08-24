frappe.ui.form.on("Atlas Controlled Document", {
	refresh(frm) {
		if (frm.is_new()) return;
		if (frm.doc.status === "Quarantine") {
			frm.add_custom_button(__("Clear quarantine"), () => {
				frappe.call({
					method:
						"erpatlas.documents.doctype.atlas_controlled_document.atlas_controlled_document.clear_quarantine",
					args: { document: frm.doc.name },
					freeze: true,
					callback: () => frm.reload_doc(),
				});
			});
		} else {
			frm.add_custom_button(__("Request original"), () => {
				frappe.call({
					method:
						"erpatlas.documents.doctype.atlas_controlled_document.atlas_controlled_document.request_export",
					args: { document: frm.doc.name },
					freeze: true,
					callback: (r) => {
						frappe.msgprint(__("Waiting on Four-eyes approver. Grant {0}.", [r.message.grant]));
						frm.reload_doc();
					},
				});
			});
			if (frm.doc.status !== "Issued") {
				frm.add_custom_button(__("Issue"), () => {
					frappe.call({
						method:
							"erpatlas.documents.doctype.atlas_controlled_document.atlas_controlled_document.issue",
						args: { document: frm.doc.name },
						freeze: true,
						callback: () => frm.reload_doc(),
					});
				});
			}
		}
	},
});
