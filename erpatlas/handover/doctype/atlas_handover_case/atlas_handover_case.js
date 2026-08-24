frappe.ui.form.on("Atlas Handover Case", {
	refresh(frm) {
		if (frm.is_new()) return;
		if (frm.doc.occupancy_certificate !== "Received") {
			frm.add_custom_button(__("Occupancy Certificate received"), () => {
				frappe.call({
					method:
						"erpatlas.handover.doctype.atlas_handover_case.atlas_handover_case.receive_occupancy_certificate",
					args: { handover: frm.doc.name },
					freeze: true,
					callback: () => frm.reload_doc(),
				});
			});
		}
		if (frm.doc.status === "Snagging") {
			frm.add_custom_button(__("Grant possession"), () => {
				frappe.call({
					method:
						"erpatlas.handover.doctype.atlas_handover_case.atlas_handover_case.grant_possession",
					args: { handover: frm.doc.name },
					freeze: true,
					callback: () => frm.reload_doc(),
				});
			}).addClass("btn-primary");
		}
	},
});
