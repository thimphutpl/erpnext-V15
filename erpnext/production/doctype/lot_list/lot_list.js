// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
// cur_frm.add_fetch("item", "item_name", "item_name");
frappe.ui.form.on('Lot List', {
	setup: function(frm){
                frm.get_docfield("lot_list_items").allow_bulk_edit = 1;
        },
	refresh: function(frm) {
			
	},
	onload: function(frm){
	}
});

frappe.ui.form.on("Lot List","refresh",function(frm){
	cur_frm.set_query("warehouse", function() {
        return {
			"query":"erpnext.controllers.queries.filter_branch_wh",
            "filters": {
                "branch": cur_frm.doc.branch
            }
        };

	});
	
	cur_frm.set_query("location", function(){
		return {
				"filters": {
						"branch": cur_frm.doc.branch,
						"is_disabled": 0
				}
		}
});
})

frappe.ui.form.on("Lot List Item", {
        "length": function(frm, cdt, cdn) {
                        d = locals[cdt][cdn];
                        if(frm.doc.item_sub_group == "Sawn" || frm.doc.item_sub_group == "Block" || frm.doc.item_sub_group == "Field Sawn"){
                                if(d.girth > 0 && d.height > 0){
                                        update_volume(frm, cdt, cdn);
                                }
                        }else{
                                if(d.girth > 0){
                                        update_volume(frm, cdt, cdn);
                                }
                        }
                },
        "girth": function(frm, cdt, cdn) {
                        d = locals[cdt][cdn];
                        if(frm.doc.item_sub_group == "Sawn" || frm.doc.item_sub_group == "Block" || frm.doc.item_sub_group == "Field Sawn"){
                                if(d.length > 0 && d.height > 0){
                                        update_volume(frm, cdt, cdn);
                                }
                        }else{
                                if(d.length > 0){
                                        update_volume(frm, cdt, cdn);
                                }
                        }
                },
        "height": function(frm, cdt, cdn) {
                        d = locals[cdt][cdn];
                        if(frm.doc.item_sub_group == "Sawn" || frm.doc.item_sub_group == "Block" || frm.doc.item_sub_group == "Field Sawn"){
                                if(d.length > 0 && d.girth > 0){
                                        update_volume(frm, cdt, cdn);
                                }
                        }
                },
	"number_pieces": function(frm, cdt, cdn) {
			update_volume(frm, cdt, cdn);
				},
});

frappe.ui.form.on("Lot List Details",{
	lot_list_items_upload_complete: function(frm, cdt, cdn)
	{
		console.log("complete")
		var row = locals[cdt][cdn]
		get_item_details(frm, row)
		refresh_field("lot_list_items")

	},
	"item": function(frm,cdt,cdn)
	{
		var row = locals[cdt][cdn]
		get_item_details(frm, row)
	}
})

function get_item_details(frm, row){
		return frappe.call({
			method: "get_item_details",
			doc: cur_frm.doc,
			args: {'item': row.item},
			callback: function(r, rt){
					if(r.message){
						frappe.model.set_value(row.doctype, row.name, "item_name", r.message[0]['item_name']);
						frappe.model.set_value(row.doctype, row.name, "item_sub_group", r.message[0]['item_sub_group']);
						frappe.model.set_value(row.doctype, row.name, "species", r.message[0]['species']);
						frappe.model.set_value(row.doctype, row.name, "timber_class", r.message[0]['timber_class']);
					} 
			}
		});
}


function update_volume(frm, cdt, cdn)
{
	d = locals[cdt][cdn];
	if(frm.doc.item_sub_group == "Sawn" || frm.doc.item_sub_group == "Block" || frm.doc.item_sub_group == "Field Sawn"){
                var volume = ((d.length * d.girth * d.height) / 144) * d.number_pieces;
        }
        else{
		var f = d.girth.toString().split(".");
		var in_inches = 0;
		if(f.length == 1){
			f[0] = d.girth;
			f[1] = 0;
		}
		var girth = (parseFloat(f[0]) * 12) + parseFloat(f[1]);
		//console.log("Girth" + girth +" f1 " + f[0] + " f2 " + f[1]);
		var volume = (((girth * girth) * d.length ) / 1809.56) * d.number_pieces;
	}

	frappe.model.set_value(cdt, cdn, "volume", volume);
	
	var items = frm.doc.items || [];
	var total_vol = 0;
	for(var i = 0; i < items.length; i++ ){
		total_vol += items[i].volume;
	}

	frm.set_value("total_volume", total_vol);
	frm.set_value("total_pieces", items.length);
}


// frappe.ui.form.on('Lot List', {
//     refresh(frm) {
//         frm.trigger("calculate_total_volume");
//     },
//     lot_list_items_add: function(frm) {
//         frm.trigger("calculate_total_volume");
//     },
//     lot_list_items_remove: function(frm) {
//         frm.trigger("calculate_total_volume");
//     }
// });

// frappe.ui.form.on('Lot List Details', {
//     total_volume: function(frm, cdt, cdn) {
//         frm.trigger("calculate_total_volume");
//     },
//     lot_list_items_remove: function(frm) {
//         frm.trigger("calculate_total_volume");
//     }
// });

// frappe.ui.form.on('Lot List', {
//     calculate_total_volume: function(frm) {
//         let total_volume = 0;
//         if (frm.doc.lot_list_items) {
//             frm.doc.lot_list_items.forEach(row => {
//                 total_volume += flt(row.total_volume);
//             });
//         }
//         frm.set_value('total_volume', total_volume);
//     }
// });