// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Land Record Report"] = {
	"filters": [

		{
			fieldname:"land_type", 
			label:__("Land Type"), 
			fieldtype:"Select", 
			options:["","Crown Property","OGZ"], 
		},
		{
			fieldname:"land_sub_type", 
			label:__("Land Sub Type"), 
			fieldtype:"Select", 
			options:["","Crown Property","Individual","Lhakhang"], 
		},
		{
			fieldname:"ownership_type", 
			label:__("Ownership Type"), 
			fieldtype:"Select", 
			options:["","Individual Person","Crown Property"], 
		},
		{
			fieldname:"dzongkhag", 
			label:__("Dzongkhag"), 
			fieldtype:"Data", 
			options:"", 
		},
		{
			fieldname:"precinctland_type", 
			label:__("Precinct/Land Type"), 
			fieldtype:"Select", 
			options:["","Kamzhing","Royal Uses","Urban","Neighbourg","Heritage"], 
		},
		{
			fieldname:"plot_id", 
			label:__("Plot Id"), 
			fieldtype:"Data", 
			options:"", 
		},
		{
			fieldname:"ruralurban", 
			label:__("Rural Urban"), 
			fieldtype:"Data", 
			options:"", 
		},
		{
			fieldname:"gewog", 
			label:__("Gewog"), 
			fieldtype:"Data", 
			options:"", 
		},
		{
			fieldname:"plot_category", 
			label:__("Plot Category"), 
			fieldtype:"Data", 
			options:"", 
		},

	]
};
