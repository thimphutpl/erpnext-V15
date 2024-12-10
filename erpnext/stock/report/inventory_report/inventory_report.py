# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, today, add_days


from operator import itemgetter
from typing import Any, TypedDict

import frappe
from frappe import _
from frappe.query_builder import Order
from frappe.query_builder.functions import Coalesce
from frappe.utils import add_days, cint, date_diff, flt, getdate
from frappe.utils.nestedset import get_descendants_of

import erpnext
from erpnext.stock.doctype.inventory_dimension.inventory_dimension import get_inventory_dimensions
from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter
from erpnext.stock.report.stock_ageing.stock_ageing import FIFOSlots, get_average_age
from erpnext.stock.utils import add_additional_uom_columns

class StockBalanceFilter(TypedDict):
    company: str | None
    from_date: str
    to_date: str
    item_group: str | None
    item: str | None
    warehouse: str | None
    warehouse_type: str | None
    include_uom: str | None  # include extra info in converted UOM
    show_stock_ageing_data: bool
    show_variant_attributes: bool

SLEntry = dict[str, Any]

def execute(filters: StockBalanceFilter | None = None):
    selected_report = filters.get('report_type', 'Inventory Report')

    if selected_report == "Inventory Report":
        stock_balance_report = StockBalanceReport(filters)
        columns, data = stock_balance_report.run()
    elif selected_report == "Inventory Summary":
        columns, data = get_inventory_summary_data()
    elif selected_report == "Non Moving Branch Wise":
        columns, data = get_non_moving_branch_data()
    else:
        columns, data = get_report_4_data()

    return columns, data


