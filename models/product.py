from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hourly_rate = fields.Float(
        string="Tarif horaire"
    )
