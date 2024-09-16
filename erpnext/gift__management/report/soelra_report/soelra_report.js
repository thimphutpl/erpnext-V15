// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Soelra Report"] = {
	"filters": [
		{
            'fieldname': 'application_date_time',
            'label': 'Application Date',
            'fieldtype': 'Date',
            'options': 'Application Date',
			
        },
		
		 {
            'fieldname': 'employment_type',
            'label': 'Employment Type',
            'fieldtype': 'Select',
            'options': [
				"Civil Servant",
				"Corporation, Private and etc",
			]
        },
       
    {
            'fieldname': 'application_status',
            'label': 'Application Status',
            'fieldtype': 'Select',
            'options': [
				"pending",
				"Allotted",
				"Rejected",
				"Withdrawn",
				"Cancelled",
                "Not Eligible",
                "Resigned/Superannuated"
			]
        },
    
      {
            'fieldname': 'building_classification',
            'label': 'Eligible Building Classification',
            'fieldtype': 'Link',
            'options': 'Building Classification',
            // 'Link': 'Building Classification'
        },
	]

	
};
