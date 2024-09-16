# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe

# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime



def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data
def get_columns():
	columns = [
		  {
            'fieldname': 'name',
            'label': 'name',
            'fieldtype': 'Data',
            'options': '',
			
        },
     {
            'fieldname': 'branch',
            'label':'branch',
            'fieldtype': 'Data',
            
        },
      
        {
            'fieldname': 'date',
            'label': 'date',
            'fieldtype': 'Data',
            'options': ''
        },
        {
            'fieldname': 'remarks',
            'label': 'remarks',
            'fieldtype': 'Data',
            'options': ''
        },
            {
            'fieldname': 'company',
            'label': 'company',
            'fieldtype': 'Data',
            'options': ''
        },
   {
            'fieldname': 'vip_name',
            'label': 'vip_name',
            'fieldtype': '',
            'options': ''
        }
   ,
   {
            'fieldname': 'particulars',
            'label': 'particulars',
            'fieldtype': 'Data',
            'options': ''
        }
   ,
     
         {
            'fieldname': 'quantity',
            'label': 'quantity',
            'fieldtype': 'Data',
            'options': ''
        },
    {
            'fieldname': 'rate',
            'label': 'Rate',
            'fieldtype': 'Data',
            'options': ''
        },
		
		 {
            'fieldname': 'warehouse',
            'label': 'warehouse',
            'fieldtype': 'Data',
            'options': ''
        },
		
    {
            'fieldname': 'uom',
            'label': 'UOM',
            'fieldtype': 'Data',
            
        },
  
   
    
   
   
	]


	return columns

def get_data(filters):
    conditions = get_filters(filters)
    # data = frappe.db.get_all("Housing Application",fields=get_fields_name(), filters = conditions)
    # return data
    query = """
                     SELECT s.name ,s.branch,s.date,s.remarks,s.company,s.vip_name,sd.particulars,sd.quantity,sd.rate,sd.warehouse,sd.uom from `tabSoelra` s inner join `tabSoelra Details` sd on s.name=sd.parent where {conditions}""".format(conditions = conditions)
           
    data = frappe.db.sql(query, filters,as_dict=True)
    return data
        

def get_filters(filters):
    conditions = []
    if filters.get('application_date_time'):
      
        conditions.append("application_date_time <= %(application_date_time)s")
    if filters.get('employment_type'):
        conditions.append('employment_type = %(employment_type)s')
    if filters.get('work_station'):
        conditions.append('work_station = %(work_station)s')
    # frappe.errprint(conditions)

    return  " AND ".join(conditions) if conditions else "1=1"