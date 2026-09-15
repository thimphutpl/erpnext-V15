// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.query_reports["Site Budget Consumption"] = {
// 	"filters": [

// 	]
// };


frappe.query_reports["Site Budget Consumption"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: "GYALSUNG INFRA",
            reqd: 1,
        },

        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: "2020-01-01",
            reqd: 1,
            read_only: 1,
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1,
            read_only: 1,
        }
    ],

    get_chart_data(columns, result) {
        const sites = result.filter(row => row.cost_center && !row.is_total_row);
        return {
            type: "bar",
            colors: ["#60A5FA", "#FBBF24"],
            fieldtype: "Currency",
            valuesOverPoints: 1,
            barOptions: { stacked: false, spaceRatio: 0.35 },
            data: {
                labels: sites.map(row => row.cost_center),
                datasets: [
                    { name: __("Estimated Budget"), values: sites.map(row => row.estimated_budget) },
                    { name: __("Total Expenses"), values: sites.map(row => row.budget_consumed) },
                ],
            },
        };
    },

    onload(report) {
        // SVG labels stay attached to each bar through animation and resizing.
        // Reapply compact formatting whenever the chart recreates its SVG.
        if (report.site_budget_label_observer) report.site_budget_label_observer.disconnect();
        const format_value = value => {
            const amount = Math.abs(value);
            for (const [scale, suffix] of [[1e12, "T"], [1e9, "B"], [1e6, "M"], [1e3, "K"]]) {
                if (amount >= scale) return (value / scale).toFixed(2) + suffix;
            }
            return value.toFixed(2);
        };
        report.site_budget_label_observer = new MutationObserver(() => {
            if (report.report_name !== "Site Budget Consumption") return;
            report.$chart[0].querySelectorAll(".data-point-value").forEach(label => {
                const value = Number(label.textContent);
                if (!label.textContent || !Number.isFinite(value)) return;
                const text = format_value(value);
                if (label.textContent !== text) label.textContent = text;
            });
        });
        report.site_budget_label_observer.observe(report.$chart[0], { childList: true, subtree: true });
    },
};
