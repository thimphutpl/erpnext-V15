from frappe import _


def get_data():
    return {
        "fieldname": "name",

        "non_standard_fieldnames": {
            "Journal Entry": "reference_link",
        },

        "transactions": [
            {
                "label": _("Payment"),
                "items": ["Journal Entry"],
            }
        ],
    }