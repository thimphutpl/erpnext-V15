// // Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// // For license information, please see license.txt


frappe.ui.form.on("Contract Details", {
    refresh(frm) {
        toggle_lock(frm);
        // optional: keep amounts consistent on load
        update_offer_amount_from_contract_currency(frm);
        calculate_final_amount(frm);
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

    // NEW: foreign currency amount changes
    contract_currency_amount(frm) {
        update_offer_amount_from_contract_currency(frm);
        calculate_final_amount(frm);
    },

    // NEW: rate changes
    exchange_rate(frm) {
        update_offer_amount_from_contract_currency(frm);
        calculate_final_amount(frm);
    },

    // if you still allow manual initial_amount edits, keep this
    // (if you want it ALWAYS auto, make initial_amount read-only in Customize Form)
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
    if (!fn) return;
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

// ✅ NEW: set Offer Amount (BTN) = contract_currency_amount * exchange_rate
function update_offer_amount_from_contract_currency(frm) {
    const ccy_amt = flt(frm.doc.contract_currency_amount); // foreign currency
    const rate = flt(frm.doc.exchange_rate);               // to BTN

    // If either missing, keep initial_amount as-is (or set 0 - your choice)
    if (!ccy_amt || !rate || rate <= 0) {
        // frm.set_value("initial_amount", 0); // uncomment if you prefer forcing 0
        return;
    }

    const btn_offer = ccy_amt * rate;
    frm.set_value("initial_amount", btn_offer);
}

function calculate_final_amount(frm) {
    const initial = flt(frm.doc.initial_amount); // now BTN
    const discount = flt(frm.doc.discount);      // BTN
    const negotiation = flt(frm.doc.negotiation_amount); // BTN
    const additional = flt(frm.doc.additional);  // BTN

    const final_amount = initial - discount - negotiation + additional;
    frm.set_value("final_amount", final_amount);
}
