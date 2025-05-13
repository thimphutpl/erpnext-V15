frappe.pages['common-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'None',
		single_column: true
	});
	$(frappe.render_template('common_dashboard')).appendTo(page.body);
}