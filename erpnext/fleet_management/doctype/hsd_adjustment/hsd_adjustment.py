# # Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

# from __future__ import unicode_literals
# import frappe
# from frappe.model.document import Document
# from frappe.utils import flt
# from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import get_pol_consumed_tills, get_pol_tills


# class HSDAdjustment(Document):
# 	# begin: auto-generated types
# 	# This code is auto-generated. Do not modify anything in this block.

# 	from typing import TYPE_CHECKING

# 	if TYPE_CHECKING:
# 		from erpnext.fleet_management.doctype.hsd_adjustment_item.hsd_adjustment_item import HSDAdjustmentItem
# 		from frappe.types import DF

# 		amended_from: DF.Link | None
# 		branch: DF.Link
# 		date: DF.Date
# 		items: DF.Table[HSDAdjustmentItem]
# 		posting_time: DF.ReadOnly
# 	# end: auto-generated types
# 	def validate(self):
# 		self.check_mandatory_fields()

# 	def check_mandatory_fields(self):
# 		for a in self.items:
# 			e_no, hsd_type, branch = frappe.db.get_value("Equipment", a.equipment, ["registration_number", "hsd_type", "branch"])
# 			if branch != self.branch:
# 				frappe.throw("Equipment <b>"+str(a.equipment)+"</b> doesn't belong to " + str(self.branch))
# 			a.registration_number = e_no
# 			a.hsd_type = hsd_type
# 			if not hsd_type:
# 				frappe.throw("HSD Type for Equipment is Mandatory on row "+ str(a.idx) +". Please set it in the Equipment Master")
# 			else:
# 				item_name = frappe.db.get_value("Item", a.hsd_type, "item_name")
# 				a.hsd_name = item_name
# 			if a.balance < 0:
# 				frappe.throw("Balance Quantity cannot be less than 0")

# 	def on_submit(self):
# 		self.make_pol_entry()

# 	def make_pol_entry(self):	
# 		for a in self.items:
# 			received = get_pol_tills("Receive", a.equipment, self.date, a.hsd_type)
# 			consumed = get_pol_consumed_tills(a.equipment)
# 			# actual_receive = flt(a.balance) + flt(consumed)
# 			# qty = flt(actual_receive) - flt(received)
# 			actual_receive = flt(a.balance) + flt(consumed)
# 			qty = flt(actual_receive) - flt(received)
	
# 			con = frappe.new_doc("POL Entry")
# 			con.flags.ignore_permissions = 1	
# 			con.equipment = a.equipment
# 			con.pol_type = a.hsd_type
# 			con.branch = self.branch
# 			con.date = self.date
# 			con.posting_time = self.posting_time
# 			con.qty = qty
# 			con.reference_type = "HSD Adjustment"
# 			con.reference_name = self.name
# 			con.is_opening = 1
# 			con.own_cost_center = 1
# 			con.type = "Receive"
# 			con.submit()

# 	def on_cancel(self):
# 		self.cancel_pol_entry()

# 	def cancel_pol_entry(self):
# 		frappe.db.sql("delete from `tabPOL Entry` where reference_name = %s", self.name)


# 	@frappe.whitelist()
# 	def get_equipments(self):
# 		if not self.branch:
# 			frappe.throw("Select the Branch first")
# 		if not self.date:
# 			frappe.throw("Select a valid date")
		
# 		# Fetch equipment and HSD name based on branch and date
# 		query = """
# 			SELECT 
# 				eq.name AS equipment, 
# 				eq.registration_number, 
# 				eq.hsd_type, 
# 				item.item_name AS hsd_name
# 			FROM 
# 				`tabEquipment` eq
# 			LEFT JOIN 
# 				`tabItem` item 
# 			ON 
# 				eq.hsd_type = item.name
# 			WHERE 
# 				eq.is_disabled = 0 
# 				AND eq.branch = %(branch)s 
# 				AND eq.creation <= %(date)s
# 		"""
# 		entries = frappe.db.sql(query, {"branch": self.branch, "date": self.date}, as_dict=True)
		
# 		# Clear and populate the items table
# 		self.set('items', [])
# 		for d in entries:
# 			d["balance"] = 0
# 			row = self.append('items', {})
# 			row.update(d)



