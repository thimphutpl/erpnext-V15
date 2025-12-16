import datetime
import json

import frappe
import pytz
from frappe import _

no_cache = 1

@frappe.whitelist(allow_guest=True)
def get_asset_info(asset_code):
    context = {}
    context["asset_info"] = None

    if asset_code:
        # applicant_info = frappe.get_all(
        #     "Asset",
        #     filters={"name": asset_code},
        #     fields=["", "applicant_name", "cid", "gender", "employment_type", "applicant_rank", "application_status", "mobile_no", "flat_no","building_classification","application_date_time","work_station"],
        # )
        asset_info = frappe.db.sql(
            """
                select concat(custodian, ' - ', custodian_name) custodian, branch,
                purchase_date, concat("BTN. ", format(gross_purchase_amount,2)) as asset_rate, name, asset_name from `tabAsset` where name = '{}'
            """.format(asset_code), as_dict=1
        )
        context["asset_info"] = asset_info
    
    return context
