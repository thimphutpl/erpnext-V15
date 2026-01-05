from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
        'fieldname': 'emi_sales',
		'non_standard_fieldnames': {
			'Payment Entry': 'reference_name',
			'Daily Collection': 'reference',
			'Journal Entry': 'reference_name',
			'Asset': 'emi_sales_id',
		},
		'transactions': [
			{
				'label': _('Related'),
				'items': ['Payment Entry', 'Journal Entry', 'Asset', 'Asset Issue Details']
			},
		]
	}
