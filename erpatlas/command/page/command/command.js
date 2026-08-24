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
		this.page.set_secondary_action(__("Board pack PDF"), () => this.download_pack());
	}

	download_pack() {
		open_url_post("/api/method/erpatlas.command.board.download_boardpack", {
			company: this.company_field.get_value(),
			project: this.project_field.get_value(),
		});
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
		const inr = (value) => frappe.format(value || 0, { fieldtype: "Currency" });
		const risks = data.risk || [];
		const risk_html = `<section class="atlas-command-exceptions">
					<h3>${__("Risk")}</h3>
					<p class="text-muted">${__("Deterministic thresholds from Atlas Settings. Cards advise only — they do not approve, pay, or change a unit.")}</p>
					<div class="atlas-command-card-list">${
						risks.length
							? risks
									.map((row) => {
										const route = (row.doctype || "").toLowerCase().replace(/ /g, "-");
										const href =
											row.doctype && row.refs && row.refs[0]
												? `/app/${route}/${encodeURIComponent(row.refs[0])}`
												: "#";
										const waiter = row.waiting_on
											? ` · ${__("Waiting on")} ${frappe.utils.escape_html(row.waiting_on)}`
											: "";
										return `<a class="atlas-command-card ${row.severity === "red" ? "is-stale" : "is-warn"}" href="${href}">
							<span class="atlas-command-card-kicker">${frappe.utils.escape_html(row.domain || "")} · ${frappe.utils.escape_html(row.severity || "")}${waiter}</span>
							<span class="atlas-command-card-title">${frappe.utils.escape_html(row.title || "")}</span>
							<span class="atlas-command-card-meta">${frappe.utils.escape_html(row.driver || "")}</span>
						</a>`;
									})
									.join("")
							: `<p class="text-muted">${__("No risk cards in this filter.")}</p>`
					}</div>
				</section>`;
		const portfolio = data.portfolio || [];
		const spark = data.sparkline || [];
		const heat_html = `<section class="atlas-command-strip">
					<h3>${__("Portfolio")}</h3>
					<p class="text-muted">${__("Heat map from live diary, failed work, Approvals. Advise only.")}</p>
					${spark.length ? `<p class="text-muted">${__("Live booking value strip")}: ${spark.join(" · ")}</p>` : ""}
					<div class="atlas-command-kpis">
						${
							portfolio.length
								? portfolio
										.map((row) => {
											const tone =
												row.health === "red" ? "is-stale" : row.health === "amber" ? "is-warn" : "";
											return kpi(
												frappe.utils.escape_html(row.project || ""),
												frappe.utils.escape_html((row.drivers || [])[0] || row.health),
												tone,
											);
										})
										.join("")
								: `<p class="text-muted">${__("No projects in this filter.")}</p>`
						}
					</div>
				</section>`;
		const o30 = data.outlook_30 || {};
		const o90 = data.outlook_90 || {};
		const brief = data.brief || [];
		const outlook_html = `<section class="atlas-command-strip">
					<h3>${__("Outlook")}</h3>
					<p class="text-muted">${__("Linear read-only forecast from snapshots ({0}). Not CatBoost. Does not pay, lock, or decide.", [o30.model_id || "linear-snapshot"])}</p>
					<div class="atlas-command-kpis">
						${kpi(__("30d booking value"), inr(o30.projected))}
						${kpi(__("90d booking value"), inr(o90.projected))}
					</div>
					${brief.map((line) => `<p>${frappe.utils.escape_html(line)}</p>`).join("")}
				</section>`;
		const cash = data.cash || {};
		const cash_html = data.shows_cash
			? `<section class="atlas-command-strip">
					<h3>${__("Cash and runway")}</h3>
					<p class="text-muted">${__("From ERPNext GL (Bank + Cash). Not a shadow ledger. Runway is cash ÷ 3-month average net outflow.")}</p>
					<div class="atlas-command-kpis">
						${kpi(__("Cash position"), inr(cash.cash_position))}
						${kpi(__("Bank"), inr(cash.bank))}
						${kpi(__("Cash"), inr(cash.cash))}
						${kpi(__("Runway (months)"), cash.runway_months == null ? "—" : cash.runway_months)}
					</div>
				</section>`
			: "";
		const money = data.money || {};
		const money_html = data.shows_money
			? `<section class="atlas-command-strip">
					<h3>${__("Sales and collections")}</h3>
					<p class="text-muted">${__("From Atlas Booking and Payment Entry. Not bank cash, not runway.")}</p>
					<div class="atlas-command-kpis">
						${kpi(__("Live booking value"), inr(money.booking_value_live))}
						${kpi(__("Booking value MTD"), inr(money.booking_value_mtd))}
						${kpi(__("Collected MTD"), inr(money.collections_mtd))}
						${kpi(__("Plan"), inr(money.plan_gross))}
						${kpi(__("Collected on plan"), inr(money.plan_collected))}
						${kpi(__("Receivable"), inr(money.receivable), money.receivable > 0 ? "is-warn" : "")}
						${kpi(__("Commission accrued"), inr(money.commission_liability))}
						${kpi(__("Hold → book"), money.hold_conversion_pct == null ? "—" : money.hold_conversion_pct + "%")}
						${kpi(__("Channel bookings"), money.channel_bookings || 0)}
						${kpi(__("In-house bookings"), money.in_house_bookings || 0)}
					</div>
				</section>`
			: "";

		this.page.main.html(`
			<div class="atlas-command">
				<p class="atlas-command-lede">${__("Waiting for a yes drives the day. Green totals are secondary. Command does not approve, pay, or change a unit.")}</p>
				<section class="atlas-command-exceptions">
					<h3>${__("Waiting for a yes")}</h3>
					<p class="text-muted">${__("Pending Approvals, oldest first. Past {0} days is stale.", [sla])}</p>
					<div class="atlas-command-card-list">${exception_html}</div>
				</section>
				${risk_html}
				${heat_html}
				${outlook_html}
				${cash_html}
				${money_html}
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
