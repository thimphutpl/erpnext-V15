frappe.ui.form.on('Deposit Work', {
	refresh: function(frm) {
	},
});



frappe.ui.form.on("Deposit Work", "onload", function(frm){
    cur_frm.set_query("cost_center", function(){
        return {
            "filters": [
                ["disabled", "!=", "1"],
                ["is_group", "!=", "1"],
            ]
        }
    });
});
