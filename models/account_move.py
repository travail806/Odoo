from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    billing_start_date = fields.Date(string="Date de début de facturation")
    billing_end_date = fields.Date(string="Date de fin de facturation")

    @api.constrains('billing_start_date', 'billing_end_date')
    def _check_billing_dates(self):
        for move in self:
            if move.billing_start_date and move.billing_end_date:
                if move.billing_end_date < move.billing_start_date:
                    raise ValidationError(
                        "La date de fin de facturation doit être postérieure à la date de début."
                    )