# # System Balance for from_equipment
# @frappe.whitelist()	
# def get_tank_data(equipment, equipment_branch=None, tanker_adjustment=0):
# 	"""
# 	Fetch equipment balance details based on the provided parameters.
# 	"""
# 	# frappe.throw("Fetching Equipment Data")
# 	data = []

# 	# Query to fetch equipment details
# 	query = """
# 		SELECT e.name, e.branch, e.registration_number, e.hsd_type, e.equipment_type
# 		FROM `tabEquipment` e
# 		JOIN `tabEquipment Type` et ON e.equipment_type = et.name
# 		WHERE 1=1
# 	"""

# 	if equipment_branch:
# 		query += " AND e.equipment_branch = %(equipment_branch)s"
# 	if equipment:
# 		query += " AND e.name = %(equipment)s"

# 	query += " ORDER BY e.branch"

# 	# Query to fetch items
# 	items = frappe.db.sql("""
# 		SELECT item_code, item_name, stock_uom 
# 		FROM `tabItem`
# 		WHERE is_hsd_item = 1 AND disabled = 0
# 	""", as_dict=True)

# 	equipment_details = frappe.db.sql(query, {
# 		'equipment_branch': equipment_branch,
# 		'equipment': equipment
# 	}, as_dict=True)

# 	for eq in equipment_details:
# 		for item in items:
# 			received = issued = 0

# 			if equipment:
# 				if tanker_adjustment == 1:
# 					# Tanker adjustment logic
# 					received = get_pol_tills("Stock", eq.name, item.item_code)
# 					issued = get_pol_tills("Issue", eq.name, item.item_code)
# 				if tanker_adjustment != 1:
# 					# Standard equipment adjustment logic
# 					received = get_pol_tills("Receive", eq.name, item.item_code)
# 					issued = get_pol_consumed_tills(eq.name)
# 			else:
# 				received = get_pol_tills("Stock", eq.name, item.item_code)
# 				issued = get_pol_tills("Issue", eq.name, item.item_code)	

# 			# Append balance details
# 			if received or issued:
# 				data.append({
# 					'received': received,
# 					'issued': issued,
# 					'balance': flt(received) - flt(issued)
# 				})

# 	return data



# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe.model.document import Document
#from frappe.utils import flt
from frappe.utils import flt, getdate, nowdate, nowtime

from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import (
    get_pol_consumed_tills,
    get_pol_consumed_tills_op,
    get_pol_till,
    get_pol_tills,
    get_pol_consumed_till,
    get_pol_transfer,
)


