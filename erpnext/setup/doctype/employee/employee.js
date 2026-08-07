// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.setup");
erpnext.setup.EmployeeController = class EmployeeController extends frappe.ui.form.Controller {
    setup() {
        this.frm.fields_dict.user_id.get_query = function (doc, cdt, cdn) {
            return {
                query: "frappe.core.doctype.user.user.user_query",
                filters: { ignore_user_type: 1 },
            };
        };
        this.frm.fields_dict.reports_to.get_query = function (doc, cdt, cdn) {
            return { query: "erpnext.controllers.queries.employee_query" };
        };
    }

    refresh() {
        erpnext.toggle_naming_series();
    }
};

frappe.ui.form.on("Employee", {
    onload: function (frm) {
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
        frm.set_query("grade", function () {
            return {
                "filters": {
                    "company": frm.doc.company,
                }
            }
        });
        frm.set_query("branch", function () {
            return {
                "filters": {
                    "company": frm.doc.company,
                    "disabled": 0,
                }
            }
        });
        frm.set_query("cost_center", function () {
            return {
                "filters": {
                    "company": frm.doc.company,
                    "disabled": 0,
                    "is_group": 0,
                }
            }
        });
        frm.set_query("employee_group", function () {
            return {
                "filters": {
                    "company": frm.doc.company,
                }
            }
        });
        frm.set_query("designation", function () {
            return {
                "filters": {
                    "company": frm.doc.company,
                }
            }
        })
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
    },

    employee_group: function (frm) {

        if (!frm.doc.employee_group || !frm.doc.grade) {
            return;
        }

        frappe.call({
            method: "erpnext.setup.doctype.employee.employee.check_grade_in_employee_group",
            args: {
                employee_group: frm.doc.employee_group,
                grade: frm.doc.grade
            },
            callback: function (r) {

                if (r.message === false) {
                    frappe.msgprint({
                        title: __("Invalid Employee Group"),
                        message: __(
                            "Grade {0} is not available under Employee Group {1}",
                            [
                                frm.doc.grade,
                                frm.doc.employee_group
                            ]
                        ),
                        indicator: "red"
                    });

                    frm.set_value("employee_group", null);
                }

            }
        });
    },
    // grade: function (frm) {

    //     if (!frm.doc.grade) {
    //         frm.set_query("employee_group", function () {
    //             return {};
    //         });
    //         return;
    //     }

    //     frappe.call({
    //         method: "erpnext.setup.doctype.employee.employee.get_employee_group_base_grade",
    //         args: {
    //             grade: frm.doc.grade,
    //             company: frm.doc.company
    //         },
    //         callback: function (res) {

    //             let groups = [];

    //             if (res.message && res.message.length > 0) {
    //                 groups = res.message.map(d => d.name);
    //             }

    //             frm.set_query("employee_group", function () {
    //                 return {
    //                     filters: {
    //                         name: ["in", groups]
    //                     }
    //                 };
    //             });

    //         }
    //     });

    // },
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
        var prefered_email_fieldname = frappe.model.scrub(frm.doc.prefered_contact_email) || "user_id";
        frm.set_value("prefered_email", frm.fields_dict[prefered_email_fieldname].value);
    },

    status: function (frm) {
        return frm.call({
            method: "deactivate_sales_person",
            args: {
                employee: frm.doc.employee,
                status: frm.doc.status,
            },
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
                email: frm.doc.prefered_email,
            },
            freeze: true,
            freeze_message: __("Creating User..."),
            callback: function (r) {
                frm.reload_doc();
            },
        });
    },
});

cur_frm.cscript = new erpnext.setup.EmployeeController({
    frm: cur_frm,
});

frappe.tour["Employee"] = [
    {
        fieldname: "first_name",
        title: "First Name",
        description: __(
            "Enter First and Last name of Employee, based on Which Full Name will be updated. IN transactions, it will be Full Name which will be fetched."
        ),
    },
    {
        fieldname: "company",
        title: "Company",
        description: __("Select a Company this Employee belongs to."),
    },
    {
        fieldname: "date_of_birth",
        title: "Date of Birth",
        description: __(
            "Select Date of Birth. This will validate Employees age and prevent hiring of under-age staff."
        ),
    },
    {
        fieldname: "date_of_joining",
        title: "Date of Joining",
        description: __(
            "Select Date of joining. It will have impact on the first salary calculation, Leave allocation on pro-rata bases."
        ),
    },
    {
        fieldname: "reports_to",
        title: "Reports To",
        description: __(
            "Here, you can select a senior of this Employee. Based on this, Organization Chart will be populated."
        ),
    },
];
