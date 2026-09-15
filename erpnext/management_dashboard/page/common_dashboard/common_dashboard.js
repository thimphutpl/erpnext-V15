frappe.pages["common-dashboard"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Common Dashboard"),
        single_column: true,
    });
    $(frappe.render_template("common_dashboard")).appendTo(page.body);
    wrapper.site_budget_chart = new frappe.pages["common-dashboard"].SiteBudgetChart(page.body);
    $(wrapper).on("hide", () => wrapper.site_budget_chart.stop_auto_refresh());
    wrapper.site_budget_chart.start_auto_refresh();
};

frappe.pages["common-dashboard"].on_page_show = function (wrapper) {
    wrapper.site_budget_chart.start_auto_refresh();
};

frappe.pages["common-dashboard"].SiteBudgetChart = class {
    constructor(body) {
        this.panel = body.find(".site-budget-panel");
        this.status = this.panel.find(".site-budget-status");
        this.on_visibility_change = () => {
            if (!document.hidden) this.refresh();
        };
    }

    start_auto_refresh() {
        if (this.refresh_timer != null) return;
        document.addEventListener("visibilitychange", this.on_visibility_change);
        this.refresh_timer = setInterval(() => {
            if (!document.hidden) this.refresh();
        }, 60 * 1000);
        if (!document.hidden) this.refresh();
    }

    stop_auto_refresh() {
        clearInterval(this.refresh_timer);
        this.refresh_timer = null;
        document.removeEventListener("visibilitychange", this.on_visibility_change);
    }

    async refresh() {
        if (this.loading) return;
        this.loading = true;
        this.status.prop("hidden", false).text(__("Loading current site budgets and expenses…"));
        try {
            const response = await frappe.call({
                method: "erpnext.management_dashboard.page.common_dashboard.common_dashboard.get_site_budget_chart",
                error: () => {},
            });
            this.render(response.message);
        } catch (error) {
            if (error && error.status === 403) {
                this.destroy_chart();
                this.panel.find(".site-budget-chart").empty();
                this.panel.find(".site-budget-details, .site-budget-notice, .site-budget-over-budget").prop("hidden", true);
            }
            this.status.prop("hidden", false).text(
                error && error.status === 403
                    ? __("You do not have permission to view Site Budget Consumption.")
                    : this.chart
                        ? __("Could not refresh site budgets. Showing the last loaded values; retrying automatically.")
                        : __("Could not load site budgets. The dashboard will retry automatically."),
            );
        } finally {
            this.loading = false;
        }
    }

    render(data) {
        const sites = data.sites;
        const currency = data.currency;
        const format_amount = (value) => value == null
            ? __("Not configured")
            : frappe.format(value, { fieldtype: "Currency", options: currency });
        // Title is static; omit period/timestamp display per preferences.
        this.destroy_chart();
        const chart_element = this.panel.find(".site-budget-chart").empty();
        this.panel.find(".site-budget-details").prop("hidden", !sites.length);
        // Allocation summary and notices have been removed from the UI.
        const missing = sites.filter(site => site.estimated_budget == null);
        const over_budget = sites.map((site, index) => ({ ...site, index })).filter(
            site => site.estimated_budget != null && site.total_expenses > 0
                && site.total_expenses > site.estimated_budget,
        );
        // A hard gradient boundary keeps the portion up to the budget amber.
        // Definitions live outside the chart so redraws and resizing preserve them.
        this.panel.find(".site-budget-color-definitions").html(over_budget.map(site => {
            const budget_percent = Math.max(0, site.estimated_budget / site.total_expenses * 100);
            return `<linearGradient id="site-budget-expense-${site.index}" x1="0" y1="1" x2="0" y2="0" gradientUnits="objectBoundingBox">
                <stop offset="${budget_percent}%" stop-color="#FBBF24" />
                <stop offset="${budget_percent}%" stop-color="#B22222" />
            </linearGradient>`;
        }).join("\n"));
        this.panel.find(".site-budget-bar-colors").text(over_budget.map(site =>
            `.site-budget-panel .site-budget-chart .dataset-1 .bar[data-point-index="${site.index}"] { fill: url("#site-budget-expense-${site.index}") !important; }`,
        ).join("\n"));
        this.panel.find(".site-budget-over-budget")
            .prop("hidden", !over_budget.length)
            .text(__("Red portions show expenses above Estimated Budget: {0}.", [over_budget.map(site => site.site).join(", ")]));
        this.panel.find(".site-budget-notice")
            .prop("hidden", !missing.length)
            .text(__("Estimated Budget is not configured for: {0}.", [missing.map(site => site.site).join(", ")]));
        if (!sites.length) {
            this.status.text(__("No site data is available."));
            return;
        }

        const fields = [
            "estimated_budget", "actual_expenses", "inventory_balance",
            "advance_to_suppliers_balance", "head_office_allocation", "total_expenses",
        ];
        const append_amounts = (row, values) => fields.forEach(field => {
            const cell = $("<td>").addClass("text-right")
                .html(values[field] == null ? "" : format_amount(values[field])).appendTo(row);
            if (field === "head_office_allocation" && values.head_office_allocation_percent != null) {
                cell.attr("title", __("{0}% of Head Office total expenses", [values.head_office_allocation_percent.toFixed(2)]));
            }
        });
        const table = this.panel.find(".site-budget-values").empty();
        sites.forEach(site => {
            const row = $("<tr>").appendTo(table);
            $("<th>").attr("scope", "row").text(site.cost_center).appendTo(row);
            append_amounts(row, site);
        });
        const total_row = $("<tr>").appendTo(this.panel.find(".site-budget-totals").empty());
        $("<th>").attr("scope", "row").text(__("Total")).appendTo(total_row);
        append_amounts(total_row, data.totals);

        this.chart = new frappe.Chart(chart_element[0], {
            type: "bar",
            height: 340,
            animate: false,
            disableEntryAnimation: true,
            colors: ["#60A5FA", "#FBBF24"],
            data: {
                labels: sites.map(site => site.site),
                datasets: [
                    { name: __("Estimated Budget"), values: sites.map(site => site.estimated_budget) },
                    { name: __("Total Expenses"), values: sites.map(site => site.total_expenses) },
                ],
            },
            valuesOverPoints: 1,
            barOptions: { stacked: false, spaceRatio: 0.35 },
            axisOptions: {
                shortenYAxisNumbers: 1,
                numberFormatter: frappe.utils.format_chart_axis_number,
            },
            tooltipOptions: { formatTooltipY: format_amount },
        });
        // Render compact value labels on top of each bar for quick glance.
        this.stop_value_labels = renderBarValueLabels(chart_element[0], sites);
        this.status.text("").prop("hidden", true);
    }

    destroy_chart() {
        if (this.stop_value_labels) {
            this.stop_value_labels();
            this.stop_value_labels = null;
        }
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
};

function formatShortNumber(value) {
    if (value == null) return '';
    const abs = Math.abs(value);
    const sign = value < 0 ? '-' : '';
    if (abs >= 1e12) return sign + (abs / 1e12).toFixed(2) + 'T';
    if (abs >= 1e9) return sign + (abs / 1e9).toFixed(2) + 'B';
    if (abs >= 1e6) return sign + (abs / 1e6).toFixed(2) + 'M';
    if (abs >= 1e3) return sign + (abs / 1e3).toFixed(2) + 'K';
    return sign + abs.toFixed(2);
}

function renderBarValueLabels(chartElement, sites) {
    // Native SVG labels move with their bars during animation and resizing.
    // Redraws recreate the labels, so reapply compact formatting afterwards.
    const format_labels = () => {
        ["estimated_budget", "total_expenses"].forEach((field, dataset) => {
            chartElement.querySelectorAll(`.dataset-${dataset} .data-point-value`).forEach(label => {
                const index = Number(label.parentNode.getAttribute("data-point-index"));
                const text = formatShortNumber(sites[index]?.[field]);
                if (label.textContent !== text) label.textContent = text;
            });
        });
    };
    const observer = new MutationObserver(format_labels);
    observer.observe(chartElement, { childList: true, subtree: true });
    format_labels();
    return () => observer.disconnect();
}
