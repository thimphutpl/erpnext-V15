// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.setup");
erpnext.setup.EmployeeController = class EmployeeController extends frappe.ui.form.Controller {
	setup() {
		this.frm.fields_dict.user_id.get_query = function (doc, cdt, cdn) {
			return {
				query: "frappe.core.doctype.user.user.user_query",
				filters: { ignore_user_type: 1 }
			}
		}
		this.frm.fields_dict.reports_to.get_query = function (doc, cdt, cdn) {
			return { query: "erpnext.controllers.queries.employee_query" }
		}
	}

	// refresh() {
		// erpnext.toggle_naming_series();
	// }

	salutation() {
		if (this.frm.doc.salutation) {
			this.frm.set_value("gender", {
				"Mr": "Male",
				"Ms": "Female"
			}[this.frm.doc.salutation]);
		}
	}
};

frappe.ui.form.on("Employee", {
	onload: function (frm) {

		frm.set_df_property('naming_series', 'hidden', 1);

		frm.set_query("department", function () {
			return {
				"filters": {
					"company": frm.doc.company,
					"disabled": 0,
					"is_division": 0,
					"is_section": 0,
					"is_unit": 0
				}
			};
		});
		frm.set_query("division", function () {
			return {
				"filters": {
					"company": frm.doc.company,
					"disabled": 0,
					"is_division": 1,
					"is_section": 0,
					"is_unit": 0
				}
			};
		});
		frm.set_query("section", function () {
			return {
				"filters": {
					"parent_department": frm.doc.division,
					"company": frm.doc.company,
					"disabled": 0,
					"is_division": 0,
					"is_section": 1
				}
			};
		});
		frm.set_query("unit", function () {
			if (!frm.doc.section) {
				return {
					"filters": {
						"parent_department": frm.doc.division,
						"company": frm.doc.company,
						"disabled": 0,
						"is_division": 0,
						"is_unit": 1,
						"is_section": 0
					}
				};
			} else {
				return {
					"filters": {
						"parent_department": frm.doc.section,
						"company": frm.doc.company,
						"disabled": 0,
						"is_division": 0,
						"is_unit": 1,
						"is_section": 0
					}
				};
			}
		});
		frappe.call({
			method: "check_logged_in_user_role_to_edit_data",
			doc:frm.doc,
			callback: function(r){  
				const lock = r.message ? 1 : 0;
				console.log(r.message)
				frm.set_df_property("status", "read_only", lock);
				frm.set_df_property("employee","read_only", lock)
				frm.set_df_property("naming_series","read_only", lock)
				frm.set_df_property("gender","read_only", lock)
				frm.set_df_property("salutation","read_only", lock)
				frm.set_df_property("first_name","read_only", lock)
				frm.set_df_property("date_of_joining","read_only", lock)
				frm.set_df_property("date_of_birth","read_only", lock)
				frm.set_df_property("middle_name","read_only", lock)
				frm.set_df_property("last_name","read_only", lock)
				frm.set_df_property("employee_name","read_only", lock)
				frm.set_df_property("old_id","read_only", lock)
				frm.set_df_property("employee_name","read_only", lock)
				frm.set_df_property("user_id","read_only", lock)
				frm.set_df_property("unsubscribed","read_only", lock)
				frm.set_df_property("contract_summary","read_only", lock)
				frm.set_df_property("separation_benefits","read_only", lock)
				frm.set_df_property("resignation_letter_date","read_only", lock)
				frm.set_df_property("held_on","read_only", lock)
				frm.set_df_property("leave_encashed","read_only", lock)
				frm.set_df_property("relieving_date","read_only", lock)
				frm.set_df_property("new_workplace","read_only", lock)
				frm.set_df_property("encashment_date","read_only", lock)
				frm.set_df_property("reason_for_leaving","read_only", lock)
				frm.set_df_property("feedback","read_only", lock)
				frm.set_df_property("attendance_device_id","read_only", lock)
				frm.set_df_property("holiday_list","read_only", lock)
				frm.set_df_property("leave_block_list","read_only", lock)
				frm.set_df_property("default_shift","read_only", lock)
				frm.set_df_property("expense_approver","read_only", lock)
				frm.set_df_property("leave_approver","read_only", lock)
				frm.set_df_property("shift_request_approver","read_only", lock)
				lock_section(frm, "employment_details_section", lock);
				lock_section(frm, "leave_and_expense_claim_section", lock);
				lock_section(frm, "erpnext_user", lock);
				lock_section(frm, "company_details_section", lock);
				lock_section(frm, "joining_details", lock);
				lock_section(frm, "salary_details", lock);
				lock_section(frm, "bank_details", lock);
				lock_section(frm, "pms_records_section", lock);
				lock_section(frm, "contract_summary", lock);					

			}
		})
	},

	

	refresh: function (frm) {
		frm.set_query("division", function () {
			return {
				"filters": {
					"company": frm.doc.company,
					"disabled": 0,
					"is_division": 1,
					"is_section": 0,
					"is_unit": 0
				}
			};
		});
	},
	leave_block_list: function (frm) {
		// add_in_blocklist
		frappe.call({
			method: "erpnext.setup.doctype.employee.employee.add_in_blocklist",
			args: {
				emp: frm.doc.name,
				block_list: frm.doc.leave_block_list
			},
			callback: function (r) {
				// refresh_fields()
			}
		})
	},
	prefered_contact_email: function (frm) {
		frm.events.update_contact(frm);
	},

	personal_email: function (frm) {
		frm.events.update_contact(frm);
	},

	company_email: function (frm) {
		frm.events.update_contact(frm);
	},

	user_id: function (frm) {
		frm.events.update_contact(frm);
	},

	update_contact: function (frm) {
		var prefered_email_fieldname = frappe.model.scrub(frm.doc.prefered_contact_email) || 'user_id';
		frm.set_value("prefered_email",
			frm.fields_dict[prefered_email_fieldname].value);
	},

	status: function (frm) {
		return frm.call({
			method: "deactivate_sales_person",
			args: {
				employee: frm.doc.employee,
				status: frm.doc.status
			}
		});
	},

	create_user: function (frm) {
		if (!frm.doc.prefered_email) {
			frappe.throw(__("Please enter Preferred Contact Email"));
		}
		frappe.call({
			method: "erpnext.setup.doctype.employee.employee.create_user",
			args: {
				employee: frm.doc.name,
				email: frm.doc.prefered_email
			},
			callback: function (r) {
				frm.set_value("user_id", r.message);
			}
		});
	}
});

