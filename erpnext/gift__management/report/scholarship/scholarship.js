// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Scholarship"] = {
	"filters": [

	],
	"formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
		column.resizable=true;
       if(column.fieldname=="profile_picture"){
			let dat=value.split('#')
			value=""
			value=`<img src='${dat[0]}' style='height=100px;'/>`
			value+="<p style='text-align:center;'>"
			for(let i=1; i<dat.length; i++){
				value+=dat[i]+"<br>"
			}
			value+="</p>"
			
	   }

	   if(column.fieldname=="profile_detail"){
			let dat=value.split('.')
			value=""
			for(let i=0; i<dat.length; i++){
				value+=dat[i]+"<br>"
			}
   		}

		if(column.fieldname=="profile_academicss"){
			let dat=value.split('.')
			value=""
			for(let i=0; i<dat.length; i++){
				value+=dat[i]+"<br>"
			}
   		}

		if(column.fieldname=="profile_relationship"){
			let dat=value.split('.')
			value=""
			for(let i=0; i<dat.length; i++){
				value+=dat[i]+"<br>"
			}
   		}

		if(column.fieldname=="profile_achievements"){
			let dat=value.split('.')
			value=""
			for(let i=0; i<dat.length; i++){
				value+=dat[i]+"<br>"
			}
   		}

		if(column.fieldname=="profile_results"){
			let dat=value.split('.')
			value=""
			for(let i=0; i<dat.length; i++){
				value+=dat[i]+"<br>"
			}
   		}



        return value;
    },
	get_datatable_options(options) {
		console.log(options)
		delete options['cellHeight']
		// change datatable options
		return Object.assign(options, {
			dynamicRowHeight: true,
			cellHeight: 280			
		});
	},
};


