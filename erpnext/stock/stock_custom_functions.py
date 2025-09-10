# Copyright (c) 2016, Druk Holding & Investments Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def get_current_item_code(item_group): 
    # Fetch the latest item code from the database for the given item group
    item_code = frappe.db.sql("""
        SELECT item_code FROM `tabItem`
        WHERE item_group=%s
        ORDER BY item_code DESC
        LIMIT 1
    """, (item_group,))

    # If an item code exists, attempt to increment it
    if item_code and item_code[0][0].isdigit():
        # Safely increment only if the item_code is numeric
        return str(int(item_code[0][0]) + 1)
    else:
        # Return a base item code for the group if no item code exists or it is non-numeric
        return str(getItemCode(item_group))

def getItemCode(item_group):
    """
    Provides a base item code for the given item group.
    """
    return {
        "Consumables": 100000,
        "Fixed Asset": 200000,
        "Spareparts": 300000,
        "Services Miscellaneous": 400000,
        "Services Works": 500000,
        "Sales Product": 600000
    }.get(item_group, 0)