class StockBalanceReport:
    def __init__(self, filters: StockBalanceFilter | None) -> None:
        self.filters = filters
        self.from_date = getdate(filters.get("from_date"))
        self.to_date = getdate(filters.get("to_date"))

        self.start_from = None
        self.data = []
        self.columns = []
        self.sle_entries: list[SLEntry] = []
        self.set_company_currency()

    def set_company_currency(self) -> None:
        if self.filters.get("company"):
            self.company_currency = erpnext.get_company_currency(self.filters.get("company"))
        else:
            self.company_currency = frappe.db.get_single_value("Global Defaults", "default_currency")

    def run(self):
        self.float_precision = cint(frappe.db.get_default("float_precision")) or 3

        self.inventory_dimensions = self.get_inventory_dimension_fields()
        self.prepare_opening_data_from_closing_balance()
        self.prepare_stock_ledger_entries()
        self.prepare_new_data()

        if not self.columns:
            self.columns = self.get_columns()

        self.add_additional_uom_columns()

        return self.columns, self.data

    def prepare_opening_data_from_closing_balance(self) -> None:
        self.opening_data = frappe._dict({})

        closing_balance = self.get_closing_balance()
        if not closing_balance:
            return

        self.start_from = add_days(closing_balance[0].to_date, 1)
        res = frappe.get_doc("Closing Stock Balance", closing_balance[0].name).get_prepared_data()

        for entry in res.data:
            entry = frappe._dict(entry)

            group_by_key = self.get_group_by_key(entry)
            if group_by_key not in self.opening_data:
                self.opening_data.setdefault(group_by_key, entry)

    def prepare_new_data(self):
        self.item_warehouse_map = self.get_item_warehouse_map()

        if self.filters.get("show_stock_ageing_data"):
            self.filters["show_warehouse_wise_stock"] = True
            item_wise_fifo_queue = FIFOSlots(self.filters, self.sle_entries).generate()

        _func = itemgetter(1)

        del self.sle_entries

        sre_details = self.get_sre_reserved_qty_details()

        variant_values = {}
        if self.filters.get("show_variant_attributes"):
            variant_values = self.get_variant_values_for()

        for _key, report_data in self.item_warehouse_map.items():
            if variant_data := variant_values.get(report_data.item_code):
                report_data.update(variant_data)

            if self.filters.get("show_stock_ageing_data"):
                opening_fifo_queue = self.get_opening_fifo_queue(report_data) or []

                fifo_queue = []
                if fifo_queue := item_wise_fifo_queue.get((report_data.item_code, report_data.warehouse)):
                    fifo_queue = fifo_queue.get("fifo_queue")

                if fifo_queue:
                    opening_fifo_queue.extend(fifo_queue)

                stock_ageing_data = {"average_age": 0, "earliest_age": 0, "latest_age": 0}
                if opening_fifo_queue:
                    fifo_queue = sorted(filter(_func, opening_fifo_queue), key=_func)
                    if not fifo_queue:
                        continue

                    to_date = self.to_date
                    stock_ageing_data["average_age"] = get_average_age(fifo_queue, to_date)
                    stock_ageing_data["earliest_age"] = date_diff(to_date, fifo_queue[0][1])
                    stock_ageing_data["latest_age"] = date_diff(to_date, fifo_queue[-1][1])
                    stock_ageing_data["fifo_queue"] = fifo_queue

                report_data.update(stock_ageing_data)

            report_data.update(
                {"reserved_stock": sre_details.get((report_data.item_code, report_data.warehouse), 0.0)}
            )

            if (
                not self.filters.get("include_zero_stock_items")
                and report_data
                and report_data.bal_qty == 0
                and report_data.bal_val == 0
            ):
                continue

            self.data.append(report_data)

    def get_item_warehouse_map(self):
        item_warehouse_map = {}
        self.opening_vouchers = self.get_opening_vouchers()

        if self.filters.get("show_stock_ageing_data"):
            self.sle_entries = self.sle_query.run(as_dict=True)

		# HACK: This is required to avoid causing db query in flt
        _system_settings = frappe.get_cached_doc("System Settings")
        with frappe.db.unbuffered_cursor():
            if not self.filters.get("show_stock_ageing_data"):
                self.sle_entries = self.sle_query.run(as_dict=True, as_iterator=True)

            for entry in self.sle_entries:
                group_by_key = self.get_group_by_key(entry)
                if group_by_key not in item_warehouse_map:
                    self.initialize_data(item_warehouse_map, group_by_key, entry)

                self.prepare_item_warehouse_map(item_warehouse_map, entry, group_by_key)

                if self.opening_data.get(group_by_key):
                    del self.opening_data[group_by_key]

        for group_by_key, entry in self.opening_data.items():
            if group_by_key not in item_warehouse_map:
                self.initialize_data(item_warehouse_map, group_by_key, entry)

        item_warehouse_map = filter_items_with_no_transactions(
            item_warehouse_map, self.float_precision, self.inventory_dimensions
        )

        return item_warehouse_map

    def get_sre_reserved_qty_details(self) -> dict:
        from erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry import (
            get_sre_reserved_qty_for_items_and_warehouses as get_reserved_qty_details,
        )

        item_code_list, warehouse_list = [], []
        for d in self.item_warehouse_map:
            item_code_list.append(d[1])
            warehouse_list.append(d[2])

        return get_reserved_qty_details(item_code_list, warehouse_list)

    def prepare_item_warehouse_map(self, item_warehouse_map, entry, group_by_key):
        qty_dict = item_warehouse_map[group_by_key]
        for field in self.inventory_dimensions:
            qty_dict[field] = entry.get(field)

        if entry.voucher_type == "Stock Reconciliation" and (not entry.batch_no or entry.serial_no):
            qty_diff = flt(entry.qty_after_transaction) - flt(qty_dict.bal_qty)
        else:
            qty_diff = flt(entry.actual_qty)

        value_diff = flt(entry.stock_value_difference)

        if entry.posting_date < self.from_date or entry.voucher_no in self.opening_vouchers.get(
            entry.voucher_type, []
        ):
            qty_dict.opening_qty += qty_diff
            qty_dict.opening_val += value_diff

        elif entry.posting_date >= self.from_date and entry.posting_date <= self.to_date:
            if flt(qty_diff, self.float_precision) >= 0:
                qty_dict.in_qty += qty_diff
                qty_dict.in_val += value_diff
            else:
                qty_dict.out_qty += abs(qty_diff)
                qty_dict.out_val += abs(value_diff)

        qty_dict.val_rate = entry.valuation_rate
        qty_dict.bal_qty += qty_diff
        qty_dict.bal_val += value_diff

        # Additional calculations for consumption, value, and movement type
        opening_receipt = qty_dict.opening_qty + qty_dict.in_qty
        issue_value = qty_dict.out_qty
        consumption = (opening_receipt / issue_value) if issue_value else 0
        # stock_value = (opening_receipt - issue_value) * (entry.valuation_rate or 0)

        # movement = (
        #     "Fast Moving" if consumption > 0.6 else 
        #     "Slow Moving" if consumption > 0 else 
        #     "No Moving"
        # )

        # # Update the item warehouse map with additional details
        # qty_dict.update({
        #     "consumption": consumption,
        #     # "value": stock_value,
        #     "movement": movement,
        # })
        # Update dictionary with Nature of Movement
        nature_of_movement = (
            "Fast Moving" if consumption > 0.6 else
            "Slow Moving" if 0 < consumption <= 0.6 else
            "No Moving"
        )
        qty_dict.update({
            "consumption": consumption,
            "nature_of_movement": nature_of_movement,
        })

    def initialize_data(self, item_warehouse_map, group_by_key, entry):
        opening_data = self.opening_data.get(group_by_key, {})

        item_warehouse_map[group_by_key] = frappe._dict(
            {
                "item_code": entry.item_code,
                "warehouse": entry.warehouse,
                "item_group": entry.item_group,
                "company": entry.company,
                "currency": self.company_currency,
                "stock_uom": entry.stock_uom,
                "item_name": entry.item_name,
                "opening_qty": opening_data.get("bal_qty") or 0.0,
                "opening_val": opening_data.get("bal_val") or 0.0,
                "opening_fifo_queue": opening_data.get("fifo_queue") or [],
                "in_qty": 0.0,
                "in_val": 0.0,
                "out_qty": 0.0,
                "out_val": 0.0,
                "bal_qty": opening_data.get("bal_qty") or 0.0,
                "bal_val": opening_data.get("bal_val") or 0.0,
                "val_rate": 0.0,
            }
        )

    def get_group_by_key(self, row) -> tuple:
        group_by_key = [row.company, row.item_code, row.warehouse]

        for fieldname in self.inventory_dimensions:
            if self.filters.get(fieldname):
                group_by_key.append(row.get(fieldname))

        return tuple(group_by_key)

    def get_closing_balance(self) -> list[dict[str, Any]]:
        if self.filters.get("ignore_closing_balance"):
            return []

        table = frappe.qb.DocType("Closing Stock Balance")

        query = (
            frappe.qb.from_(table)
            .select(table.name, table.to_date)
            .where(
                (table.docstatus == 1)
                & (table.company == self.filters.company)
                & (table.to_date <= self.from_date)
                & (table.status == "Completed")
            )
            .orderby(table.to_date, order=Order.desc)
            .limit(1)
        )

        for fieldname in ["warehouse", "item_code", "item_group", "warehouse_type"]:
            if self.filters.get(fieldname):
                query = query.where(table[fieldname] == self.filters.get(fieldname))

        return query.run(as_dict=True)

    def prepare_stock_ledger_entries(self):
        sle = frappe.qb.DocType("Stock Ledger Entry")
        item_table = frappe.qb.DocType("Item")

        query = (
            frappe.qb.from_(sle)
            .inner_join(item_table)
            .on(sle.item_code == item_table.name)
            .select(
                sle.item_code,
                sle.warehouse,
                sle.posting_date,
                sle.actual_qty,
                sle.valuation_rate,
                sle.company,
                sle.voucher_type,
                sle.qty_after_transaction,
                sle.stock_value_difference,
                sle.item_code.as_("name"),
                sle.voucher_no,
                sle.stock_value,
                sle.batch_no,
                sle.serial_no,
                sle.serial_and_batch_bundle,
                sle.has_serial_no,
                item_table.item_group,
                item_table.stock_uom,
                item_table.item_name,
            )
            .where((sle.docstatus < 2) & (sle.is_cancelled == 0))
            .orderby(sle.posting_datetime)
            .orderby(sle.creation)
            .orderby(sle.actual_qty)
        )

        query = self.apply_inventory_dimensions_filters(query, sle)
        query = self.apply_warehouse_filters(query, sle)
        query = self.apply_items_filters(query, item_table)
        query = self.apply_date_filters(query, sle)

        if self.filters.get("company"):
            query = query.where(sle.company == self.filters.get("company"))

        self.sle_query = query

    def apply_inventory_dimensions_filters(self, query, sle) -> str:
        inventory_dimension_fields = self.get_inventory_dimension_fields()
        if inventory_dimension_fields:
            for fieldname in inventory_dimension_fields:
                query = query.select(fieldname)
                if self.filters.get(fieldname):
                    query = query.where(sle[fieldname].isin(self.filters.get(fieldname)))

        return query

    def apply_warehouse_filters(self, query, sle) -> str:
        warehouse_table = frappe.qb.DocType("Warehouse")

        if self.filters.get("warehouse"):
            query = apply_warehouse_filter(query, sle, self.filters)
        elif warehouse_type := self.filters.get("warehouse_type"):
            query = (
                query.join(warehouse_table)
                .on(warehouse_table.name == sle.warehouse)
                .where(warehouse_table.warehouse_type == warehouse_type)
            )

        return query

    def apply_items_filters(self, query, item_table) -> str:
        if item_group := self.filters.get("item_group"):
            children = get_descendants_of("Item Group", item_group, ignore_permissions=True)
            query = query.where(item_table.item_group.isin([*children, item_group]))

        for field in ["item_code", "brand"]:
            if not self.filters.get(field):
                continue
            elif field == "item_code":
                query = query.where(item_table.name == self.filters.get(field))
            else:
                query = query.where(item_table[field] == self.filters.get(field))

        return query

    def apply_date_filters(self, query, sle) -> str:
        if not self.filters.ignore_closing_balance and self.start_from:
            query = query.where(sle.posting_date >= self.start_from)

        if self.to_date:
            query = query.where(sle.posting_date <= self.to_date)

        return query

    def get_columns(self):
        columns = [
            {
                "label": _("Item"),
                "fieldname": "item_code",
                "fieldtype": "Link",
                "options": "Item",
                "width": 100,
            },
            {"label": _("Item Name"), "fieldname": "item_name", "width": 150},
            {
                "label": _("Item Group"),
                "fieldname": "item_group",
                "fieldtype": "Link",
                "options": "Item Group",
                "width": 100,
            },
            # {
            #     "label": _("Warehouse"),
            #     "fieldname": "warehouse",
            #     "fieldtype": "Link",
            #     "options": "Warehouse",
            #     "width": 100,
            # },
        ]

        for dimension in get_inventory_dimensions():
            columns.append(
                {
                    "label": _(dimension.doctype),
                    "fieldname": dimension.fieldname,
                    "fieldtype": "Link",
                    "options": dimension.doctype,
                    "width": 110,
                }
            )

        columns.extend(
            [
                # {
                #     "label": _("Stock UOM"),
                #     "fieldname": "stock_uom",
                #     "fieldtype": "Link",
                #     "options": "UOM",
                #     "width": 90,
                # },
                {
                    "label": _("Balance Qty"),
                    "fieldname": "bal_qty",
                    "fieldtype": "Float",
                    "width": 100,
                    "convertible": "qty",
                },
                {
                    "label": _("Balance Value"),
                    "fieldname": "bal_val",
                    "fieldtype": "Currency",
                    "width": 100,
                    "options": "Company:company:default_currency",
                },
                {
                    "label": _("Opening Qty"),
                    "fieldname": "opening_qty",
                    "fieldtype": "Float",
                    "width": 100,
                    "convertible": "qty",
                },
                {
                    "label": _("Opening Value"),
                    "fieldname": "opening_val",
                    "fieldtype": "Currency",
                    "width": 110,
                    "options": "Company:company:default_currency",
                },
                {
                    "label": _("In Qty"),
                    "fieldname": "in_qty",
                    "fieldtype": "Float",
                    "width": 80,
                    "convertible": "qty",
                },
                {"label": _("In Value"), "fieldname": "in_val", "fieldtype": "Float", "width": 80},
                {
                    "label": _("Out Qty"),
                    "fieldname": "out_qty",
                    "fieldtype": "Float",
                    "width": 80,
                    "convertible": "qty",
                },
                {"label": _("Out Value"), "fieldname": "out_val", "fieldtype": "Float", "width": 80},
                {
                    "label": _("Valuation Rate"),
                    "fieldname": "val_rate",
                    "fieldtype": self.filters.valuation_field_type or "Currency",
                    "width": 90,
                    "convertible": "rate",
                    "options": "Company:company:default_currency"
                    if self.filters.valuation_field_type == "Currency"
                    else None,
                },
                # {
                #     "label": _("Reserved Stock"),
                #     "fieldname": "reserved_stock",
                #     "fieldtype": "Float",
                #     "width": 80,
                #     "convertible": "qty",
                # },
                # {
                #     "label": _("Company"),
                #     "fieldname": "company",
                #     "fieldtype": "Link",
                #     "options": "Company",
                #     "width": 100,
                # },
                {
                    "label": _("Consumption"),
                    "fieldname": "consumption",
                    "fieldtype": "float",
                    "width": 100,
                },
                {
                    "label": _("Category"),
                    "fieldname": "category",
                    "fieldtype": "Data",
                    "width": 100,
                },
                {
                    "label": _("Nature of Movement"),
                    "fieldname": "movement",
                    "fieldtype": "Data",
                    "width": 100,
                },
            ]
        )

        if self.filters.get("show_stock_ageing_data"):
            columns += [
                {"label": _("Average Age"), "fieldname": "average_age", "width": 100},
                {"label": _("Earliest Age"), "fieldname": "earliest_age", "width": 100},
                {"label": _("Latest Age"), "fieldname": "latest_age", "width": 100},
            ]

        if self.filters.get("show_variant_attributes"):
            columns += [
                {"label": att_name, "fieldname": att_name, "width": 100}
                for att_name in get_variants_attributes()
            ]

        return columns

    def add_additional_uom_columns(self):
        if not self.filters.get("include_uom"):
            return

        conversion_factors = self.get_itemwise_conversion_factor()
        add_additional_uom_columns(self.columns, self.data, self.filters.include_uom, conversion_factors)

    def get_itemwise_conversion_factor(self):
        items = []
        if self.filters.item_code or self.filters.item_group:
            items = [d.item_code for d in self.data]

        table = frappe.qb.DocType("UOM Conversion Detail")
        query = (
            frappe.qb.from_(table)
            .select(
                table.conversion_factor,
                table.parent,
            )
            .where((table.parenttype == "Item") & (table.uom == self.filters.include_uom))
        )

        if items:
            query = query.where(table.parent.isin(items))

        result = query.run(as_dict=1)
        if not result:
            return {}

        return {d.parent: d.conversion_factor for d in result}

    def get_variant_values_for(self):
        """Returns variant values for items."""
        attribute_map = {}
        items = []
        if self.filters.item_code or self.filters.item_group:
            items = [d.item_code for d in self.data]

        filters = {}
        if items:
            filters = {"parent": ("in", items)}

        attribute_info = frappe.get_all(
            "Item Variant Attribute",
            fields=["parent", "attribute", "attribute_value"],
            filters=filters,
        )

        for attr in attribute_info:
            attribute_map.setdefault(attr["parent"], {})
            attribute_map[attr["parent"]].update({attr["attribute"]: attr["attribute_value"]})

        return attribute_map

    def get_opening_vouchers(self):
        opening_vouchers = {"Stock Entry": [], "Stock Reconciliation": []}

        se = frappe.qb.DocType("Stock Entry")
        sr = frappe.qb.DocType("Stock Reconciliation")

        vouchers_data = (
            frappe.qb.from_(
                (
                    frappe.qb.from_(se)
                    .select(se.name, Coalesce("Stock Entry").as_("voucher_type"))
                    .where((se.docstatus == 1) & (se.posting_date <= self.to_date) & (se.is_opening == "Yes"))
                )
                + (
                    frappe.qb.from_(sr)
                    .select(sr.name, Coalesce("Stock Reconciliation").as_("voucher_type"))
                    .where(
                        (sr.docstatus == 1)
                        & (sr.posting_date <= self.to_date)
                        & (sr.purpose == "Opening Stock")
                    )
                )
            ).select("voucher_type", "name")
        ).run(as_dict=True)

        if vouchers_data:
            for d in vouchers_data:
                opening_vouchers[d.voucher_type].append(d.name)

        return opening_vouchers

    @staticmethod
    def get_inventory_dimension_fields():
        return [dimension.fieldname for dimension in get_inventory_dimensions()]

    @staticmethod
    def get_opening_fifo_queue(report_data):
        opening_fifo_queue = report_data.get("opening_fifo_queue") or []
        for row in opening_fifo_queue:
            row[1] = getdate(row[1])

        return opening_fifo_queue