cur_frm.cscript = new erpnext.setup.EmployeeController({
	frm: cur_frm
});
cur_frm.fields_dict['gewog'].get_query = function(doc, dt, dn) {
	return {
			filters:{"dzongkhag": doc.dzongkhag}
	}
}

cur_frm.fields_dict['village'].get_query = function(doc, dt, dn) {
	return {
			filters:{"gewog": doc.gewog}
	}
}

frappe.tour['Employee'] = [
	{
		fieldname: "first_name",
		title: "First Name",
		description: __("Enter First and Last name of Employee, based on Which Full Name will be updated. IN transactions, it will be Full Name which will be fetched.")
	},
	{
		fieldname: "company",
		title: "Company",
		description: __("Select a Company this Employee belongs to.")
	},
	{
		fieldname: "date_of_birth",
		title: "Date of Birth",
		description: __("Select Date of Birth. This will validate Employees age and prevent hiring of under-age staff.")
	},
	{
		fieldname: "date_of_joining",
		title: "Date of Joining",
		description: __("Select Date of joining. It will have impact on the first salary calculation, Leave allocation on pro-rata bases.")
	},
	{
		fieldname: "reports_to",
		title: "Reports To",
		description: __("Here, you can select a senior of this Employee. Based on this, Organization Chart will be populated.")
	},
];

// var toggle_remarks_display = function(frm, ){
// 	frm.set_df_property("supervisor_remarks","read_only",supervisor);
// 	frm.set_df_property("supervisor_clearance","read_only",supervisor);
// 	frm.set_df_property("finance_head_remarks","read_only",fd);
// 	frm.set_df_property("finance_clearance","read_only",fd);
// 	frm.set_df_property("erp_remarks","read_only",erp);
// 	frm.set_df_property("erp_clearance","read_only",erp);
// 	frm.set_df_property("hr_remarks","read_only",hra);
// 	frm.set_df_property("hra_clearance","read_only",hra);
// 	frm.set_df_property("adm_remarks","read_only",adm);
// 	frm.set_df_property("adm_clearance","read_only",adm);
// }

// Lock/unlock all fields inside a section (by Section Break fieldname)
function lock_section(frm, section_fieldname, read_only = 1) {
  const RO = !!read_only;
  const layoutOnly = new Set(["Section Break", "Column Break", "Tab Break", "HTML"]);
  const fields = frm.meta.fields;

  let i = fields.findIndex(
    df => df.fieldtype === "Section Break" && df.fieldname === section_fieldname
  );
  if (i === -1) return;

  for (i = i + 1; i < fields.length; i++) {
    const df = fields[i];
    if (df.fieldtype === "Section Break") break;
    if (layoutOnly.has(df.fieldtype)) continue;

    if (df.fieldtype === "Table") {
      frm.set_df_property(df.fieldname, "read_only", RO);
      const grid = frm.get_field(df.fieldname)?.grid;
      if (grid) {
        grid.set_read_only(RO);
        
        const child_meta = frappe.get_meta(df.options);
        child_meta.fields.forEach(cdf => {
          if (!layoutOnly.has(cdf.fieldtype)) {
            grid.update_docfield_property(cdf.fieldname, "read_only", RO);
          }
        });
      }
      frm.refresh_field(df.fieldname);
    } else {
      // Normal field
      frm.set_df_property(df.fieldname, "read_only", RO);
      const docfield = frm.get_docfield(df.fieldname);
      if (docfield?.read_only_depends_on) {
        frm.set_df_property(df.fieldname, "read_only_depends_on", null);
      }
      frm.toggle_enable(df.fieldname, !RO);
      frm.refresh_field(df.fieldname);
    }
  }

  frm.refresh_fields();
}

