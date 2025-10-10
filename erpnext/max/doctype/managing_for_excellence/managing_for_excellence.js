// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Managing for Excellence", {
    onload:function(frm){
        toggle_child_fields(frm);
        // toggle_file_area_mandatory(frm);
        restrict_child_fields_on_refresh(frm)
    },
	refresh: function(frm) {
        if (frm.doc.workflow_state ==="Evaluation Verified"){
            frm.set_df_property('items', 'read_only', 1);
        }
        toggle_child_fields(frm);
        // toggle_file_area_mandatory(frm);
        restrict_child_fields_on_refresh(frm)
        
    },

    workflow_state: function(frm) {
        toggle_child_fields(frm);
        restrict_child_fields_on_refresh(frm)
    },
    pms_group: function(frm) {
        toggle_file_area_mandatory(frm);
    },

    // Helper function to toggle child table field
    

  

    fetch_competency: function(frm){
        if (!frm.doc.pms_group) return;
        frappe.call({
            method:"erpnext.max.doctype.managing_for_excellence.managing_for_excellence.get_max_competency",
            args: {
                    name: frm.doc.name,
                    pms_group:frm.doc.pms_group
                },
                callback: function(r) {
                    if (r.message) {
                        // Clear existing rows first (optional)
                        frm.clear_table("competency_item");
    
                        // r.message should be an array of objects
                        r.message.forEach(function(row) {
                            let child = frm.add_child("competency_item");
                            child.competency = row.competency_item;
                            child.description = row.description;
                        });
    
                        // Refresh the table to show the new data
                        frm.refresh_field("competency_item");
                    }
                }
        })
    }
});


// function toggle_child_fields(frm) {
//     // condition: enable & show only when workflow_state == "Plan Verified"
//     let is_enabled = (frm.doc.workflow_state === "Plan Verified");

//     frm.fields_dict["items"].grid.toggle_display("self_rating", is_enabled);
//     frm.fields_dict["items"].grid.toggle_enable("self_rating", is_enabled);

//     frm.fields_dict["items"].grid.toggle_display("supervisor_rating", is_enabled);
//     frm.fields_dict["items"].grid.toggle_enable("supervisor_rating", is_enabled);
// }

// function toggle_child_fields(frm) {
//     frm.fields_dict.items.grid.wrapper.find('.grid-row').each(function(index, row_wrapper) {
//         const row = frm.doc.items[index];

//         // Self Rating: editable only when workflow_state is "Plan Verified"
//         frm.fields_dict.items.grid.toggle_enable('self_rating', frm.doc.workflow_state === "Plan Verified", row);

//         // Supervisor Rating: editable only when workflow_state is "Evaluation Submitted"
//         frm.fields_dict.items.grid.toggle_enable('supervisor_rating', frm.doc.workflow_state === "Evaluation Submitted", row);
//     });
//     frm.fields_dict.items.grid.wrapper.find('.grid-row').each(function(index, row_wrapper) {
//         const row = frm.doc.competency_item[index];

//         // Self Rating: editable only when workflow_state is "Plan Verified"
//         frm.fields_dict.items.grid.toggle_enable('self_rating', frm.doc.workflow_state === "Plan Verified", row);

