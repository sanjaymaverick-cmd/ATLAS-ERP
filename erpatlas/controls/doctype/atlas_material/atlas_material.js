frappe.ui.form.on("Atlas Material", {
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Receive"), () => qty_call(frm, "receive"));
		frm.add_custom_button(__("Issue"), () => qty_call(frm, "issue"));
	},
});

function qty_call(frm, action) {
	frappe.prompt({ fieldname: "qty", fieldtype: "Float", label: __("Quantity"), reqd: 1 }, (v) => {
		frappe.call({
			method: `erpatlas.controls.doctype.atlas_material.atlas_material.${action}`,
			args: { material: frm.doc.name, qty: v.qty },
			freeze: true,
			callback: () => frm.reload_doc(),
		});
	});
}