def filter_items_with_no_transactions(
	iwb_map, float_precision: float, inventory_dimensions: list | None = None
):
	pop_keys = []
	for group_by_key in iwb_map:
		qty_dict = iwb_map[group_by_key]

		no_transactions = True
		for key, val in qty_dict.items():
			if inventory_dimensions and key in inventory_dimensions:
				continue

			if key in [
				"item_code",
				"warehouse",
				"item_name",
				"item_group",
				"project",
				"stock_uom",
				"company",
				"opening_fifo_queue",
			]:
				continue

			val = flt(val, float_precision)
			qty_dict[key] = val
			if key != "val_rate" and val:
				no_transactions = False

		if no_transactions:
			pop_keys.append(group_by_key)

	for key in pop_keys:
		iwb_map.pop(key)

	return iwb_map


def get_variants_attributes() -> list[str]:
	"""Return all item variant attributes."""
	return frappe.get_all("Item Attribute", pluck="name")













# Report 1 Data (Stock Ledger)
def get_inventory_report_data(filters):
    validate_filters(filters)

    from_date = filters["from_date"]
    to_date = filters["to_date"]

    columns = [
        {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Data"},
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data"},
        {"fieldname": "opening", "label": "Opening", "fieldtype": "Float"},
        {"fieldname": "receipt", "label": "Receipt", "fieldtype": "Float"},
        {"fieldname": "opening_receipt", "label": "Opening + Receipt", "fieldtype": "Float"},
        {"fieldname": "issue_value", "label": "Issue Value", "fieldtype": "Float"},
        {"fieldname": "valuation_rate", "label": "Valuation Rate", "fieldtype": "Float"},
        {"fieldname": "value", "label": "Value", "fieldtype": "Currency"},
        {"fieldname": "closing", "label": "Closing", "fieldtype": "Float"},
        {"fieldname": "consumption", "label": "Consumption", "fieldtype": "Float"},
        {"fieldname": "category", "label": "Category", "fieldtype": "Data"},
        {"fieldname": "movement", "label": "Nature of Movement", "fieldtype": "Data"},
    ]

    stock_entries = frappe.db.sql(f"""
        SELECT
            sle.item_code,
            i.item_name,
            SUM(CASE WHEN sle.posting_date < %(from_date)s THEN sle.actual_qty ELSE 0 END) AS opening_qty,
            SUM(CASE WHEN sle.posting_date BETWEEN %(from_date)s AND %(to_date)s AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) AS in_qty,
            SUM(CASE WHEN sle.posting_date BETWEEN %(from_date)s AND %(to_date)s AND sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END) AS out_qty,
            sle.valuation_rate,
            i.item_group AS category
        FROM `tabStock Ledger Entry` sle
        JOIN `tabItem` i ON i.name = sle.item_code
        WHERE sle.posting_date <= %(to_date)s
        GROUP BY sle.item_code
    """, {"from_date": from_date, "to_date": to_date}, as_dict=True)

    data = []
    total_opening_receipt = total_issue_value = total_value = 0
    total_items = 0

    for entry in stock_entries:
        opening = entry.opening_qty
        opening_receipt = opening + entry.in_qty
        issue_value = abs(entry.out_qty)
        closing = opening + (entry.in_qty - issue_value)
        consumption = (opening_receipt / issue_value) if issue_value else 0
        value = ((opening_receipt - issue_value) * entry.valuation_rate)

        movement = "Fast Moving" if consumption > 0.6 else "Slow Moving" if consumption > 0 else "No Moving"

        data.append({
            "item_code": entry.item_code,
            "item_name": entry.item_name,
            "opening": opening,
            "opening_receipt": opening_receipt,
            "issue_value": issue_value,
            "valuation_rate": entry.valuation_rate,
            "value": value,
            "closing": closing,
            "consumption": consumption,
            "category": entry.category,
            "movement": movement,
        })

        total_opening_receipt += opening_receipt
        total_issue_value += issue_value
        total_value += value
        total_items += 1

    if total_items > 0:
        average_valuation_rate = total_value / total_items
        data.append({
            "item_code": "TOTAL",
            "item_name": "",
            "opening": "",
            "opening_receipt": total_opening_receipt,
            "issue_value": total_issue_value,
            "valuation_rate": average_valuation_rate,
            "value": total_value,
            "closing": "",
            "consumption": "",
            "category": "",
            "movement": "",
        })

    return columns, data

def validate_filters(filters):
    required_fields = ["from_date", "to_date"]
    for field in required_fields:
        if not filters.get(field):
            frappe.throw(_("'{0}' is a required filter").format(field))

    # Optional: Validate filter formats (e.g., date ranges)
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))
    if from_date > to_date:
        frappe.throw(_("From Date cannot be after To Date."))