//         // Supervisor Rating: editable only when workflow_state is "Evaluation Submitted"
//         frm.fields_dict.items.grid.toggle_enable('supervisor_rating', frm.doc.workflow_state === "Evaluation Submitted", row);
//     });
// }
function toggle_child_fields(frm) {

    const is_new = frm.is_new(); // true if opening a new doc

    // -------- items table ----------
    frm.fields_dict.items.grid.wrapper.find('.grid-row').each(function(index, row_wrapper) {
        const row = frm.doc.items[index];

        // if (is_new) {
        //     // Make both fields readonly for new document
        //     frm.fields_dict.items.grid.toggle_enable('self_rating', false, row);
        //     frm.fields_dict.items.grid.toggle_enable('supervisor_rating', false, row);
        // } else {
            // Enable/disable based on workflow_state
            frm.fields_dict.items.grid.toggle_enable('self_rating', frm.doc.workflow_state === "Plan Verified", row);
            frm.fields_dict.items.grid.toggle_enable('supervisor_rating', frm.doc.workflow_state === "Evaluation Submitted", row);
        // }
    });

    // -------- competency_item table ----------
    if (frm.fields_dict.competency_item) {  
        frm.fields_dict.competency_item.grid.wrapper.find('.grid-row').each(function(index, row_wrapper) {
            const row = frm.doc.competency_item[index];

            if (is_new) {
                frm.fields_dict.competency_item.grid.toggle_enable('self_rating', false, row);
                frm.fields_dict.competency_item.grid.toggle_enable('supervisor_rating', false, row);
            } else {
                frm.fields_dict.competency_item.grid.toggle_enable('self_rating', frm.doc.workflow_state === "Plan Verified", row);
                frm.fields_dict.competency_item.grid.toggle_enable('supervisor_rating', frm.doc.workflow_state === "Evaluation Submitted", row);
             }
        });
    }
}

function toggle_file_area_mandatory(frm) {
    if (frm.doc.pms_group) {
        frappe.call({
            method: "erpnext.max.doctype.managing_for_excellence.managing_for_excellence.get_target_fields",
            args: {
                pms_group: frm.doc.pms_group
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    console.log('hih');

                    const required_activity = r.message[0].required_activity;
                    const required_area = r.message[0].required_area;
                    const required_baselined = r.message[0].required_baselined;
                    const required_key_result_areas = r.message[0].required_key_result_areas;

                    // Use grid_rows to access child doc objects
                    frm.fields_dict.items.grid.grid_rows.forEach(row_wrapper => {
                        const row = row_wrapper.doc;

                        row.__unsaved = true; // mark as changed

                        frm.fields_dict.items.grid.toggle_reqd('area', required_area, row);
                        frm.fields_dict.items.grid.toggle_reqd('key_result_areas', required_key_result_areas, row);
                        frm.fields_dict.items.grid.toggle_reqd('baseline', required_baselined, row);
                        frm.fields_dict.items.grid.toggle_reqd('activity', required_activity, row);

                        frm.fields_dict.items.grid.toggle_display('area', required_area);
                        frm.fields_dict.items.grid.toggle_display('key_result_areas', required_key_result_areas);
                        frm.fields_dict.items.grid.toggle_display('baseline', required_baselined);
                        frm.fields_dict.items.grid.toggle_display('activity', required_activity);

                                            
                     });

                    // Refresh to show red asterisks
                    frm.refresh_field('items');
                }
            }
        });
    }
}
    
    // const is_operation = frm.doc.pms_group === "Executives and P1M";

    // // -------- items table ----------
    // frm.fields_dict.items.grid.wrapper.find('.grid-row').each(function(index, row_wrapper) {
    //     const row = frm.doc.items[index];
    //     if (row) {
    //         row.__unsaved = true; // mark row as changed
    //         frm.fields_dict.items.grid.toggle_reqd('area', is_operation, row);
    //         frm.fields_dict.items.grid.toggle_reqd('key_result_areas', true, row);
    //         frm.fields_dict.items.grid.toggle_reqd('required_baselined', true, row);
    //     }

        
    
    // })\
    // ;}

    // frappe.ui.form.on('MAX item', {
    //     competency_item_add: function(frm, cdt, cdn) {
    //         const row = locals[cdt][cdn];
    //         toggle_row_fields(frm, row);
    //     }
    // });

    // function toggle_row_fields(frm, row) {
    //     const is_new = frm.is_new();
    
    //     if (is_new) {
    //         row.self_rating_read_only = 1;
    //         row.supervisor_rating_read_only = 1;
    //     } else {
    //         row.self_rating_read_only = (frm.doc.workflow_state !== "Plan Verified");
    //         row.supervisor_rating_read_only = (frm.doc.workflow_state !== "Evaluation Submitted");
    //     }
    
    //     frm.refresh_field('items');
    // }

    // This fun should be  inside the parent custom script
// frappe.ui.form.on("MAX item",{
//     // items is the child field name 
//     items_add: function(frm){
//     console.log("OK");
//     }})

