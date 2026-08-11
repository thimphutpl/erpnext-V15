// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Budget Proposal", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Budget Proposal', {
	onload: function(frm) {
		frappe.call({
			"method": "get_consolidated_data",
			"doc": frm.doc,
			callback: function(r){
				if(r.message){
					render_budget_table(frm, r.message)
				}
			}
		})
		frm.set_query("account", "accounts", function() {
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0
				}
			};
		});
		
		frm.set_query("cost_center", "accounts", function() {
			return {
				filters: {
					company: frm.doc.company,
					disabled: 0,
				}
			};
		});

		frm.set_query("budget_activity", "accounts", function() {
			return {
				filters: {
					company: frm.doc.company
				}
			};
		});

		frm.set_query("budget_sub_activity", "accounts", function() {
			return {
				filters: {
					company: frm.doc.company
				}
			};
		});

		frm.set_query("broad_head", "accounts", function(doc, cdt, cdn) {
            return {
                filters: {
					"company": frm.doc.company,
					"is_group":1
                }
            };
        });
		
		
		// frm.set_query("budget_accounts", function() {
		// 	return {
		// 		filters: {
		// 			company: frm.doc.company,
		// 			is_group: 0
		// 		}
		// 	};
		// });

		frm.set_query("first_author_student", function() {
			return {
				filters: {
					student: frm.doc.student
				}
			};
		});
		frm.set_query("second_author_student", function() {
			return {
				filters: {
					student: frm.doc.student
				}
			};
		});
		frm.set_query("third_author_student", function() {
			return {
				filters: {
					student: frm.doc.student
				}
			};
		});

		frm.set_query("first_author_student", function() {
			return {
				filters: {
					student: frm.doc.student
				}
			};
		});
		frm.set_query("second_author_student", function() {
			return {
				filters: {
					student: frm.doc.student
				}
			};
		});
		frm.set_query("third_author_student", function() {
			return {
				filters: {
					student: frm.doc.student
				}
			};
		});

		frm.set_query("budget_sub_activities", function() {
			return {
				filters: {
					company: frm.doc.company
				}
			};
		});

		frm.set_query("budget_activities", function() {
			return {
				filters: {
					company: frm.doc.company
				}
			};
		});

		frm.set_query("monthly_distribution", function() {
			return {
				filters: {
					fiscal_year: frm.doc.fiscal_year
				}
			};
		});
		//erpnext.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);

		// Ensure any existing rows have approved_budget populated
        frm.doc.accounts.forEach(function(row) {
            if (row.initial_budget && (!row.approved_budget || row.approved_budget === 0)) {
                frappe.model.set_value(row.doctype, row.name, 'approved_budget', row.initial_budget);
            }
        });
	},

	refresh: function(frm) {
		frm.trigger("toggle_reqd_fields")
		frm.get_field("accounts").grid.grid_pagination.page_length = 150
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Budget Release'),()=> make_budget_release(frm),__('Create'));
		}
		frappe.call({
			"method": "get_consolidated_data",
			"doc": frm.doc,
			callback: function(r){
				if(r.message){
					render_budget_table(frm, r.message)
				}
			}
		})
	},
	setup: function(frm) {
		const createFilter = (options = {}) => {
			return () => {
				if (!frm.doc.company) {
					alert("Please select Company first");
				}
				return {
					filters: {
						company: frm.doc.company,
						disabled: 0,
						...options
					}
				};
			};
		};
		
		frm.set_query("cost_center", createFilter({}));
		frm.set_query("budget_accounts",createFilter({is_group:0}))
		frm.set_query("branch", createFilter({}));
	},

	cost_center: function(frm) {
        // Only proceed if:
        // 1. There are existing accounts with cost center
        // 2. We're actually changing the cost center (not setting it for first time)
        // 3. The new cost center is different from the existing one
        
        if (frm.doc.accounts && frm.doc.accounts.length > 0) {
            // Check if any row already has a cost center set
            let hasCostCenter = frm.doc.accounts.some(row => row.cost_center);
            
            // Check if we're actually changing the cost center
            let currentCostCenter = frm.doc.cost_center;
            let oldCostCenter = frm._previous_cost_center || '';
            
            // Only show confirmation if:
            // 1. There are rows with cost center already
            // 2. The new cost center is different from the old one
            // 3. It's not the first time setting cost center
            if (hasCostCenter && oldCostCenter && currentCostCenter !== oldCostCenter) {
                frappe.confirm(
                    __('Do you want to update the cost center for all existing rows in the accounts table?'),
                    function() {
                        // User confirmed - update all rows
                        let accounts = frm.doc.accounts;
                        for (let i = 0; i < accounts.length; i++) {
                            frappe.model.set_value(accounts[i].doctype, accounts[i].name, 'cost_center', frm.doc.cost_center);
                        }
                        frm.refresh_field('accounts');
                        
                        // Show success message
                        frappe.show_alert({
                            message: __('Cost center updated for all rows'),
                            indicator: 'green'
                        });
                    },
                    function() {
                        // User cancelled - revert the cost_center field
                        frm.set_value('cost_center', oldCostCenter);
                    }
                );
            }
        }
        
        // Store current value for next comparison
        frm._previous_cost_center = frm.doc.cost_center;
    },
    
    // Also handle the case when cost_center is set from child table
    cost_centers: function(frm) {
        // If cost_centers table is used, you might want to trigger update here too
        if (frm.doc.cost_centers && frm.doc.cost_centers.length > 0) {
            // Optionally update from the first cost_center in the table
            // let first_cost_center = frm.doc.cost_centers[0].cost_center;
            // if (first_cost_center && frm.doc.cost_center !== first_cost_center) {
            //     frm.set_value('cost_center', first_cost_center);
            // }
        }
    },

	budget_against: function(frm) {
		frm.trigger("set_null_value")
		frm.trigger("toggle_reqd_fields")
	},

	set_null_value: function(frm) {
		if(frm.doc.budget_against == 'Cost Center') {
			frm.set_value('project', null)
		} else {
			frm.set_value('cost_center', null)
		}
	},
	get_accounts: function(frm) {
		if(frm.doc.cost_center || frm.doc.project){
			return frappe.call({
				method: "get_accounts",
				doc: frm.doc,
				callback: function(r, rt) {
					frm.refresh_field("accounts");
					frm.refresh_fields();
				},
				freeze: true,
				freeze_message: "Loading Expense Accounts..... Please Wait"
			});
		}else{
			frappe.throw("Either Cost Center or Project is missing. ")
		}
	},
	cost_centers: function(frm){
		frappe.call({
			"method": "get_filtered_budget_data",
			"doc": frm.doc,
			callback: function(r){
				if(r.message){
					render_filtered_budget_table(frm, r.message)
				}
			}
		})
	},
	budget_activities: function(frm){
		frappe.call({
			"method": "get_filtered_budget_data",
			"doc": frm.doc,
			callback: function(r){
				if(r.message){
					render_filtered_budget_table(frm, r.message)
				}
			}
		})
	},
	budget_sub_activities: function(frm){
		frappe.call({
			"method": "get_filtered_budget_data",
			"doc": frm.doc,
			callback: function(r){
				if(r.message){
					render_filtered_budget_table(frm, r.message)
				}
			}
		})
	},
	source_of_funds: function(frm){
		frappe.call({
			"method": "get_filtered_budget_data",
			"doc": frm.doc,
			callback: function(r){
				if(r.message){
					render_filtered_budget_table(frm, r.message)
				}
			}
		})
	},
	budget_accounts: function(frm){
		frappe.call({
			"method": "get_filtered_budget_data",
			"doc": frm.doc,
			callback: function(r){
				if(r.message){
					render_filtered_budget_table(frm, r.message)
				}
			}
		})
	},
	get_budget_heads: function(frm) {
		if(frm.doc.cost_center && frm.doc.budget_activities && frm.doc.budget_sub_activities && frm.doc.source_of_funds){
			return frappe.call({
				method: "get_budget_heads",
				doc: frm.doc,
				callback: function(r, rt) {
					frappe.call({
						"method": "get_consolidated_data",
						"doc": frm.doc,
						callback: function(r){
							if(r.message){
								render_budget_table(frm, r.message)
							}
						}
					})
					frm.refresh_field("accounts");
					frm.refresh_fields();
				},
				freeze: true,
				freeze_message: "Inserting in Accounts Table..... Please Wait"
			});

		}else{
			frappe.throw("Either Cost Center or Project is missing. ")
		}
	},
	toggle_reqd_fields: function(frm) {
		// frm.toggle_reqd("cost_center", frm.doc.budget_against=="Cost Center");
		frm.toggle_reqd("project", frm.doc.budget_against=="Project");
	}
});

