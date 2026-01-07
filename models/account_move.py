from odoo import models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    billing_start_date = fields.Date(
        string="Date de début de facturation"
    )

    billing_end_date = fields.Date(
        string="Date de fin de facturation"
    )
