frappe.ui.form.on("Atlas Booking", {
	refresh(frm) {
		if (frm.is_new()) return;
		if (frm.doc.status === "Draft") {
			frm.add_custom_button(__("Activate"), () => {
				frappe.call({
					method: "erpatlas.booking.doctype.atlas_booking.atlas_booking.activate",
					args: { booking: frm.doc.name },
					freeze: true,
					callback: () => frm.reload_doc(),
				});
			}).addClass("btn-primary");
		}
		if (frm.doc.status === "Active") {
			frm.add_custom_button(__("Collect"), () => {
				frappe.prompt(
					[
						{
							fieldname: "amount",
							fieldtype: "Currency",
							label: __("Amount"),
							reqd: 1,
						},
						{
							fieldname: "mode_of_payment",
							fieldtype: "Link",
							options: "Mode of Payment",
							label: __("Mode of payment"),
						},
					],
					(values) => {
						frappe.call({
							method: "erpatlas.booking.doctype.atlas_booking.atlas_booking.collect",
							args: {
								booking: frm.doc.name,
								amount: values.amount,
								mode_of_payment: values.mode_of_payment,
							},
							freeze: true,
							callback: () => frm.reload_doc(),
						});
					},
					__("Collect against next unpaid step"),
				);
			}).addClass("btn-primary");
			frm.add_custom_button(__("Cancel booking"), () => {
				frappe.confirm(__("Cancel this booking and return the unit to Available?"), () => {
					frappe.call({
						method: "erpatlas.booking.doctype.atlas_booking.atlas_booking.cancel",
						args: { booking: frm.doc.name },
						freeze: true,
						callback: () => frm.reload_doc(),
					});
				});
			});
		}
	},
});
