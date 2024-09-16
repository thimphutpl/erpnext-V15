// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Scholarship", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Scholarship', {
    refresh: function(frm) {
        // Trigger when the form is refreshed
        frm.fields_dict['course'].df.onchange = function() {
            let selected_course = frm.doc.course;
            let options = frm.fields_dict['course'].df.options.split("\n");

            if (!options.includes(selected_course)) {
                frappe.prompt([
                    {
                        label: 'New Course',
                        fieldname: 'new_course',
                        fieldtype: 'Data',
                        reqd: 1
                    }
                ],
                function(data) {
                    // Add the new course to the dropdown options
                    frm.fields_dict['course'].df.options += '\n' + data.new_course;
                    frm.set_value('course', data.new_course);
                    frm.refresh_field('course');
                },
                'Add New Course',
                'Add');
            }
        };
    }
});

