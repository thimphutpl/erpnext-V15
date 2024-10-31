# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = get_columns(), get_datas(filters)
	return columns, data

def get_datas(filters=None):
    conditions=get_conditions(filters)
    data_sql=frappe.db.sql("""
        Select name, insurance_for, equipment, asset, posting_date, branch, vehicle_type, 
        vehicle_model, asset_name, asset_category, asset_sub_category, company, total_amount, 
        cost_center, party_type, imprest_party, amended_from from `tabInsurance and Registration` where 1=1 {}""".format(conditions), as_dict=True)
    
    final_data=[]
    for data in data_sql:
        dat=data
        insurance_item=frappe.db.sql("Select party, policy_number, insured_date, due_date, validity, insurance_type, total_amount from `tabInsurance Details` where parent='{}'".format(data["name"]), as_dict=True)
        claim_item=frappe.db.sql("Select claim_date, claim_amount, remarks from `tabClaim Details` where parent='{}'".format(data["name"]), as_dict=True)
        registration_detail=frappe.db.sql("Select fiscal_year, registration_date, registration_amount from `tabRegistration Details` where parent='{}'".format(data["name"]), as_dict=True)
        registration_certificate_and_emission_detail=frappe.db.sql("Select fiscal_year, registration_date, registration_amount from `tabRegistration Details` where parent='{}'".format(data["name"]), as_dict=True)
        
        dat['insurance_item']=create_table(insurance_item)
        dat['claim_item']=create_table(claim_item)
        dat['registration_detail']=create_table(registration_detail)
        dat['registration_certificate_and_emission_detail']=create_table(registration_certificate_and_emission_detail)
        final_data
        
        
    return data_sql

def get_conditions(filters):
	conditions = []
 
	if filters.get("company"):
		conditions.append("company = \"{}\"".format(filters.get("company")))
	if filters.get("equipment"):
		conditions.append("equipment = \"{}\"".format(filters.get("equipment")))

	return "and {}".format(" and ".join(conditions)) if conditions else ""


def create_table(datas, filters=None):
    tab=""
    if datas:
        tab+="<table style='border:1px solid black;'>"
        tab+="<tr style=\"border:1px solid black;\">"
        for col in datas[0].keys():
            tab+="<th style=\"border:1px solid black;\">"+str(col)+"</th>"
        tab+="<tr>"
            
        
        for data in datas:
            tab+="<tr style=\"border:1px solid black;\">"
            for ele in data.values():
                tab+="<td style=\"border:1px solid black;\">"+str(ele)+"</td>"
            tab+="</tr>"
        tab+="</table>"
    return tab
        
        
        
    

def get_columns(filters=None):
    return [
		{
			"fieldname":"insurance_for",
			"label":_("Insurance For"),
			"fieldtype":"Data",
			"width":130
		},
		{
			"fieldname":"equipment",
			"label":_("Vehicle"),
			"fieldtype":"Link",
			"options": "Equipment",
			"width":130
		},
		{
			"fieldname":"asset",
			"label":_("Asset"),
			"fieldtype":"Link",
			"options": "Asset",
			"width":130
		},
		{
			"fieldname":"posting_date",
			"label":_("Posting Date"),
			"fieldtype":"Date",
			"width":130
		},
		{
			"fieldname":"branch",
			"label":_("Branch"),
			"fieldtype":"Link",
			"options": "Branch",
			"width":250
		},
		{
			"fieldname":"vehicle_type",
			"label":_("Vehicle Type"),
			"fieldtype":"Link",
			"options": "Equipment Type",
			"width":130
		},
		{
			"fieldname":"vehicle_model",
			"label":_("Vehicle Model"),
			"fieldtype":"Data",
			"width":130
		},
		{
			"fieldname":"party_type",
			"label":_("Imprest Party Type"),
			"fieldtype":"Data",
			"width":130
		},
		{
			"fieldname":"cost_center",
			"label":_("Cost Center"),
			"fieldtype":"Link",
			"options": "Cost Center",
			"width":130
		},
		{
			"fieldname":"imprest_party",
			"label":_("Imprest Party"),
			"fieldtype":"Data",
			"width":130
		},
		{
			"fieldname":"asset_name",
			"label":_("Asset Name"),
			"fieldtype":"Data",
			"width":130
		},
  
		{
			"fieldname":"asset_category",
			"label":_("Asset Category"),
			"fieldtype":"Link",
			"options": "Equipment Type",
			"width":130
		},
		{
			"fieldname":"insurance_item",
			"label":_("Insurance Detail"),
			"fieldtype":"HTML",
		
			
		},
		{
			"fieldname":"claim_item",
			"label":_("Claim Detail"),
			"fieldtype":"HTML",
			
			
		},
		{
			"fieldname":"registration_detail",
			"label":_("Registration Detail"),
			"fieldtype":"HTML",
   			"width":400
			
   
			
		},
		{
			"fieldname":"registration_certificate_and_emission_detail",
			"label":_("Registration Certificate and Emission Details"),
			"fieldtype":"HTML",
			"width":400
			
		},
		{
			"fieldname":"company",
			"label":_("Company"),
			"fieldtype":"Link",
			"options":"Company",
			"width":130
		},
		{
			"fieldname":"total_amount",
			"label":_("Total Amount"),
			"fieldtype":"Data",
			"width":130
		},
		{
			"fieldname":"amended_from",
			"label":_("Amended From"),
			"fieldtype":"Link",
			"options": "Insurance and Registration",
			"width":130
		},
	]