# Report 2
def get_inventory_summary_data():
    report_1_columns, report_1_data = get_inventory_report_data()

    summary = {
        "fast_moving": {"count": 0, "value": 0},
        "slow_moving": {"count": 0, "value": 0},
        "no_moving": {"count": 0, "value": 0},
    }
    total_items = 0
    total_value = 0

    for entry in report_1_data:
        total_items += 1
        total_value += entry["issue_value"]

        if entry["movement"] == "Fast Moving":
            summary["fast_moving"]["count"] += 1
            summary["fast_moving"]["value"] += entry["issue_value"]
        elif entry["movement"] == "Slow Moving":
            summary["slow_moving"]["count"] += 1
            summary["slow_moving"]["value"] += entry["issue_value"]
        else:
            summary["no_moving"]["count"] += 1
            summary["no_moving"]["value"] += entry["issue_value"]

    # Stock Balance should only include Fast and Slow Moving
    stock_balance_count = summary["fast_moving"]["count"] + summary["slow_moving"]["count"]
    stock_balance_value = summary["fast_moving"]["value"] + summary["slow_moving"]["value"]

    total_percent_items = 100
    total_percent_value = 100

    columns = [
        {"fieldname": "movement_type", "label": "Movement Type", "fieldtype": "Data"},
        {"fieldname": "num_items", "label": "Number of Items", "fieldtype": "Int"},
        {"fieldname": "item_percent", "label": "Item Percent", "fieldtype": "Percent"},
        {"fieldname": "total_value", "label": "Total Value", "fieldtype": "Float"},
        {"fieldname": "value_percent", "label": "Value Percent", "fieldtype": "Percent"}
    ]

    data = [
        {
            "movement_type": "Fast Moving",
            "num_items": summary["fast_moving"]["count"],
            "item_percent": (summary["fast_moving"]["count"] / total_items) * 100 if total_items else 0,
            "total_value": summary["fast_moving"]["value"],
            "value_percent": (summary["fast_moving"]["value"] / total_value) * 100 if total_value else 0
        },
        {
            "movement_type": "Slow Moving",
            "num_items": summary["slow_moving"]["count"],
            "item_percent": (summary["slow_moving"]["count"] / total_items) * 100 if total_items else 0,
            "total_value": summary["slow_moving"]["value"],
            "value_percent": (summary["slow_moving"]["value"] / total_value) * 100 if total_value else 0
        },
        {
            "movement_type": "No Moving",
            "num_items": summary["no_moving"]["count"],
            "item_percent": (summary["no_moving"]["count"] / total_items) * 100 if total_items else 0,
            "total_value": summary["no_moving"]["value"],
            "value_percent": (summary["no_moving"]["value"] / total_value) * 100 if total_value else 0
        },
        {
            "movement_type": "Stock Balance",
            "num_items": stock_balance_count,  # Sum of Fast and Slow Moving
            "total_value": stock_balance_value,  # Sum of Fast and Slow Moving
        },
        {
            "movement_type": "Total",
            "num_items": total_items,
            "item_percent": total_percent_items,
            "total_value": total_value,
            "value_percent": total_percent_value
        }
    ]

    return columns, data