class HSDAdjustment(Document):

    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.fleet_management.doctype.hsd_adjustment_item.hsd_adjustment_item import HSDAdjustmentItem
        from frappe.types import DF

        amended_from: DF.Link | None
        branch: DF.Link
        date: DF.Date
        items: DF.Table[HSDAdjustmentItem]
        posting_time: DF.Time
    # end: auto-generated types

    def validate(self):
        self.check_mandatory_fields()
        self.set_system_balance()

    def check_mandatory_fields(self):
        for a in self.items:
            if not a.equipment:
                frappe.throw(
                    "Equipment is mandatory on row " + str(a.idx)
                )

            equipment_data = frappe.db.get_value(
                "Equipment",
                a.equipment,
                ["registration_number", "hsd_type", "branch"],
                as_dict=True
            )

            if not equipment_data:
                frappe.throw(
                    "Equipment <b>" + str(a.equipment)
                    + "</b> does not exist."
                )

            e_no = equipment_data.registration_number
            hsd_type = equipment_data.hsd_type
            branch = equipment_data.branch

            if branch != self.branch:
                frappe.throw(
                    "Equipment <b>" + str(a.equipment)
                    + "</b> doesn't belong to " + str(self.branch)
                )

            a.registration_number = e_no
            a.hsd_type = hsd_type

            if not hsd_type:
                frappe.throw(
                    "HSD Type for Equipment is Mandatory on row "
                    + str(a.idx)
                    + ". Please set it in the Equipment Master"
                )

            a.hsd_name = frappe.db.get_value(
                "Item",
                hsd_type,
                "item_name"
            )

            if flt(a.balance) < 0:
                frappe.throw(
                    "Balance Quantity cannot be less than 0"
                )




    # def get_system_balance_for_equipment(self, equipment, hsd_type):
    #     if not equipment or not hsd_type or not self.date:
    #         return 0
    #     equipment_hsd_type = frappe.db.get_value(
    #         "Equipment", equipment, "hsd_type"
    #     )
    #     if equipment_hsd_type != hsd_type:
    #         return 0
    #     opening = frappe.db.sql(
    #         """
    #         SELECT posting_date, qty
    #         FROM `tabPOL Entry`
    #         WHERE docstatus = 1
    #         AND is_opening = 1
    #         AND equipment = %s
    #         AND pol_type = %s
    #         AND posting_date <= %s
    #         ORDER BY posting_date DESC, creation DESC
    #         LIMIT 1
    #         """,
    #         (equipment, hsd_type, self.date),
    #         as_dict=True,
    #     )
    #     if opening:
    #         opening_date = getdate(opening[0].posting_date)
    #         opening_qty = flt(opening[0].qty)
    #         received = frappe.db.sql(
    #             """
    #             SELECT COALESCE(SUM(qty), 0)
    #             FROM `tabPOL Entry`
    #             WHERE docstatus = 1
    #             AND type = 'Receive'
    #             AND equipment = %s
    #             AND pol_type = %s
	# 			AND posting_date > %s
    #             AND posting_date <= %s
	# 			AND IFNULL(is_opening, 0) = 0
    #             """,
    #             (equipment, hsd_type, opening_date, self.date),
    #         )[0][0] or 0
    #         consumed = frappe.db.sql(
    #             """
    #             SELECT COALESCE(SUM(consumption), 0)
    #             FROM `tabVehicle Logbook`
    #             WHERE docstatus = 1
    #             AND equipment = %s
    #             AND to_date > %s
    #             AND to_date <= %s
    #             """,
    #             (equipment, opening_date, self.date),
    #         )[0][0] or 0
    #         transferred = frappe.db.sql(
    #         	"""
    #         	SELECT COALESCE(SUM(qty), 0)
    #         	FROM `tabPOL Entry`
    #         	WHERE docstatus = 1
    #           	AND type = 'Transfer'
    #           	AND equipment = %s
    #           	AND pol_type = %s
    #           	AND posting_date > %s
    #          	AND posting_date <= %s
    #           	AND IFNULL(is_opening, 0) = 0
    #         	""",
    #         	(equipment, hsd_type, opening_date, self.date),
    #     	)[0][0] or 0
    #     return (
    #         opening_qty
    #         + flt(received)
    #         - flt(consumed)
    #         - flt(transferred)
    #     )
    #     received = get_pol_tills(
    #    		"Receive", equipment, hsd_type, self.date
    # 	)
    #     consumed = get_pol_consumed_till(
    #    		equipment, self.date
    # 	)
    #     transferred = get_pol_transfer(
    #         "Transfer", equipment, self.date, hsd_type
    # 	)
    #     return (
    #     	flt(received)
    #    	 - flt(consumed)
    #    	 - flt(transferred)
    # 	)
    
    
    def get_system_balance_for_equipment(self, equipment, hsd_type):
        """
        Calculate system balance using the same logic as POL Issue.

        If an opening exists:
            Latest opening qty
            + Receive/Stock after opening
            - Issue after opening

        If no opening exists:
            Total Receive/Stock - Total consumption
        """

        if not equipment or not hsd_type or not self.date:
            return 0

        equipment_hsd_type = frappe.db.get_value(
            "Equipment",
            equipment,
            "hsd_type"
        )

        if equipment_hsd_type != hsd_type:
            return 0

        adjustment_date = getdate(self.date)
        adjustment_time = str(self.posting_time or "23:59:59")

        # ---------------------------------------------------------
        # 1. Get the latest opening entry up to adjustment date/time
        # ---------------------------------------------------------

        opening_rows = frappe.db.sql(
            """
            SELECT
                name,
                qty,
                posting_date,
                posting_time,
                creation
            FROM `tabPOL Entry`
            WHERE docstatus = 1
                AND IFNULL(is_opening, 0) = 1
                AND equipment = %s
                AND pol_type = %s
                AND (
                    posting_date < %s
                    OR (
                        posting_date = %s
                        AND IFNULL(posting_time, '00:00:00') <= %s
                    )
                )
            ORDER BY
                posting_date DESC,
                IFNULL(posting_time, '00:00:00') DESC,
                creation DESC,
                name DESC
            LIMIT 1
            """,
            (
                equipment,
                hsd_type,
                adjustment_date,
                adjustment_date,
                adjustment_time,
            ),
            as_dict=True
        )

        opening_exists = bool(opening_rows)

        # ---------------------------------------------------------
        # 2. Prepare movement cutoff
        # ---------------------------------------------------------

        movement_cutoff = ""

        params = {
            "equipment": equipment,
            "hsd_type": hsd_type,
            "adjustment_date": adjustment_date,
            "adjustment_time": adjustment_time,
        }

        opening_qty = 0

        if opening_exists:
            opening = opening_rows[0]
            opening_qty = flt(opening.qty)

            opening_time = str(
                opening.posting_time or "00:00:00"
            )

            # Only movements after the exact latest opening entry.
            movement_cutoff = """
                AND (
                    posting_date > %(opening_date)s
                    OR (
                        posting_date = %(opening_date)s
                        AND (
                            IFNULL(posting_time, '00:00:00')
                                > %(opening_time)s
                            OR (
                                IFNULL(posting_time, '00:00:00')
                                    = %(opening_time)s
                                AND (
                                    creation > %(opening_creation)s
                                    OR (
                                        creation = %(opening_creation)s
                                        AND name > %(opening_name)s
                                    )
                                )
                            )
                        )
                    )
                )
            """

            params.update({
                "opening_date": opening.posting_date,
                "opening_time": opening_time,
                "opening_creation": opening.creation,
                "opening_name": opening.name,
            })

        # ---------------------------------------------------------
        # 3. Calculate POL Entry movements
        # ---------------------------------------------------------

        movements = frappe.db.sql(
            """
            SELECT
                COALESCE(SUM(
                    CASE
                        WHEN type IN ('Receive', 'Stock') THEN qty
                        ELSE 0
                    END
                ), 0) AS received,

                COALESCE(SUM(
                    CASE
                        WHEN type = 'Issue' THEN qty
                        ELSE 0
                    END
                ), 0) AS consumed

            FROM `tabPOL Entry`
            WHERE docstatus = 1
                AND equipment = %(equipment)s
                AND pol_type = %(hsd_type)s
                AND IFNULL(is_opening, 0) = 0
                AND (
                    posting_date < %(adjustment_date)s
                    OR (
                        posting_date = %(adjustment_date)s
                        AND IFNULL(posting_time, '00:00:00')
                            <= %(adjustment_time)s
                    )
                )
            """ + movement_cutoff,
            params,
            as_dict=True
        )[0]

        received = flt(movements.received)

        # ---------------------------------------------------------
        # 4. Calculate final balance
        # ---------------------------------------------------------

        if opening_exists:
            # Same approach as POL Issue when an opening exists.
            consumed = flt(
                get_pol_consumed_tills_op(
                    equipment=equipment,
                    opening_date=opening.posting_date,
                    posting_date=adjustment_date,
                )
            )

            balance = (
                flt(opening_qty)
                + flt(received)
                - flt(consumed)
            )

        else:
            # Preserve the existing POL Issue logic when no opening
            # exists. This helper calculates Vehicle Logbook consumption.
            consumed = flt(
                get_pol_consumed_tills(equipment)
            )

            balance = (
                flt(received)
                - flt(consumed)

            )

        return flt(balance)    






    def set_system_balance(self):
        """
        Recalculate system_balance during validation.
        """

        for row in self.items:
            row.system_balance = self.get_system_balance_for_equipment(
                row.equipment,
                row.hsd_type
            )

    def on_submit(self):
        self.make_pol_entry()

    def make_pol_entry(self):
        for a in self.items:
            received = get_pol_tills(
                "Receive",
                a.equipment,
                self.date,
                a.hsd_type
            )

            consumed = get_pol_consumed_tills(
                a.equipment
            )

            # actual_receive = flt(a.balance) + flt(consumed)
            # qty = flt(actual_receive) - flt(received)
            actual_receive = flt(a.balance)
            qty = flt(actual_receive) - flt(received)

            con = frappe.new_doc("POL Entry")
            con.flags.ignore_permissions = 1
            con.equipment = a.equipment
            con.pol_type = a.hsd_type
            con.branch = self.branch
            con.date = self.date
            con.posting_date = self.date
            
            con.posting_time = self.posting_time
            con.qty = qty
            con.reference_type = "HSD Adjustment"
            con.reference_name = self.name
            con.is_opening = 1
            con.own_cost_center = 1
            con.type = "Receive"
            con.submit()

    def on_cancel(self):
        self.cancel_pol_entry()

    def cancel_pol_entry(self):
        frappe.db.sql(
            """
            DELETE FROM `tabPOL Entry`
            WHERE reference_name = %s
            """,
            self.name
        )

    @frappe.whitelist()
    def get_equipments(self):
        if not self.branch:
            frappe.throw("Select the Branch first")

        if not self.date:
            frappe.throw("Select a valid date")

        query = """
            SELECT
                eq.name AS equipment,
                eq.registration_number,
                eq.hsd_type,
                item.item_name AS hsd_name,
                eq.equipment_type
            FROM `tabEquipment` eq
            LEFT JOIN `tabItem` item
                ON eq.hsd_type = item.name
            WHERE
                eq.is_disabled = 0
                AND eq.branch = %(branch)s
                AND eq.creation < DATE_ADD(
                    %(date)s, INTERVAL 1 DAY
                )
            ORDER BY eq.name
        """

        entries = frappe.db.sql(
            query,
            {
                "branch": self.branch,
                "date": self.date
            },
            as_dict=True
        )

        # Clear existing rows
        self.set("items", [])

        for d in entries:
            row = self.append("items", {})

            row.equipment = d.equipment
            row.registration_number = d.registration_number
            row.hsd_type = d.hsd_type
            row.hsd_name = d.hsd_name
            row.balance = 0

            # Calculate system balance immediately in Python
            row.system_balance = self.get_system_balance_for_equipment(
                d.equipment,
                d.hsd_type
            )

        return self.items


