from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    billing_start_date = fields.Date(
        string="Début de période de facturation"
    )

    billing_end_date = fields.Date(
        string="Fin de période de facturation"
    )
