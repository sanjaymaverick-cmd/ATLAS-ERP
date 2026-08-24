frappe.ui.form.on("Atlas Parcel", {
	refresh(frm) {
		if (frm.is_new()) return;
		if (frm.doc.status === "acquired" || frm.doc.status === "closed") return;
		frm.add_custom_button(__("Start standard title pack"), () => {
			frappe.call({
				method: "erpatlas.land.doctype.atlas_parcel.atlas_parcel.start_title_pack",
				args: { parcel: frm.doc.name },
				freeze: true,
				callback: () => frm.reload_doc(),
			});
		});
		frm
			.add_custom_button(__("Acquire"), () => {
				frappe.prompt(
					[
						{
							fieldname: "consideration",
							fieldtype: "Currency",
							label: __("Consideration"),
							reqd: 1,
							default: frm.doc.consideration,
						},
						{
							fieldname: "sale_deed_no",
							fieldtype: "Data",
							label: __("Sale deed number"),
							reqd: 1,
							default: frm.doc.sale_deed_no,
						},
						{
							fieldname: "advocate_name",
							fieldtype: "Data",
							label: __("Advocate"),
							default: frm.doc.advocate_name,
						},
					],
					(v) => {
						frappe.call({
							method: "erpatlas.land.doctype.atlas_parcel.atlas_parcel.acquire",
							args: {
								parcel: frm.doc.name,
								consideration: v.consideration,
								sale_deed_no: v.sale_deed_no,
								advocate_name: v.advocate_name,
							},
							freeze: true,
							callback: () => frm.reload_doc(),
						});
					},
					__("Acquire parcel"),
				);
			})
			.addClass("btn-primary");
	},
});
