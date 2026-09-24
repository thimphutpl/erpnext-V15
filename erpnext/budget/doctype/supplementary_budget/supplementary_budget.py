# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint, scrub
from frappe.model.document import Document
from frappe.utils import flt, nowdate

class SupplementaryBudget(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.budget.doctype.supplementary_budget_item.supplementary_budget_item import SupplementaryBudgetItem
        from frappe.types import DF

        amended_from: DF.Link | None
        approver: DF.Link | None
        approver_designation: DF.Data | None
        approver_name: DF.Data | None
        attachment: DF.Attach | None
        branch: DF.Link
        budget_against: DF.Literal["", "Cost Center", "Project"]
        company: DF.Link
        cost_center: DF.Link
        fiscal_year: DF.Link
        items: DF.Table[SupplementaryBudgetItem]
        posting_date: DF.Date
        project: DF.Link | None
        remarks: DF.SmallText | None
        supplementary_type: DF.Literal["", "New Supplementary Budget", "Additional Supplementary Budget"]
    # end: auto-generated types

    def validate(self):
        self.validate_budget()

    def on_submit(self):
        if self.supplementary_type == "Additional Supplementary Budget":
            self.supplement_budget(cancel=False)
        elif self.supplementary_type == "New Supplementary Budget":
            self.new_supplement_budget(cancel=False)
            self.create_budget_doc()

    def on_cancel(self):
        if self.supplementary_type == "Additional Supplementary Budget":
            self.supplement_budget(cancel=True)
        elif self.supplementary_type == "New Supplementary Budget":
            self.new_supplement_budget(cancel=True)
            self.cancel_budget()

    def set_broad_head_from_account(self):
        """Auto-set broad_head as parent_account of selected account"""
        for row in self.get("items"):  # Replace with your child table fieldname
            if row.account and not row.broad_head:
                parent_account = frappe.db.get_value("Account", row.account, "parent_account")
                if parent_account:
                    row.broad_head = parent_account
                else:
                    frappe.throw(f"Account {row.account} does not have a parent account")
            elif row.account and row.broad_head:
                # Optional: Validate that broad_head matches parent_account
                parent_account = frappe.db.get_value("Account", row.account, "parent_account")
                if parent_account and row.broad_head != parent_account:
                    frappe.throw(f"Broad Head {row.broad_head} does not match parent account {parent_account} of {row.account}")            

    def validate_budget(self):
        if self.supplementary_type == "New Supplementary Budget":
            return

        budget_against_field = frappe.scrub(self.budget_against)
        budget_against = self.get(budget_against_field)

        if not self.items:
            frappe.throw(_("Please provide Budget Head or Account to supplement budget"))

        for d in self.items:
            query = f"""
                SELECT b.name, ba.account, ba.budget_amount
                FROM `tabBudget` b, `tabBudget Account` ba
                WHERE ba.parent = b.name
                  AND b.docstatus = 1
                  AND b.company = %s
                  AND b.{budget_against_field} = %s
                  AND b.fiscal_year = %s
                  AND ba.account = %s
            """
            params = [self.company, budget_against, self.fiscal_year, d.account]

            if d.get('budget_activity'):
                query += " AND ba.budget_activity = %s"
                params.append(d.budget_activity)
            if d.get('budget_sub_activity'):
                query += " AND ba.budget_sub_activity = %s"
                params.append(d.budget_sub_activity)

            budget_exist = frappe.db.sql(query, params, as_dict=1)

            if not budget_exist:
                error_message = _(
                    "Budget record does not exist against {0} '{1}' and account '{2}' for fiscal year {3}"
                ).format(self.budget_against, budget_against, d.account, self.fiscal_year)

                if d.get('budget_activity'):
                    error_message += _(" with budget activity '{0}'").format(d.budget_activity)
                if d.get('budget_sub_activity'):
                    error_message += _(" and budget sub-activity '{0}'").format(d.budget_sub_activity)
                
                frappe.throw(error_message)

            d.approved_budget = flt(
            budget_exist[0].budget_amount,
            2
        )

    def supplement_budget(self, cancel=False):
        if frappe.db.get_value("Fiscal Year", self.fiscal_year, "closed"):
            frappe.throw(_("Fiscal Year {0} has already been closed").format(self.fiscal_year))

        budget_against_field = frappe.scrub(self.budget_against)
        budget_against = self.get(budget_against_field)

        for d in self.items:
            month = d.month
            if d.amount <= 0:
                frappe.throw(_("Budget Supplementary Amount should be greater than 0 for record {0}").format(d.idx))

            query = f"""
                SELECT ba.name, ba.account, b.name as budget_name
                FROM `tabBudget` b, `tabBudget Account` ba
                WHERE ba.parent = b.name
                AND b.docstatus < 2
                AND b.company = %s
                AND b.{budget_against_field} = %s
                AND b.fiscal_year = %s
                AND ba.account = %s
            """
            params = [self.company, budget_against, self.fiscal_year, d.account]

            if d.get('budget_activity'):
                query += " AND ba.budget_activity = %s"
                params.append(d.budget_activity)
            if d.get('budget_sub_activity'):
                query += " AND ba.budget_sub_activity = %s"
                params.append(d.budget_sub_activity)
            if d.get('budget_sub_activity'):
                query += " AND ba.source_of_fund = %s"
                params.append(d.source_of_fund)    

            result = frappe.db.sql(query, params, as_dict=1)

            if not result:
                frappe.throw(_("Budget not set for account {0} under {1} {2}. Please check initial budget allocations").format(
                    d.account, self.budget_against, budget_against
                ))

            # Get the Budget Account document
            budget_account_name = result[0].name
            budget_account_doc = frappe.get_doc("Budget Account", budget_account_name)
            
            # Get the Budget document
            budget_doc = frappe.get_doc("Budget", result[0].budget_name)

            if cancel:
                sup_budget = flt(budget_account_doc.supplementary_budget) - flt(d.amount)
                total = flt(budget_account_doc.budget_amount) - flt(d.amount)
                frappe.db.sql("DELETE FROM `tabSupplementary Details` WHERE reference = %s", self.name)
            else:
                sup_budget = flt(budget_account_doc.supplementary_budget) + flt(d.amount)
                total = flt(budget_account_doc.budget_amount) + flt(d.amount)
                supp_details = frappe.new_doc("Supplementary Details")
                supp_details.budget_against = self.budget_against
                supp_details.cost_center = self.cost_center if self.budget_against == "Cost Center" else ""
                supp_details.project = self.project if self.budget_against == "Project" else ""
                supp_details.account = d.account
                supp_details.budget_activity = d.get('budget_activity', '')
                supp_details.budget_sub_activity = d.get('budget_sub_activity', '')
                supp_details.amount = flt(d.amount)
                supp_details.company = self.company
                supp_details.month = month
                supp_details.reference = self.name
                supp_details.posting_date = nowdate()
                supp_details.fiscal_year = self.fiscal_year
                supp_details.insert(ignore_permissions=True)

            monthly_budget = frappe.db.get_single_value("Budget Settings", "monthly_budget_check")
            
            # Update the Budget Account document
            budget_account_doc.db_set("supplementary_budget", flt(sup_budget, 2))
            budget_account_doc.db_set("budget_amount", flt(total))

            self.update_budget_release(d, budget_against_field, budget_against, cancel)

            if monthly_budget:
                if month:
                    month_field_map = {
                        "January": "sb_january",
                        "February": "sb_february",
                        "March": "sb_march",
                        "April": "sb_april",
                        "May": "sb_may",
                        "June": "sb_june",
                        "July": "sb_july",
                        "August": "sb_august",
                        "September": "sb_september",
                        "October": "sb_october",
                        "November": "sb_november",
                        "December": "sb_december"
                    }
                    if month in month_field_map:
                        month_field = month_field_map[month]
                        current_value = flt(getattr(budget_account_doc, month_field, 0))
                        new_value = current_value - flt(d.amount) if cancel else current_value + flt(d.amount)
                        budget_account_doc.db_set(month_field, flt(new_value))
                    else:
                        frappe.throw(_("Invalid month specified: {0}").format(month))
                else:
                    frappe.throw(_("Please Enter Month"))

    def update_budget_release(self, d, budget_against_field, budget_against, cancel=False):

        release = frappe.db.sql(f"""
            SELECT bra.name, br.name as parent
            FROM `tabBudget Release` br
            INNER JOIN `tabBudget Release Account` bra
                ON bra.parent = br.name
            WHERE br.docstatus < 2
            AND br.company = %s
            AND br.{budget_against_field} = %s
            AND br.fiscal_year = %s
            AND bra.account = %s
        """, (self.company, budget_against, self.fiscal_year, d.account), as_dict=1)

        if not release:
            return

        bra_doc = frappe.get_doc("Budget Release Account", release[0].name)

        # # ---- Update Approved Budget ----
        # if cancel:
        #     approved = flt(bra_doc.approved_budget) - flt(d.amount)
        # else:
        #     approved = flt(bra_doc.approved_budget) + flt(d.amount)

        # bra_doc.db_set("approved_budget", approved)

        # SUPPLEMENTARY BUDGET (NEW)
        if hasattr(bra_doc, "supplementary_budget"):
            if cancel:
                sup = flt(bra_doc.supplementary_budget) - flt(d.amount)
            else:
                sup = flt(bra_doc.supplementary_budget) + flt(d.amount)

            bra_doc.db_set("supplementary_budget", flt(sup, 2))

        # # ---- Update Released Budget (Optional) ----
        # if hasattr(bra_doc, "released_budget"):
        #     if cancel:
        #         released = flt(bra_doc.released_budget) - flt(d.amount)
        #     else:
        #         released = flt(bra_doc.released_budget) + flt(d.amount)

        #     bra_doc.db_set("released_budget", released)

        # # -------------------------------
        # # UPDATE PARENT (Budget Release)
        # # -------------------------------
        # parent_doc = frappe.get_doc("Budget Release", release[0].parent)

        # if cancel:
        #     balance = flt(parent_doc.budget_balance) - flt(d.amount)
        # else:
        #     balance = flt(parent_doc.budget_balance) + flt(d.amount)

        # parent_doc.db_set("budget_balance", balance)
                

    def new_supplement_budget(self, cancel=False):
        if frappe.db.get_value("Fiscal Year", self.fiscal_year, "closed"):
            frappe.throw(_("Fiscal Year {0} has already been closed").format(self.fiscal_year))

        budget_against_field = frappe.scrub(self.budget_against)
        budget_against = self.get(budget_against_field)
        for d in self.items:
            month = d.month
            if d.amount <= 0:
                frappe.throw(_("Supplementary Amount should be greater than 0 for record {0}").format(d.idx))

            if cancel:
                frappe.db.sql(
                    "DELETE FROM `tabSupplementary Details` WHERE reference = %s AND account = %s",
                    (self.name, d.account)
                )
            else:
                supp_details = frappe.new_doc("Supplementary Details")
                supp_details.budget_against = self.budget_against
                supp_details.cost_center = self.cost_center if self.budget_against == "Cost Center" else ""
                supp_details.project = self.project if self.budget_against == "Project" else ""
                supp_details.account = d.account
                supp_details.budget_activity = d.get('budget_activity', '')
                supp_details.budget_sub_activity = d.get('budget_sub_activity', '')
                supp_details.amount = flt(d.amount)
                supp_details.company = self.company
                supp_details.month = month
                supp_details.reference = self.name
                supp_details.posting_date = nowdate()
                supp_details.fiscal_year = self.fiscal_year
                supp_details.insert(ignore_permissions=True)

    def create_budget_doc(self):
        """Create a new Budget document from Supplementary Budget"""
        budget = frappe.new_doc("Budget")
        self.map_proposal_to_budget(budget)
        budget.new_supplement_budget = self.name  # Link back to proposal
        budget.submit()
        return budget

    def update_budget_doc(self, budget):
        """Update existing Budget document from Supplementary Budget"""
        self.map_proposal_to_budget(budget)
        budget.new_supplement_budget = self.name

    def map_proposal_to_budget(self, budget):
        """Map fields from Supplementary Budget to Budget"""
        # Map basic fields
        budget.company = self.company
        budget.fiscal_year = self.fiscal_year
        budget.budget_against = self.budget_against
        budget.cost_center = self.cost_center
        budget.branch = self.branch
        
        # Clear existing accounts in budget
        budget.set('accounts', [])
        
        # Map items from supplementary to budget
        for supp_account in self.items:
            budget_account = budget.append('accounts', {})
            budget_account.account = supp_account.account
            budget_account.cost_center = self.cost_center
            budget_account.broad_head = supp_account.broad_head
            budget_account.budget_activity = supp_account.budget_activity
            budget_account.budget_sub_activity = supp_account.budget_sub_activity
            budget_account.source_of_fund = supp_account.source_of_fund
            # budget_account.approved_budget = supp_account.approved_budget
            budget_account.supplementary_budget = supp_account.amount
            budget_account.budget_amount = supp_account.amount
            budget.new_supplementary_budget_check = 1

    def cancel_budget(self):
        """Cancel the associated Budget document"""
        existing_budget = frappe.db.exists("Budget", {
            "new_supplement_budget": self.name,
            "docstatus": 1  # Submitted
        })
        
        if existing_budget:
            budget_doc = frappe.get_doc("Budget", existing_budget)
            budget_doc.cancel()
            frappe.msgprint(_("Budget {0} has been cancelled").format(budget_doc.name))	            

def get_permission_query_conditions(user=None):
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    if "System Manager" in roles:
        return ""

    if "Budget User" in roles:
        return f"""
            `tabSupplementary Budget`.owner = {frappe.db.escape(user)}
            AND `tabBudget Proposal`.workflow_state  IN('Draft','Waiting for Approval','Approved','Rejected')
        """

    if "Budget Approver" in roles:
        return """
            `tabSupplementary Budget`.workflow_state IN('Waiting for Approval','Approved','Rejected')
        """

    return "1=0"