var render_budget_table = function(frm, datas) {
    let wrapper = $(frm.fields_dict["budget_details"].wrapper).empty();
    let i = 1;
    let data = [];

    datas.map(v => {
        let r = [
            i,
            frappe.format(v["budget_sub_activity"], { fieldtype: "Data" }),
            frappe.format(v["initial_budget"], { fieldtype: "Currency" }),
            frappe.format(v["source_of_fund_summary"], { fieldtype: "Data" })
        ];
        i = i + 1;
        data.push(r);
    });

    let columns = [
        { name: __("No."), editable: false, resizable: false, width: 60 },
        { name: __("Budget Sub Activity"), editable: false, resizable: true, width: 200 },
        { name: __("Initial Budget (Total)"), editable: false, resizable: true, width: 200 },
        { name: __("Source of Fund "), editable: false, resizable: true, width: 300 }
    ];

    let datatable = new frappe.DataTable(wrapper.get(0), {
        columns: columns,
        data: data,
        serialNoColumn: false,
        checkboxColumn: true,
        cellHeight: 35,
    });

    // keep your styling
    datatable.style.setStyle(`.dt-scrollable`, {
        "font-size": "0.75rem",
        "margin-bottom": "1rem",
        "margin-left": "0.35rem",
        "margin-right": "0.35rem",
    });
    datatable.style.setStyle(`.dt-header`, { "margin-left": "0.35rem", "margin-right": "0.35rem" });
    datatable.style.setStyle(`.dt-cell--header .dt-cell__content`, {
        color: "var(--gray-600)",
        "font-size": "var(--text-sm)",
    });
    datatable.style.setStyle(`.dt-cell`, { color: "var(--text-color)" });
    datatable.style.setStyle(`.dt-cell--col-1`, { "text-align": "center" });
    datatable.style.setStyle(`.dt-cell--col-3`, { "font-weight": "bold", "color": "#000" });
}

