# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)
    
    return columns, data

def get_columns(filters):
    columns = [
        
        {
            "label": _("Name"),
            "fieldname": "name",
            "fieldtype": "data",
            "width": 140,
        },
        {
            "label": _("Designation(Giver)"),
            "fieldname": "designation_giver",
            "fieldtype": "data",
            "width": 160,
        },
          {
            "label": _("Designation(Recipient)"),
            "fieldname": "designation_recipient",
            "fieldtype": "data",
            "width": 180,
        },
  
        {
            "label": _("Description of gift"),
            "fieldname": "description_of_gift",
            "fieldtype": "data",
            "width": 400,
        },
        {
            "label": _("Date of Receipt"),
            "fieldname": "date_of_receipt",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "label": _("Source of gift(name)"),
            "fieldname": "source_of_gift",
            "fieldtype": "data",
            "width": 180,
        },
        {
            "label": _("Relationship with the giver"),
            "fieldname": "relationship_with_the_giver",
            "fieldtype": "data",
            "width": 220,
        },
        {
            "label": _("Date of Deposit"),
            "fieldname": "date_of_deposit",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "label": _("Current disposition of location"),
            "fieldname": "current_disposition_of_location",
            "fieldtype": "data",
            "width": 300,
        },
        {
            "label": _("Estimated Fair Market Value"),
            "fieldname": "estimated_fair_market_value",
            "fieldtype": "data",
            "width": 180,
        },
        {
            "label": _("Mode of disposal"),
            "fieldname": "mode_of_disposal",
            "fieldtype": "data",
            "width": 500,
        },
    ]
    return columns

def get_data(filters):

    if filters:
        q="select * from `tabGift Register` where 1=1 and {}".format(apply_filters_on_query(filters))
        datalist=frappe.db.sql(q, as_dict=True)
    
    else:
        
        datalist=frappe.db.sql("select * from `tabGift Register`", as_dict=True)
        
    
    
    datas=[]
    
    for data in datalist:
        row={}
        row['name']=data['gift_name']
        row['designation_giver']=data['designation']
        row['designation_recipient']=data['designation_of_the_recipient']
        row['description_of_gift']=data['description_of_gift']
        row['date_of_receipt']=data['date_of_receipt']
        row['source_of_gift']=data['name_of_the_gift_giver']
        row['relationship_with_the_giver']=data['relationship_with_the_giver']
        row['date_of_deposit']=data['date_of_deposit']
        row['current_disposition_of_location']=data['current_deposition_of_location']
        row['estimated_fair_market_value']='{:.2f}'.format(data['estimated_fair_market_valuenu'])
        row['mode_of_disposal']=data['mode_of_disposal']
        row['gift_status']=data['gift_status']
            
        datas.append(row)
    
    return datas

def apply_filters_on_query(filters):
    
    
    query=""
    if query=="":
        
        
        if filters.get("fiscal_year"):
            query+="date_of_receipt >='{}-01-01' and date_of_receipt<='{}-12-31'".format(filters.get("fiscal_year"), filters.get("fiscal_year"))
        else:
            if filters.get("name"):
                query+="gift_name='{}'".format(filters.get("name"))
            if filters.get("to_date"):
                query+="date_of_receipt<'{}'".format(filters.get("to_date"))
            if filters.get("from_date"):
                query+="date_of_receipt>'{}'".format(filters.get("from_date"))
    else:
        
        
        if filters.get("fiscal_year")=="fiscal_year":
            query+=" and date_of_receipt >='{}-01-01' and date_of_receipt<='{}-12-31'".format(filters.get("fiscal_year"), filters.get("fiscal_year"))
        else:
            if filters.get("name"):
                query+=" and gift_name='{}'".format(filters.get("name"))
            if filters.get("to_date")=="to_date":
                query+=" and date_of_receipt<'{}'".format(filters.get("to_date"))
            if filters.get("from_date")=="from_date":
                query+=" and date_of_receipt>'{}'".format(filters.get("from_date"))
                     
    return query