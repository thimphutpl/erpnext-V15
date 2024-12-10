// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Inventory Report"] = {
    "filters": [
        {
            fieldname: "report_type",
            label: __("Select Report"),
            fieldtype: "Select",
            options: [
                "Inventory Report",
                "Inventory Summary",
                "Non Moving Branch Wise",
                "Consumption Report"
            ],
            default: "Inventory Report",
            reqd: 1,
            on_change: function(query_report) {
                query_report.refresh();
            }
        },
        {
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			width: "80",
			options: "Company",
			default: frappe.defaults.get_default("company"),
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			width: "80",
			options: "Item Group",
			
		},
		{
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			width: "80",
			options: "Item",
			get_query: () => {
                let item_group = frappe.query_report.get_filter_value('item_group');
                if (item_group) {
                    return {
                        filters: {
                            item_group: item_group
                        }
                    };
                }
            }
			//Remarks [Old code]
			// get_query: function () {
			// 	return {
			// 		query: "erpnext.controllers.queries.item_query",
			// 	};
			// },
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			width: "80",
			options: "Warehouse",
			get_query: () => {
				let warehouse_type = frappe.query_report.get_filter_value("warehouse_type");
				let company = frappe.query_report.get_filter_value("company");

				return {
					filters: {
						...(warehouse_type && { warehouse_type }),
						...(company && { company }),
					},
				};
			},
		},
		{
			fieldname: "warehouse_type",
			label: __("Warehouse Type"),
			fieldtype: "Link",
			width: "80",
			options: "Warehouse Type",
		},
		{
			fieldname: "valuation_field_type",
			label: __("Valuation Field Type"),
			fieldtype: "Select",
			width: "80",
			options: "Currency\nFloat",
			default: "Currency",
		},
		{
			fieldname: "include_uom",
			label: __("Include UOM"),
			fieldtype: "Link",
			options: "UOM",
		},
		{
			fieldname: "show_variant_attributes",
			label: __("Show Variant Attributes"),
			fieldtype: "Check",
		},
		{
			fieldname: "show_stock_ageing_data",
			label: __("Show Stock Ageing Data"),
			fieldtype: "Check",
		},
		{
			fieldname: "ignore_closing_balance",
			label: __("Ignore Closing Balance"),
			fieldtype: "Check",
			default: 0,
		},
		{
			fieldname: "include_zero_stock_items",
			label: __("Include Zero Stock Items"),
			fieldtype: "Check",
			default: 0,
		},
    ],

    onload: function(report) {
        frappe.query_report.refresh();
    },

    get_data: function(filters) {
        const selected_report = filters.report_type;

        switch (selected_report) {
            case "Inventory Report":
                // return this.get_inventory_report_data();
                return this.StockBalanceReport();
            case "Inventory Summary":
                return this.get_inventory_summary_data();
            case "Non Moving Branch Wise":
                return this.get_non_moving_branch_data();
            case "Report 4":
                return this.get_report_4_data();
            default:
                // return this.get_inventory_report_data(); // Default to Report 1
                return this.StockBalanceReport(); // Default to Report 1
        }
    },

    // get_inventory_report_data: function() {
    //     return frappe.call({
    //         method: "erpnext.stock.report.inventory_report.inventory_report.get_inventory_report_data",
    //         callback: function(r) {
    //             return r.message;
    //         }
    //     });
    // },

    StockBalanceReport: function() {
        return frappe.call({
            method: "erpnext.stock.report.inventory_report.inventory_report.StockBalanceReport",
            callback: function(r) {
                return r.message;
            }
        });
    },

    get_inventory_summary_data: function() {
        return frappe.call({
            method: "erpnext.stock.report.inventory_report.inventory_report.get_inventory_summary_data",
            callback: function(r) {
                return r.message;
            }
        });
    },

    get_non_moving_branch_data: function() {
        return frappe.call({
            method: "erpnext.stock.report.inventory_report.inventory_report.get_non_moving_branch_data",
            callback: function(r) {
                return r.message;
            }
        });
    },

    get_report_4_data: function() {
        return frappe.call({
            method: "erpnext.stock.report.inventory_report.inventory_report.get_report_4_data",
            callback: function(r) {
                return r.message;
            }
        });
    },
    formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "out_qty" && data && data.out_qty > 0) {
			value = "<span style='color:red'>" + value + "</span>";
		} else if (column.fieldname == "in_qty" && data && data.in_qty > 0) {
			value = "<span style='color:green'>" + value + "</span>";
		}

		return value;
	},
};
erpnext.utils.add_inventory_dimensions("Stock Balance", 8);