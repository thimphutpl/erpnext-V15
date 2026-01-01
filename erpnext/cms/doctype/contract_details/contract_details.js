// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Contract Details", {
    refresh(frm) {
        toggle_lock(frm);
    },
    status(frm) {
        toggle_lock(frm);
    },
    start_date(frm) {
        validate_dates(frm);
    },
    end_date(frm) {
        validate_dates(frm);
        update_delay_days(frm);
    },
    initial_amount(frm) {
        calculate_final_amount(frm);
    },
    discount(frm) {
        calculate_final_amount(frm);
    },
    negotiation_amount(frm) {
        calculate_final_amount(frm);
    },
    additional(frm) {
        calculate_final_amount(frm);
    },
    revised_expiry_date(frm) {
        update_delay_days(frm);
    },
    actual_completion_date(frm) {
        update_delay_days(frm);
    }  
    
});

function toggle_lock(frm) {
  const locked = (frm.doc.status === "Closed" || frm.doc.status === "Terminated");
  (frm.fields || []).forEach(f => {
    if (!f.df) return;
    if (f.df.fieldtype === "Section Break" || f.df.fieldtype === "Column Break") return;

    const fn = f.df.fieldname;
    if (!fn) return
    if (fn === "status") {
      frm.set_df_property(fn, "read_only", 0);
    } else {
      frm.set_df_property(fn, "read_only", locked ? 1 : 0);
    }
  });
  frm.refresh_fields();
}

function validate_dates(frm) {
    const start = frm.doc.start_date;
    const end = frm.doc.end_date;

    if (start && end) {
        if (moment(start).isAfter(end)) {
            frappe.msgprint("Start Date cannot be greater than End Date.");
            frm.set_value("start_date", "");
        }
    }
}


function update_delay_days(frm) {
  const actual = frm.doc.actual_completion_date;
  const deadline = frm.doc.revised_expiry_date || frm.doc.end_date;

  if (!actual || !deadline) {
    frm.set_value("delay_days", 0);
    frm.toggle_display("delay_days", false);
    return;
  }

  const diff = frappe.datetime.get_diff(actual, deadline);
  const delay_days = diff > 0 ? diff : 0;

  frm.set_value("delay_days", delay_days);
  frm.toggle_display("delay_days", delay_days > 0);
}


function calculate_final_amount(frm) {
    const initial = flt(frm.doc.initial_amount);
    const discount = flt(frm.doc.discount);
    const negotiation = flt(frm.doc.negotiation_amount);
    const additional = flt(frm.doc.additional);

    const final_amount =
        initial
        - discount
        - negotiation
        + additional;

    frm.set_value("final_amount", final_amount);
}






