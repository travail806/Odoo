from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hours_per_day = fields.Float(
        string="Heures par jour",
        default=0.0
    )
