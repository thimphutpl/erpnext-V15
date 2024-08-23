# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class JournalEntrySeries(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.Data | None
		enabled: DF.Check
		entry_type: DF.Literal["Journal Entry", "Inter Company Journal Entry", "Bank Entry", "Cash Entry", "Credit Card Entry", "Debit Note", "Credit Note", "Contra Entry", "Excise Entry", "Write Off Entry", "Opening Entry", "Depreciation Entry", "Exchange Rate Revaluation", "Exchange Gain Or Loss", "Deferred Revenue", "Deferred Expense"]
		journal_entry_series: DF.Data
		prefix: DF.Data
	# end: auto-generated types
	pass
