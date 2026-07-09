frappe.treeview_settings["Miscellaneous Account"] = {
	breadcrumb: "Miscellaneous",
	title: __("Chart Of Accounts - Miscellaneous"),
	get_tree_root: false,

	filters: [
		{
			fieldname: "company",
			fieldtype: "Select",
			options: erpnext.utils.get_tree_options("company"),
			label: __("Company"),
			default: erpnext.utils.get_tree_default("company"),

			on_change: function () {
				let me = frappe.treeview_settings["Miscellaneous Account"].treeview;
				let company = me.page.fields_dict.company.get_value();

				frappe.call({
					method: "erpnext.accounts.doctype.account.account.get_root_company",
					args: {
						company: company
					},
					callback: function (r) {
						if (r.message) {
							let root_company = r.message.length ? r.message[0] : "";
							me.page.fields_dict.root_company.set_value(root_company);
						}
					}
				});
			}
		},

		{
			fieldname: "root_company",
			fieldtype: "Data",
			label: __("Root Company"),
			hidden: true,
			disable_onchange: true
		}
	],

	root_label: "Accounts",

	get_tree_nodes: "erpnext.miscellaneous.utils.get_children",
	add_tree_node: "erpnext.miscellaneous.utils.add_ac",

	fields: [
		{
			fieldtype: "Data",
			fieldname: "sws_account_name",
			label: __("New Account Name"),
			reqd: true
		},

		{
			fieldtype: "Data",
			fieldname: "account_number",
			label: __("Account Number")
		},

		{
			fieldtype: "Check",
			fieldname: "is_group",
			label: __("Is Group")
		},

		{
			fieldtype: "Select",
			fieldname: "root_type",
			label: __("Root Type"),
			options: ["Asset", "Liability", "Equity", "Income", "Expense"].join("\n"),
			depends_on: "eval:doc.is_group && !doc.parent_miscellaneous_account"
		},

		{
			fieldtype: "Select",
			fieldname: "account_type",
			label: __("Account Type"),

			options: frappe.get_meta("Miscellaneous Account")
				.fields.filter(d => d.fieldname == "account_type")[0].options
		}
	],

	ignore_fields: ["parent_miscellaneous_account"],

	extend_toolbar: true
};