# Report 3: Warehouse and Balance Value
def get_non_moving_branch_data():
    columns = [
        {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Data"},
        {"fieldname": "balance_value", "label": "Value (Nu.)", "fieldtype": "Float"}
    ]

    warehouse_balances = frappe.db.sql("""
        SELECT
            sle.warehouse,
            SUM(sle.actual_qty * sle.valuation_rate) AS balance_value
        FROM `tabStock Ledger Entry` sle
        WHERE sle.posting_date <= CURDATE()
        GROUP BY sle.warehouse
    """, as_dict=True)

    data = []
    total_balance_value = 0

    for warehouse_entry in warehouse_balances:
        data.append({
            "warehouse": warehouse_entry.warehouse,
            "balance_value": warehouse_entry.balance_value
        })
        total_balance_value += warehouse_entry.balance_value

     # Add a row for the overall total
    data.append({
        "warehouse": "Overall Total",
        "balance_value": total_balance_value
    })    

    return columns, data


# Report 4 Data
def get_report_4_data():
    report_1_columns, report_1_data = get_inventory_report_data()

    summary = {
        "inventory1": {"count": 0, "value": 0},
        "inventory2": {"count": 0, "value": 0},
        "inventory3": {"count": 0, "value": 0},
    }

    total_items = 0
    total_value = 0

    for entry in report_1_data:
        total_items += 1
        total_value += entry["issue_value"]

        if entry["movement"] == "Fast Moving":
            summary["inventory1"]["count"] += 1
            summary["inventory1"]["value"] += entry["issue_value"]
        elif entry["movement"] == "Slow Moving":
            summary["inventory2"]["count"] += 1
            summary["inventory2"]["value"] += entry["issue_value"]
        else:
            summary["inventory3"]["count"] += 1
            summary["inventory3"]["value"] += entry["issue_value"]

    total_percent_items = 100
    total_percent_value = 100

    columns = [
        {"fieldname": "consumption_type", "label": "Consumption Type", "fieldtype": "Data"},
        {"fieldname": "num_items", "label": "Number of Items", "fieldtype": "Int"},
        {"fieldname": "item_percent", "label": "Item Percent", "fieldtype": "Percent"},
        {"fieldname": "total_value", "label": "Total Value", "fieldtype": "Float"},
        {"fieldname": "value_percent", "label": "Value Percent", "fieldtype": "Percent"}
    ]

    data = [
        {
            "consumption_type": "Items with opening balance & closing balance but no Receipt & Consumption",
            "num_items": summary["inventory1"]["count"],
            "item_percent": (summary["inventory1"]["count"] / total_items) * 100 if total_items else 0,
            "total_value": summary["inventory1"]["value"],
            "value_percent": (summary["inventory1"]["value"] / total_value) * 100 if total_value else 0
        },
        {
            "consumption_type": "Items with Opening balance, Receipt value & no consumption",
            "num_items": summary["inventory2"]["count"],
            "item_percent": (summary["inventory2"]["count"] / total_items) * 100 if total_items else 0,
            "total_value": summary["inventory2"]["value"],
            "value_percent": (summary["inventory2"]["value"] / total_value) * 100 if total_value else 0
        },
        {
            "consumption_type": "Purchased during the year with no consumption",
            "num_items": summary["inventory3"]["count"],
            "item_percent": (summary["inventory3"]["count"] / total_items) * 100 if total_items else 0,
            "total_value": summary["inventory3"]["value"],
            "value_percent": (summary["inventory3"]["value"] / total_value) * 100 if total_value else 0
        },
        {
            "consumption_type": "Total",
            "num_items": total_items,
            "item_percent": total_percent_items,
            "total_value": total_value,
            "value_percent": total_percent_value
        }
    ]

    return columns, data