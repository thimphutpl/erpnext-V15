# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns, data = get_columns(filters),get_datas(filters) 
    return columns, data

# def get_conditions(filters):
    
def get_datas(filters):
    data_list=frappe.db.sql("select * from `tabScholarship` where 1=1 ", as_dict=True)
    
    
    datas_list=[]
    for data in data_list:
        if data['name']=="lnjicljput":
            continue
        dat={}
        prof=""
        if data['profile_picture']:
            dat['profile_picture']=data['profile_picture']+"#"+data['name1']+"#("+data['cid_number']+")#"+data['contact_number']
            
        dat['profile_detail']="Village: "+data['village']+".\nGewog: "+data['gewog']+".\nDzongkhag: "+data['dzongkhag']+".\nContact No: "+data['contact_number']+".\nEmail: "+data['email_address']
        dat['profile_academicss']="XII "+data['stream']+" with "+data['percentage']+".\n"+data['highschool']+"\n"+".English: "+data['english']
        dat['profile_relationship']=""
        famdetails=frappe.db.sql("Select * from `tabFamily Detail Table` where parent='{}'".format(data['name']), as_dict=True)
        for fam in famdetails:
            dat['profile_relationship']+=fam['relation_to_applicant']+": "+fam['name1']+", "+fam["remarks"]+".\n"
        
        dat['profile_achievements']=""
        achievementdetails=frappe.db.sql("Select * from `tabStudent Achievement Table` where parent='{}'".format(data['name']), as_dict=True)
        frappe.throw(str(achievementdetails))
        for ach in achievementdetails:
            famdetails+=ach['achievement_rankposition']+" in "+ach["achievement_name"]+ " in "+str(ach['achievement_year'])+".\n"
        
        dat['profile_results']="Scored "+str(data['percentagex'])+" in Class X..\n\n"+"(Selected for "+str(data['college'])+")"
        datas_list.append(dat)
        
    return datas_list

def get_columns(filters):
    columns = [
          {
            'fieldname': 'profile_picture',
            'label': 'Profile Picture',
            'fieldtype': 'Image',
            'options': '',
            
        },
     {
            'fieldname': 'profile_detail',
            'label':'Profile Detail',
            'fieldtype': 'Data',
            
        },
      
        {
            'fieldname': 'profile_academicss',
            'label': 'Academic Detail',
            'fieldtype': 'Data',
            'options': ''
        },
        {
            'fieldname': 'profile_relationship',
            'label': 'Family Details',
            'fieldtype': 'Data',
            'options': ''
        },
            {
            'fieldname': 'profile_achievements',
            'label': 'Achievement',
            'fieldtype': 'Data',
            'options': ''
        },
            {
            'fieldname': 'profile_results',
            'label': 'Results',
            'fieldtype': 'Data',
            'options': ''
        }
    ]
    return columns