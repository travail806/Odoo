from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_compute_hours(self):
        for line in self:
            move = line.move_id
            product = line.product_id

            if not product or not move:
                return

            template = product.product_tmpl_id

            if (
                move.billing_start_date
                and move.billing_end_date
                and template.hours_per_day
            ):
                days = (move.billing_end_date - move.billing_start_date).days + 1
                line.quantity = days * template.hours_per_day
