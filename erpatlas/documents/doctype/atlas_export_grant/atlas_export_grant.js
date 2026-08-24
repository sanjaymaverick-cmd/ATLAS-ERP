frappe.ui.form.on("Atlas Export Grant", {
	refresh(frm) {
		if (frm.doc.status === "Granted") {
			frm.add_custom_button(__("Consume original (single use)"), () => {
				frappe.call({
					method: "erpatlas.documents.doctype.atlas_export_grant.atlas_export_grant.consume",
					args: { grant: frm.doc.name },
					freeze: true,
					callback: () => frm.reload_doc(),
				});
			}).addClass("btn-primary");
		}
	},
});