//---------------------------------------------------------------->
// frappe.ui.form.on("MAX item", {
//     items_add: function(frm, cdt, cdn) {
//         // Make area field mandatory
        
//         frm.fields_dict.items.grid.update_docfield_property(
//             'area',  // field name
//             'reqd',  // property (required)
//             1,       // value (true)
//             cdn      // child row name
//         );
        
//         console.log("Area field made mandatory for new row");
//     }
// });



frappe.ui.form.on("MAX item", {
    items_add: function(frm, cdt, cdn) {
        // Make area field mandatory
        frappe.call({
            method: "erpnext.max.doctype.managing_for_excellence.managing_for_excellence.get_target_fields",
            args: {
                pms_group: frm.doc.pms_group
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    console.log('API Response received');

                    const required_activity = r.message[0].required_activity;
                    const required_area = r.message[0].required_area;
                    const required_baselined = r.message[0].required_baselined;
                    const required_key_result_areas = r.message[0].required_key_result_areas;

                    // Apply to the newly added row
                    const row = frappe.get_doc(cdt, cdn);
                    const grid_row = frm.fields_dict.items.grid.grid_rows_by_docname[cdn];

                    // Toggle required property
                    frm.fields_dict.items.grid.update_docfield_property(
                        'area', 'reqd', required_area ? 1 : 0, cdn
                    );
                    frm.fields_dict.items.grid.update_docfield_property(
                        'key_result_areas', 'reqd', required_key_result_areas ? 1 : 0, cdn
                    );
                    frm.fields_dict.items.grid.update_docfield_property(
                        'baseline', 'reqd', required_baselined ? 1 : 0, cdn
                    );
                    frm.fields_dict.items.grid.update_docfield_property(
                        'activity', 'reqd', required_activity ? 1 : 0, cdn
                    );

                    frm.fields_dict.items.grid.toggle_enable('area', required_area ? 1 : 0, row);
                    frm.fields_dict.items.grid.toggle_enable('key_result_areas', required_key_result_areas ? 1 : 0, row);
                    frm.fields_dict.items.grid.toggle_enable('baseline', required_baselined ? 1 : 0, row);
                    frm.fields_dict.items.grid.toggle_enable('activity', required_activity ? 1 : 0, row);

                    // Toggle display
                    if (frm.is_new()) {
                        // Make both fields readonly for new document
                        frm.fields_dict.items.grid.toggle_enable('self_rating', false, row);
                        frm.fields_dict.items.grid.toggle_enable('supervisor_rating', false, row);
                    }
                    // grid_row.toggle_display('area', required_area);
                    // grid_row.toggle_display('key_result_areas', required_key_result_areas);
                    // grid_row.toggle_display('baseline', required_baselined);
                    // grid_row.toggle_display('activity', required_activity);

                    console.log("Fields updated for new row - Area required:", required_area);
                }
            }
        });
    }
});


frappe.ui.form.on("Max Competency Item", {
    items_add: function(frm, cdt, cdn) {
        // Make area field mandatory
        if (frm.is_new()) {
            // Make both fields readonly for new document
            frm.fields_dict.items.grid.toggle_enable('self_rating', false, row);
            frm.fields_dict.items.grid.toggle_enable('supervisor_rating', false, row);
        }
       
    }
});

