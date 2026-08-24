frappe.provide("atlas");

frappe.pages["command"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Command"),
		single_column: true,
	});
	page.set_title(__("Are we on track, and what needs a yes today?"));
	new atlas.CommandBoard(page);
};

atlas.CommandBoard = class CommandBoard {
	constructor(page) {
		this.page = page;
		this.make_filters();
		this.refresh();
	}

	make_filters() {
		this.company_field = this.page.add_field({
			fieldtype: "Link",
			fieldname: "company",
			options: "Company",
			label: __("Legal Entity"),
			change: () => this.refresh(),
		});
		this.project_field = this.page.add_field({
			fieldtype: "Link",
			fieldname: "project",
			options: "Project",
			label: __("Project"),
			get_query: () => {
				const company = this.company_field.get_value();
				if (!company) return {};
				return { filters: { company } };
			},
			change: () => this.refresh(),
		});
		this.page.set_primary_action(__("Refresh"), () => this.refresh());
	}

	refresh() {
		frappe.call({
			method: "erpatlas.command.board.get_command",
			args: {
				company: this.company_field.get_value(),
				project: this.project_field.get_value(),
			},
			freeze: true,
			callback: (r) => this.render(r.message || {}),
		});
	}

	render(data) {
		const units = data.units || {};
		const holds = data.holds || {};
		const approvals = data.approvals || {};
		const exceptions = data.exceptions || [];
		const sla = approvals.sla_days;
		const exception_html = exceptions.length
			? exceptions
					.map((row) => {
						const stale = (row.aging_days || 0) >= sla;
						const amount =
							row.amount != null && row.amount !== ""
								? frappe.format(row.amount, { fieldtype: "Currency" })
								: "";
						return `<a class="atlas-command-card ${stale ? "is-stale" : ""}" href="/app/atlas-approval/${encodeURIComponent(row.name)}">
							<span class="atlas-command-card-kicker">${frappe.utils.escape_html(row.kind || "")} · ${frappe.utils.escape_html(row.waiting_on || "")} · ${row.aging_days || 0}d</span>
							<span class="atlas-command-card-title">${frappe.utils.escape_html(row.title || row.name)}</span>
							<span class="atlas-command-card-meta">${frappe.utils.escape_html(row.project || "")}${amount ? " · " + amount : ""}</span>
						</a>`;
					})
					.join("")
			: `<p class="text-muted">${__("No pending Approvals in this filter.")}</p>`;

		const kpi = (label, value, tone) =>
			`<div class="atlas-command-kpi ${tone || ""}"><span class="atlas-command-kpi-label">${label}</span><span class="atlas-command-kpi-value">${value}</span></div>`;

		this.page.main.html(`
			<div class="atlas-command">
				<p class="atlas-command-lede">${__("Waiting for a yes drives the day. Green totals are secondary. Command does not approve, pay, or change a unit.")}</p>
				<section class="atlas-command-exceptions">
					<h3>${__("Waiting for a yes")}</h3>
					<p class="text-muted">${__("Pending Approvals, oldest first. Past {0} days is stale.", [sla])}</p>
					<div class="atlas-command-card-list">${exception_html}</div>
				</section>
				<section class="atlas-command-strip">
					<h3>${__("Inventory and holds")}</h3>
					<div class="atlas-command-kpis">
						${kpi(__("Available"), units.Available || 0)}
						${kpi(__("Held"), units.Held || 0)}
						${kpi(__("Booked"), units.Booked || 0)}
						${kpi(__("Sold"), units.Sold || 0)}
						${kpi(__("Live holds"), holds.held || 0)}
						${kpi(__("Holds expiring soon"), holds.expiring_soon || 0, holds.expiring_soon ? "is-stale" : "")}
					</div>
				</section>
				<section class="atlas-command-strip">
					<h3>${__("Approvals")}</h3>
					<div class="atlas-command-kpis">
						${kpi(__("Pending"), approvals.pending || 0, approvals.pending ? "is-warn" : "")}
						${kpi(__("Past SLA"), approvals.past_sla || 0, approvals.past_sla ? "is-stale" : "")}
						${kpi(__("Oldest (days)"), approvals.oldest_days || 0, (approvals.oldest_days || 0) >= sla ? "is-stale" : "")}
					</div>
				</section>
			</div>
		`);
	}
};