// var render_filtered_budget_table=function(frm, datas){
// 	if(datas.length > 0)
// 	{
// 		let wrapper = $(frm.fields_dict["filtered_budget_data"].wrapper).empty();
// 		let i = 1
// 		let data = [];

// 		datas.map(v=>{
// 				let r=[
// 					i,
// 					frappe.format(v["cost_center"], { fieldtype: "Data" }),
// 					frappe.format(v["budget_activity"], { fieldtype: "Data" }),
// 					frappe.format(v["budget_sub_activity"], { fieldtype: "Data" }),
// 					frappe.format(v["account"], { fieldtype: "Data" }),
// 					frappe.format(v["approved_budget"], { fieldtype: "Currency" }),
// 				]
// 				i=i+1
// 				data.push(r)
// 		})
		
		
		
// 		let columns = [
// 			{ name: __("No."), editable: false, resizable: false, format: (value) => value, width: 60 },
// 			{ name: __("Cost Center"), editable: false, resizable: true, width: 200 },
// 			{ name: __("Budget Activity"), editable: false, resizable: true, width: 100 },
// 			{ name: __("Budget Sub Activity"), editable: false, resizable: true, width: 100 },
// 			{ name: __("Account"), editable: false, resizable: true, width: 300 },
// 			{ name: __("Initial Budget"), editable: false, resizable: true, width: 200 },
// 		];
		