function check_item_fields(frm){
    frappe.call({
        method: "erpnext.max.doctype.managing_for_excellence.managing_for_excellence.get_target_fields",
        args: {
            pms_group: frm.doc.pms_group
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                console.log('API Response received');

                const required_activity = r.message[0].required_activity;
                const required_area = r.message[0].required_area;
                const required_baselined = r.message[0].required_baselined;
                const required_key_result_areas = r.message[0].required_key_result_areas;

                // Apply to the newly added row
                const row = frappe.get_doc(cdt, cdn);
                const grid_row = frm.fields_dict.items.grid.grid_rows_by_docname[cdn];

                // Toggle required property
                frm.fields_dict.items.grid.update_docfield_property(
                    'area', 'reqd', required_area ? 1 : 0, cdn
                );
                frm.fields_dict.items.grid.update_docfield_property(
                    'key_result_areas', 'reqd', required_key_result_areas ? 1 : 0, cdn
                );
                frm.fields_dict.items.grid.update_docfield_property(
                    'baseline', 'reqd', required_baselined ? 1 : 0, cdn
                );
                frm.fields_dict.items.grid.update_docfield_property(
                    'activity', 'reqd', required_activity ? 1 : 0, cdn
                );

                frm.fields_dict.items.grid.toggle_enable('area', required_area ? 1 : 0, row);
                frm.fields_dict.items.grid.toggle_enable('key_result_areas', required_key_result_areas ? 1 : 0, row);
                frm.fields_dict.items.grid.toggle_enable('baseline', required_baselined ? 1 : 0, row);
                frm.fields_dict.items.grid.toggle_enable('activity', required_activity ? 1 : 0, row);

                // Toggle display
                if (frm.is_new()) {
                    // Make both fields readonly for new document
                    frm.fields_dict.items.grid.toggle_enable('self_rating', false, row);
                    frm.fields_dict.items.grid.toggle_enable('supervisor_rating', false, row);
                }
                // grid_row.toggle_display('area', required_area);
                // grid_row.toggle_display('key_result_areas', required_key_result_areas);
                // grid_row.toggle_display('baseline', required_baselined);
                // grid_row.toggle_display('activity', required_activity);

                console.log("Fields updated for new row - Area required:", required_area);
            }
        }
    });
}


function restrict_child_fields_on_refresh(frm) {
    if (!frm.doc.pms_group) return;

    frappe.call({
        method: "erpnext.max.doctype.managing_for_excellence.managing_for_excellence.get_target_fields",
        args: {
            pms_group: frm.doc.pms_group
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                console.log("🔄 Restricting child fields on refresh");

                const { required_activity, required_area, required_baselined, required_key_result_areas } = r.message[0];

                // Loop through all existing rows
                frm.fields_dict.items.grid.grid_rows.forEach(row_wrapper => {
                    const row = row_wrapper.doc;

                    // Required properties
                    frm.fields_dict.items.grid.update_docfield_property('area', 'reqd', required_area ? 1 : 0, row.name);
                    frm.fields_dict.items.grid.update_docfield_property('key_result_areas', 'reqd', required_key_result_areas ? 1 : 0, row.name);
                    frm.fields_dict.items.grid.update_docfield_property('baseline', 'reqd', required_baselined ? 1 : 0, row.name);
                    frm.fields_dict.items.grid.update_docfield_property('activity', 'reqd', required_activity ? 1 : 0, row.name);

                    // Enable/Disable
                    frm.fields_dict.items.grid.toggle_enable('area', required_area ? 1 : 0, row);
                    frm.fields_dict.items.grid.toggle_enable('key_result_areas', required_key_result_areas ? 1 : 0, row);
                    frm.fields_dict.items.grid.toggle_enable('baseline', required_baselined ? 1 : 0, row);
                    frm.fields_dict.items.grid.toggle_enable('activity', required_activity ? 1 : 0, row);

                    if (frm.doc.workflow_state ==='Plan Verified' || frm.doc.workflow_state ==='Evaluation Submitted' || frm.doc.workflow_state ==='Evaluation Submitted' || frm.doc.workflow_state ==="Evaluation Verified"){
                        frm.fields_dict.items.grid.toggle_enable('area', 0, row);
                        frm.fields_dict.items.grid.toggle_enable('key_result_areas',0, row);
                        frm.fields_dict.items.grid.toggle_enable('baseline', 0, row);
                        frm.fields_dict.items.grid.toggle_enable('activity', 0, row);
                        frm.fields_dict.items.grid.toggle_enable('output', 0, row);
                        frm.fields_dict.items.grid.toggle_enable('kpi', 0, row);

                        frm.fields_dict.competency_item.grid.toggle_enable('competency', 0, row);
                        frm.fields_dict.competency_item.grid.toggle_enable('description', 0, row);
                    }

                    // Make self/supervisor ratings readonly if new
                   
                });

                // Refresh to reflect UI changes
                frm.refresh_field('items');
            }
        }
    });
}
