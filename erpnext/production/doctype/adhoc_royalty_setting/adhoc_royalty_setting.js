cur_frm.add_fetch("range_name","location","location");
cur_frm.add_fetch("range_name", "branch", "branch");
cur_frm.add_fetch("range_name", "company", "company");

frappe.ui.form.on('Adhoc Production', {
	refresh: function(frm) {

	}
});
