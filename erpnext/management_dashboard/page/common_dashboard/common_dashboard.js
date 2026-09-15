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
        this.progress_panel = body.find(".site-progress-panel");
        this.progress_status = this.progress_panel.find(".site-progress-status");
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
        this.progress_status.prop("hidden", false).text(__("Loading current project progress…"));
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
                this.progress_panel.find(".site-progress-chart").empty();
            }
            this.status.prop("hidden", false).text(
                error && error.status === 403
                    ? __("You do not have permission to view Site Budget Consumption.")
                    : this.chart
                        ? __("Could not refresh site budgets. Showing the last loaded values; retrying automatically.")
                        : __("Could not load site budgets. The dashboard will retry automatically."),
            );
            this.progress_status.prop("hidden", false).text(
                error && error.status === 403
                    ? __("You do not have permission to view project financial progress.")
                    : this.progress_chart
                        ? __("Could not refresh project progress. Showing the last loaded values; retrying automatically.")
                        : __("Could not load project progress. The dashboard will retry automatically."),
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
            this.render_progress([]);
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
        this.render_progress(data.progress || []);
    }

    render_progress(progress) {
        this.destroy_progress_chart();
        const chart_element = this.progress_panel.find(".site-progress-chart").empty();
        if (!progress.length) {
            this.progress_status.text(__("No project progress data is available.")).prop("hidden", false);
            return;
        }
        this.progress_chart = new ProjectProgressChart(chart_element[0], progress);
        this.progress_status.text("").prop("hidden", true);
    }

    destroy_progress_chart() {
        if (this.progress_chart) {
            this.progress_chart.destroy();
            this.progress_chart = null;
        }
    }

    destroy_chart() {
        this.destroy_progress_chart();
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

function formatProgressPercent(value) {
    return value == null ? __("N/A") : `${Number(value).toFixed(2)}%`;
}

function renderBarValueLabels(chartElement, sites, fields = ["estimated_budget", "total_expenses"], formatter = formatShortNumber) {
    // Native SVG labels move with their bars during animation and resizing.
    // Redraws recreate the labels, so reapply compact formatting afterwards.
    const format_labels = () => {
        fields.forEach((field, dataset) => {
            chartElement.querySelectorAll(`.dataset-${dataset} .data-point-value`).forEach(label => {
                const index = Number(label.parentNode.getAttribute("data-point-index"));
                const text = formatter(sites[index]?.[field]);
                if (label.textContent !== text) label.textContent = text;
            });
        });
    };
    const observer = new MutationObserver(format_labels);
    observer.observe(chartElement, { childList: true, subtree: true });
    format_labels();
    return () => observer.disconnect();
}

// A fixed SVG scale keeps both percentage axes at 0–100 in 10% steps.
// Only the drawn height is bounded; labels and tooltips retain the actual ratio.
class ProjectProgressChart {
    constructor(element, progress) {
        this.element = element;
        const escape = value => frappe.utils.escape_html(String(value));
        const left = 86, right = 1014, top = 52, bottom = 302;
        const step = (right - left) / progress.length;
        const bar_width = Math.min(64, step * 0.34);
        const series = [
            { field: "physical_progress", name: __("Physical Progress"), color: "#60A5FA" },
            { field: "financial_progress", name: __("Financial Progress"), color: "#8BC34A" },
        ];
        const svg = [
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 360" width="1100" height="360" class="site-progress-svg">',
            `<title>${escape(__("Physical Progress vs Financial Progress"))}</title>`,
        ];
        series.forEach((dataset, index) => {
            const x = 8 + index * 170;
            svg.push(`<circle cx="${x}" cy="18" r="5" fill="${dataset.color}" />`,
                `<text x="${x + 12}" y="22" class="site-progress-legend">${escape(dataset.name)}</text>`);
        });
        for (let percent = 0; percent <= 100; percent += 10) {
            const y = bottom - (bottom - top) * percent / 100;
            svg.push(
                `<line x1="${left}" x2="${right}" y1="${y}" y2="${y}" class="site-progress-grid" />`,
                `<text x="${left - 9}" y="${y}" dy="0.35em" text-anchor="end" class="site-progress-tick">${percent.toFixed(2)}%</text>`,
                `<text x="${right + 9}" y="${y}" dy="0.35em" class="site-progress-tick">${percent}%</text>`,
            );
        }
        const middle_y = (top + bottom) / 2;
        const axis_title = escape(__("Progress Percent"));
        svg.push(
            `<text transform="translate(20 ${middle_y}) rotate(-90)" text-anchor="middle" class="site-progress-axis-title">${axis_title}</text>`,
            `<text transform="translate(1080 ${middle_y}) rotate(90)" text-anchor="middle" class="site-progress-axis-title">${axis_title}</text>`,
            `<text x="550" y="349" text-anchor="middle" class="site-progress-axis-title">${escape(__("Gyalsung Project"))}</text>`,
        );
        progress.forEach((row, index) => {
            const center = left + step * (index + 0.5);
            svg.push(`<text x="${center}" y="322" text-anchor="middle" class="site-progress-project">${escape(row.project)}</text>`);
            series.forEach((dataset, series_index) => {
                const value = row[dataset.field];
                const height = (bottom - top) * Math.max(0, Math.min(100, value ?? 0)) / 100;
                const x = center + (series_index - 1) * bar_width;
                const y = bottom - height;
                const label = escape(formatProgressPercent(value));
                svg.push(`<g class="site-progress-bar" data-series="${dataset.field}" data-point-index="${index}">`,
                    `<title>${escape(row.project)} — ${escape(dataset.name)}: ${label}</title>`);
                if (value != null) {
                    svg.push(`<rect x="${x}" y="${y}" width="${bar_width}" height="${height}" fill="${dataset.color}" />`);
                }
                if (value > 100) {
                    const midpoint = x + bar_width / 2;
                    svg.push(`<path d="M ${midpoint - 4} ${top + 10} L ${midpoint} ${top + 4} L ${midpoint + 4} ${top + 10}" class="site-progress-overflow" />`);
                }
                svg.push(`<text x="${x + bar_width / 2}" y="${y - 7}" text-anchor="middle" class="site-progress-value">${label}</text>`, '</g>');
            });
        });
        svg.push('</svg>');
        this.element.innerHTML = svg.join("");
    }

    destroy() {
        this.element.innerHTML = "";
    }
}
