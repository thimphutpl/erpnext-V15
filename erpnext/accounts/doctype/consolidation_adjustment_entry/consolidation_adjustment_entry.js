frappe.ui.form.on('Consolidation Adjustment Entry', {
	refresh: function(frm) {
		frm.get_docfield("items").allow_bulk_edit = 1;
	}
});