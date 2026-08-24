frappe.ui.form.on("Atlas Quantity", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.status === "approved") return;
		frm
			.add_custom_button(__("Approve quantity"), () => {
				frappe.call({
					method: "erpatlas.controls.doctype.atlas_quantity.atlas_quantity.approve",
					args: { quantity: frm.doc.name },
					freeze: true,
					callback: () => frm.reload_doc(),
				});
			})
			.addClass("btn-primary");
	},
});
