# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LandRecord(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		areain_acre: DF.Data | None
		areain_sqft: DF.Data | None
		attach_file: DF.Attach | None
		dzongkhag: DF.Data | None
		finding: DF.SmallText | None
		gewog: DF.Data | None
		land_sub_type: DF.Literal["", "Crown Property", "Individual", "Lhakhang"]
		land_type: DF.Literal["", "Crown Property", "OGZ"]
		location: DF.Data | None
		origin_of_thram: DF.Data | None
		ownership_type: DF.Literal["", "Individual Person", "Crown Property"]
		photograph: DF.Attach | None
		plot_category: DF.Data | None
		plot_id: DF.Data | None
		plot_status: DF.SmallText | None
		precinctland_type: DF.Literal["", "Kamzhing", "Royal Uses", "Urban", "Neighbourg", "Heritage"]
		reference: DF.Attach | None
		remarks: DF.Data | None
		ruralurban: DF.Literal["", "Rural", "Urban"]
		thram_holder: DF.Literal["", "HM"]
		thram_no: DF.Data | None
		thromde: DF.Data | None
		village: DF.Data | None
		way_forward: DF.SmallText | None
	# end: auto-generated types
	pass
