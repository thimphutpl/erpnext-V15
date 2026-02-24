// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.ui.form.on("Customer Revenue Target", {
	refresh(frm) {
        	if (frm.doc.docstatus == 1){
			frm.add_custom_button(__("Achievement Report"), function(){
			var fy = frappe.model.get_doc("Fiscal Year", frm.doc.fiscal_year);
			var y_start_date = y_end_date = "";
				
			if (fy) {
				y_start_date = fy.year_start_date;
				y_end_date   = fy.year_end_date;
			}
				
			frappe.route_options = {
				fiscal_year: frm.doc.fiscal_year,
				from_date: y_start_date,
				to_date: y_end_date
			};
			frappe.set_route("query-report", "Customer Revenue Target");
				}
			);
			
		}
      

	},
    branch: function(frm){
		frm.clear_table("revenue_target_customer");
		frm.refresh_field("revenue_target_customer");
	},
    get_customers: function(frm){
        return frappe.call({
            method: "get_customer",
            doc:frm.doc,
            callback: function(r, rt){
                frm.refresh_field("revenue_target_customer");
                frm.refresh_fields();
            },
            freeze: true,
            freeze_message: "Loading..... Please Wait"
        });
    },
});
frappe.ui.form.on('Revenue Target Customer',{
	"january": function(frm, cdt, cdn) {
		set_initial_revenue_target(frm, cdt, cdn);
	},
	"february": function(frm, cdt, cdn) {
		set_initial_revenue_target(frm, cdt, cdn);
	},
	"march": function(frm, cdt, cdn) {
		set_initial_revenue_target(frm, cdt, cdn);
	},
	"april": function(frm, cdt, cdn) {
		set_initial_revenue_target(frm, cdt, cdn);
	},
	"may": function(frm, cdt, cdn) {
		set_initial_revenue_target(frm, cdt, cdn);
	},
	"june": function(frm, cdt, cdn) {
		set_initial_revenue_target(frm, cdt, cdn);
	},
	"july": function(frm, cdt, cdn) {
		set_initial_revenue_target(frm, cdt, cdn);
	},
	"august": function(frm, cdt, cdn) {
		set_initial_revenue_target(frm, cdt, cdn);
	},
	"september": function(frm, cdt, cdn) {
		set_initial_revenue_target(frm, cdt, cdn);
	},
	"october": function(frm, cdt, cdn) {
		set_initial_revenue_target(frm, cdt, cdn);
	},
	"november": function(frm, cdt, cdn) {
		set_initial_revenue_target(frm, cdt, cdn);
	},
	"december": function(frm, cdt, cdn) {
		set_initial_revenue_target(frm, cdt, cdn);
	},
});

var set_initial_revenue_target=(frm,cdt,cdn)=>{
	frappe.call({
		method:"set_initial_revenue_target",
		doc: frm.doc,
		callback: function(r) {
			frm.refresh_field('target_amount');
			frm.refresh_field('tot_target_amount');
			frm.refresh_fields('revenue_target_customer');
		}
	})
}
