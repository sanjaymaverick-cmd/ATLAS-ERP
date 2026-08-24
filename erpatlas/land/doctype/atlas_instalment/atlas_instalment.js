frappe.ui.form.on("Atlas Instalment", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.status === "paid") return;
		frm.add_custom_button(__("Record paid (ops only)"), () => {
			frappe.call({
				method: "erpatlas.land.doctype.atlas_instalment.atlas_instalment.mark_paid",
				args: { name: frm.doc.name },
				freeze: true,
				callback: () => frm.reload_doc(),
			});
		}).addClass("btn-primary");
	},
});