// 		let datatable = new frappe.DataTable(wrapper.get(0), {
// 			columns: columns,
// 			data: data,
// 			serialNoColumn: false,
// 			checkboxColumn: true,
// 			cellHeight: 35,
// 		});

// 		datatable.style.setStyle(`.dt-scrollable`, {
// 			"font-size": "0.75rem",
// 			"margin-bottom": "1rem",
// 			"margin-left": "0.35rem",
// 			"margin-right": "0.35rem",
// 		});
// 		datatable.style.setStyle(`.dt-header`, { "margin-left": "0.35rem", "margin-right": "0.35rem" });
// 		datatable.style.setStyle(`.dt-cell--header .dt-cell__content`, {
// 			color: "var(--gray-600)",
// 			"font-size": "var(--text-sm)",
// 		});
// 		datatable.style.setStyle(`.dt-cell`, { color: "var(--text-color)" });
// 		datatable.style.setStyle(`.dt-cell--col-1`, { "text-align": "center" });
// 		datatable.style.setStyle(`.dt-cell--col-6`, { "font-weight": 600 });
// 	}
// 	else{
// 		let wrapper = $(frm.fields_dict["filtered_budget_data"].wrapper).empty();
// 	}
// }
var make_budget_release = function(frm, remaining, remaining_installment){
	var d = new frappe.ui.Dialog({
		title: __('Create Installment Journal Entries'),
		fields: [
			{
				"label": "Month",
				"fieldname": "month",
				"fieldtype": "Select",
				"options": ["July", "August", "September", "October", "November", "December", "January", "February", "March", "April", "May", "June"],
				"reqd": 1,
			},
		],
		primary_action: function() {
			var data = d.get_values();
			frappe.model.open_mapped_doc({
				method: "erpnext.budget.doctype.budget_proposal.budget_proposal.make_budget_release",
				frm: frm,
				args: {"month": data.month},
			})
		},
		primary_action_label: __('Create')
	});
	d.show();
}

frappe.ui.form.on("Budget Proposal Account", {	
	"january": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"february": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"march": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"april": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"may": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"june": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"july": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"august": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"september": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"october": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"november": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	"december": function(frm, cdt, cdn) {
		set_initial_budget(frm, cdt, cdn);
	},
	initial_budget: function(frm, cdt, cdn){
		frappe.call({
			"method": "get_consolidated_data",
			"doc": frm.doc,
			callback: function(r){
				if(r.message){
					render_budget_table(frm, r.message)
				}
			}
		})
		frappe.call({
			"method": "get_filtered_budget_data",
			"doc": frm.doc,
			callback: function(r){
				if(r.message){
					render_filtered_budget_table(frm, r.message)
				}
			}
		})
	},
	initial_budget: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        // If approved_budget is empty or 0, auto-fill with initial_budget
        if (row.initial_budget && (!row.approved_budget || row.approved_budget === 0)) {
            frappe.model.set_value(cdt, cdn, 'approved_budget', row.initial_budget);
        }
    },
    
    approved_budget: function(frm, cdt, cdn) {
        // Optional: Track that user manually changed approved_budget
        let row = locals[cdt][cdn];
        if (row.approved_budget && row.initial_budget && row.approved_budget !== row.initial_budget) {
            // User manually changed approved_budget - you can add a flag if needed
            // row.approved_budget_manually_changed = 1;
        }
    }
}); 

function set_initial_budget(frm, cdt, cdn){
	frappe.call({
		method:"set_initial_budget",
		doc: frm.doc,
		callback: function(r) {
			frm.refresh_field('initial_budget');
			frm.refresh_field('budget_amount');
			frm.refresh_fields('accounts');
		}
	})
}