// // Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// // For license information, please see license.txt

// // frappe.ui.form.on("Voucher Correction", {
// // 	refresh(frm) {

// // 	},
// // });



// frappe.ui.form.on("Voucher Correction", {
//   refresh(frm) {
//     // if (frm.doc.docstatus === 1 && !frm.doc.applied) {
//     //   frm.add_custom_button("Apply Correction", () => {
//     //     frm.call("apply_correction").then(() => {
//     //       frappe.msgprint("Correction applied successfully.");
//     //       frm.reload_doc();
//     //     });
//     //   });
//     // }
//   },
//   voucher_name(frm) {
//     (frm.doc.changes || []).forEach(r => r.old_value = "");
//     frm.refresh_field("changes");
//   }
// });

// async function fetch_old_value(frm, cdt, cdn) {
//   const row = locals[cdt][cdn];
//   if (!frm.doc.voucher_doctype || !frm.doc.voucher_name) return;
//   if (!row.scope || !row.field_name) return;

//   if (row.scope === "Header") {
//     const r = await frappe.call({
//       method: "erpnext.accounting_tools.doctype.voucher_correction.voucher_correction.get_old_value",
//       args: {
//         voucher_doctype: frm.doc.voucher_doctype,
//         voucher_name: frm.doc.voucher_name,
//         scope: "Header",
//         fieldname: row.field_name
//       }
//     });
//     frappe.model.set_value(cdt, cdn, "old_value", r.message || "");
//     return;
//   }

//   if (row.scope === "Child") {
//     if (!row.child_table || !row.child_row_idx) return;

//     const r = await frappe.call({
//       method: "erpnext.accounting_tools.doctype.voucher_correction.voucher_correction.get_old_value",
//       args: {
//         voucher_doctype: frm.doc.voucher_doctype,
//         voucher_name: frm.doc.voucher_name,
//         scope: "Child",
//         child_table: row.child_table,
//         row_idx: row.child_row_idx,
//         fieldname: row.field_name
//       }
//     });

//     frappe.model.set_value(cdt, cdn, "old_value", r.message || "");
//   }
// }

// frappe.ui.form.on("Voucher Corection Detail", {
//   scope: fetch_old_value,
//   child_table: fetch_old_value,
//   child_row_idx: fetch_old_value,
//   field_name: fetch_old_value
// });




// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Voucher Correction", {
  refresh(frm) {
    // Auto-apply happens on submit in Python (on_submit),
    // so we intentionally do NOT show an Apply button here.
  },

  voucher_doctype(frm) {
    // Clear old values when voucher type changes
    (frm.doc.changes || []).forEach(r => (r.old_value = ""));
    frm.refresh_field("changes");
  },

  voucher_name(frm) {
    // Clear old values when voucher changes
    (frm.doc.changes || []).forEach(r => (r.old_value = ""));
    frm.refresh_field("changes");
  },
});

async function fetch_old_value(frm, cdt, cdn) {
  const row = locals[cdt][cdn];

  if (!frm.doc.voucher_doctype || !frm.doc.voucher_name) return;
  if (!row.scope || !row.field_name) return;

  // prevent older async responses from overwriting newer selection
  const request_key = `${frm.doc.voucher_doctype}|${frm.doc.voucher_name}|${row.scope}|${row.child_table || ""}|${row.child_row_idx || ""}|${row.field_name}`;
  row.__last_req_key = request_key;

  try {
    // HEADER
    if (row.scope === "Header") {
      const r = await frappe.call({
        method: "erpnext.accounting_tools.doctype.voucher_correction.voucher_correction.get_old_value",
        args: {
          voucher_doctype: frm.doc.voucher_doctype,
          voucher_name: frm.doc.voucher_name,
          scope: "Header",
          fieldname: row.field_name,
        },
      });

      if (row.__last_req_key !== request_key) return;
      frappe.model.set_value(cdt, cdn, "old_value", r.message || "");
      return;
    }

    // CHILD
    if (row.scope === "Child") {
      if (!row.child_table || !row.child_row_idx) return;

      const r = await frappe.call({
        method: "erpnext.accounting_tools.doctype.voucher_correction.voucher_correction.get_old_value",
        args: {
          voucher_doctype: frm.doc.voucher_doctype,
          voucher_name: frm.doc.voucher_name,
          scope: "Child",
          child_table: row.child_table,
          row_idx: row.child_row_idx,
          fieldname: row.field_name,
        },
      });

      if (row.__last_req_key !== request_key) return;
      frappe.model.set_value(cdt, cdn, "old_value", r.message || "");
    }
  } catch (e) {
    // optional: show only if you want noise
    // frappe.msgprint(e.message || __("Failed to fetch old value"));
    // Clear old_value on error to avoid misleading values
    frappe.model.set_value(cdt, cdn, "old_value", "");
  }
}

frappe.ui.form.on("Voucher Corection Detail", {
  scope: fetch_old_value,
  child_table: fetch_old_value,
  child_row_idx: fetch_old_value,
  field_name: fetch_old_value,
});
