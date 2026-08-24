frappe.ui.form.on("Atlas Inspection", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.result !== "Pending") return;
		frm.add_custom_button(__("Pass"), () => complete(frm, "Pass"));
		frm.add_custom_button(__("Fail"), () => complete(frm, "Fail")).addClass("btn-primary");
	},
});

function complete(frm, result) {
	frappe.call({
		method: "erpatlas.site.doctype.atlas_inspection.atlas_inspection.complete",
		args: { inspection: frm.doc.name, result },
		freeze: true,
		callback: () => frm.reload_doc(),
	});
}
