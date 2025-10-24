frappe.ui.form.on('Scholarship', {
    refresh: function(frm) {
        frm.set_query('gewog', function() {
            return {
                filters: {
                    dzongkhag: frm.doc.dzongkhag
                }
            };
        });
        frm.set_query('village', function() {
            return {
                filters: {
                    gewog: frm.doc.gewog
                }
            };
        });
    },
});