# Existing equipment tank data method
@frappe.whitelist()
def get_tank_data(
    equipment,
    equipment_branch=None,
    tanker_adjustment=0
):
    data = []

    query = """
        SELECT
            e.name,
            e.branch,
            e.registration_number,
            e.hsd_type,
            e.equipment_type
        FROM `tabEquipment` e
        JOIN `tabEquipment Type` et
            ON e.equipment_type = et.name
        WHERE 1=1
    """

    if equipment_branch:
        query += " AND e.equipment_branch = %(equipment_branch)s"

    if equipment:
        query += " AND e.name = %(equipment)s"

    query += " ORDER BY e.branch"

    items = frappe.db.sql(
        """
        SELECT
            item_code,
            item_name,
            stock_uom
        FROM `tabItem`
        WHERE
            is_hsd_item = 1
            AND disabled = 0
        """,
        as_dict=True
    )

    equipment_details = frappe.db.sql(
        query,
        {
            "equipment_branch": equipment_branch,
            "equipment": equipment
        },
        as_dict=True
    )

    for eq in equipment_details:
        for item in items:
            received = 0
            issued = 0

            if equipment:
                if int(tanker_adjustment or 0) == 1:
                    received = get_pol_tills(
                        "Stock",
                        eq.name,
                        item.item_code
                    )

                    issued = get_pol_tills(
                        "Issue",
                        eq.name,
                        item.item_code
                    )
                else:
                    received = get_pol_tills(
                        "Receive",
                        eq.name,
                        item.item_code
                    )

                    issued = get_pol_consumed_tills(
                        eq.name
                    )
            else:
                received = get_pol_tills(
                    "Stock",
                    eq.name,
                    item.item_code
                )

                issued = get_pol_tills(
                    "Issue",
                    eq.name,
                    item.item_code
                )

            if received or issued:
                data.append({
                    "received": received,
                    "issued": issued,
                    "balance": (
                        flt(received) - flt(issued)
                    )
                })

    return data
