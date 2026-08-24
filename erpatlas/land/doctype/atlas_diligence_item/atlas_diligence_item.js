frappe.ui.form.on("Atlas Diligence Item", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.status === "clear") return;
		frm.add_custom_button(__("Clear"), () => set_status(frm, "clear")).addClass("btn-primary");
		if (frm.doc.status !== "flagged") {
			frm.add_custom_button(__("Flag"), () => set_status(frm, "flagged"));
		}
	},
});

function set_status(frm, status) {
	frappe.call({
		method: "erpatlas.land.doctype.atlas_diligence_item.atlas_diligence_item.set_status",
		args: { item: frm.doc.name, status },
		freeze: true,
		callback: () => frm.reload_doc(),
	});
}
