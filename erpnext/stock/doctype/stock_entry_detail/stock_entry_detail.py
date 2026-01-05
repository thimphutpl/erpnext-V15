# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from frappe.model.document import Document


class StockEntryDetail(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_qty: DF.Float
		additional_cost: DF.Currency
		against_stock_entry: DF.Link | None
		allow_alternative_item: DF.Check
		allow_zero_valuation_rate: DF.Check
		amount: DF.Currency
		barcode: DF.Data | None
		basic_amount: DF.Currency
		basic_rate: DF.Currency
		batch_no: DF.Link | None
		bom_no: DF.Link | None
		conversion_factor: DF.Float
		cost_center: DF.Link
		description: DF.TextEditor | None
		difference_amount: DF.Currency
		difference_qty: DF.Float
		engine_no: DF.Data | None
		equipment: DF.Link | None
		equipment_category: DF.Link | None
		equipment_model: DF.Link | None
		equipment_type: DF.Link | None
		expense_account: DF.Link | None
		gross_vehicle_weight: DF.Float
		hired_equipmentvehicle: DF.Check
		image: DF.Attach | None
		is_finished_item: DF.Check
		is_process_loss: DF.Check
		is_scrap_item: DF.Check
		issue_to: DF.DynamicLink | None
		issue_to_employee: DF.Link | None
		issue_to_equipment: DF.Link | None
		issue_type: DF.Literal["", "Employee", "Equipment"]
		issued_employee_name: DF.Data | None
		issued_equipment_name: DF.Data | None
		item_code: DF.Link
		item_group: DF.Data | None
		item_name: DF.Data | None
		job_card_item: DF.Data | None
		material_request: DF.Link | None
		material_request_item: DF.Link | None
		original_item: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		po_detail: DF.Data | None
		pol_slip_no: DF.Data | None
		project: DF.Link | None
		putaway_rule: DF.Link | None
		qty: DF.Float
		quality_inspection: DF.Link | None
		received_qty: DF.Float
		reference_purchase_receipt: DF.Link | None
		remarks: DF.SmallText | None
		retain_sample: DF.Check
		s_warehouse: DF.Link | None
		sample_quantity: DF.Int
		sco_rm_detail: DF.Data | None
		serial_no: DF.SmallText | None
		set_basic_rate_manually: DF.Check
		ste_detail: DF.Data | None
		stock_uom: DF.Link
		subcontracted_item: DF.Link | None
		t_warehouse: DF.Link | None
		tare_weight: DF.Float
		transfer_qty: DF.Float
		transferred_qty: DF.Float
		transporter: DF.Link | None
		tvo_no: DF.Data | None
		unloading_by: DF.Literal["", "Company", "Transporter"]
		uom: DF.Link
		valuation_rate: DF.Currency
		weight_slip_no: DF.Data | None
	# end: auto-generated types

	pass
