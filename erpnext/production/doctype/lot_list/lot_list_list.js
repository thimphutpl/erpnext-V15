
frappe.listview_settings['Lot List'] = {
    add_fields: ["name","sales_order","stock_entry","production","docstatus", "posting_date"],
    get_indicator: function(doc) {
        // Default indicators
        if(doc.production){
            return ["Taken For Sawing", "orange"];
        } else if(doc.stock_entry){
            return ["Stock Transferred", "green"];
        }

        // For sales, call server to check quantities
        let indicator = ["Unsold", "green"];
        if(doc.name) {
            frappe.call({
                method: "erpnext.production.doctype.lot_list.lot_list.get_lot_sale_status",
                args: { lot_name: doc.name },
                async: false,  // Wait for result
                callback: function(r) {
                    if(r.message == "Sold") {
                        indicator = ["Sold", "orange"];
                    } else if(r.message == "Partially Sold") {
                        indicator = ["Partially Sold", "yellow"];
                    } else if(r.message == "Stock Transferred") {
                        indicator = ["Stock Transferred", "orange"];
                    } else if(r.message == "Stock Partially Transferred") {
                        indicator = ["Stock Partially Transferred", "yellow"];
                    }
                }
            });
        }
        return indicator;
    }
};