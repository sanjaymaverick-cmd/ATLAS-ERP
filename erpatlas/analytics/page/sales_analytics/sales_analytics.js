frappe.pages["sales-analytics"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Who is in the funnel?"),
		single_column: true,
	});
	page.add_field({
		fieldtype: "Link",
		fieldname: "company",
		options: "Company",
		label: __("Legal Entity"),
		change: () => load(page),
	});
	page.add_field({
		fieldtype: "Link",
		fieldname: "project",
		options: "Project",
		label: __("Project"),
		change: () => load(page),
	});
	page.set_primary_action(__("Refresh"), () => load(page));
	load(page);
};

function load(page) {
	const company = page.fields_dict.company.get_value();
	const project = page.fields_dict.project.get_value();
	frappe.call({
		method: "erpatlas.analytics.board.get_sales_analytics",
		args: { company, project },
		freeze: true,
		callback: (r) => render(page, r.message || {}),
	});
}

function render(page, data) {
	const funnel = data.funnel || [];
	const monitor = data.monitor || {};
	const bands = data.bands || {};
	const conv = data.conversion_pct == null ? "—" : data.conversion_pct + "%";
	const rows = funnel
		.map(
			(row) =>
				`<div class="atlas-command-kpi"><span class="atlas-command-kpi-label">${frappe.utils.escape_html(row.stage)}</span><span class="atlas-command-kpi-value">${row.count || 0}</span></div>`,
		)
		.join("");
	page.main.html(`
		<div class="atlas-command">
			<p class="atlas-command-lede">${__("Counts from native Lead. CatBoost stays an external scorer. This page does not book, pay, or lock a unit.")}</p>
			<section class="atlas-command-strip">
				<h3>${__("Funnel")}</h3>
				<div class="atlas-command-kpis">${rows || `<p class="text-muted">${__("No leads in this filter.")}</p>`}</div>
			</section>
			<section class="atlas-command-strip">
				<h3>${__("Monitor")}</h3>
				<div class="atlas-command-kpis">
					<div class="atlas-command-kpi"><span class="atlas-command-kpi-label">${__("Won / closed")}</span><span class="atlas-command-kpi-value">${conv}</span></div>
					<div class="atlas-command-kpi"><span class="atlas-command-kpi-label">${__("Hot")}</span><span class="atlas-command-kpi-value">${bands.hot || 0}</span></div>
					<div class="atlas-command-kpi"><span class="atlas-command-kpi-label">${__("Hybrid scores")}</span><span class="atlas-command-kpi-value">${monitor.hybrid || 0}</span></div>
					<div class="atlas-command-kpi"><span class="atlas-command-kpi-label">${__("External CatBoost")}</span><span class="atlas-command-kpi-value">${monitor.external_catboost || 0}</span></div>
				</div>
				<p class="text-muted">${__("Monitor only — Atlas does not re-run CatBoost here.")}</p>
			</section>
		</div>
	`);
}
