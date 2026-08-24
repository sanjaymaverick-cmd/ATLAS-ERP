frappe.ui.form.on("Atlas Change Item", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.status === "closed") return;
		if (frm.doc.kind === "rfi") {
			frm.add_custom_button(__("Respond"), () => {
				frappe.prompt(
					{ fieldname: "response", fieldtype: "Small Text", label: __("Response"), reqd: 1 },
					(v) => {
						frappe.call({
							method: "erpatlas.change_control.doctype.atlas_change_item.atlas_change_item.respond",
							args: { name: frm.doc.name, response: v.response },
							freeze: true,
							callback: () => frm.reload_doc(),
						});
					},
				);
			}).addClass("btn-primary");
		}
		if (frm.doc.kind === "ncr") {
			frm.add_custom_button(__("Close NCR"), () => {
				frappe.call({
					method: "erpatlas.change_control.doctype.atlas_change_item.atlas_change_item.close_ncr",
					args: { name: frm.doc.name },
					freeze: true,
					callback: () => frm.reload_doc(),
				});
			});
		}
		if (frm.doc.kind === "change" && frm.doc.status === "open") {
			frm.add_custom_button(__("Send for approval"), () => {
				frappe.call({
					method: "erpatlas.change_control.doctype.atlas_change_item.atlas_change_item.send_vo_for_approval",
					args: { name: frm.doc.name },
					freeze: true,
					callback: () => frm.reload_doc(),
				});
			}).addClass("btn-primary");
		}
	},
});
