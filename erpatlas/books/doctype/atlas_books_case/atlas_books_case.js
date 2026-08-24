frappe.ui.form.on("Atlas Books Case", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.status === "reconciled" || frm.doc.status === "exception") return;
		frm.add_custom_button(__("Reconcile"), () => settle(frm, "reconciled"));
		frm.add_custom_button(__("Exception"), () => {
			frappe.prompt(
				{ fieldname: "note", fieldtype: "Small Text", label: __("Acceptance note"), reqd: 1 },
				(v) => settle(frm, "exception", v.note),
			);
		});
	},
});

function settle(frm, decision, note) {
	frappe.call({
		method: "erpatlas.books.doctype.atlas_books_case.atlas_books_case.settle",
		args: { name: frm.doc.name, decision, note },
		freeze: true,
		callback: () => frm.reload_doc(),
	});
}
