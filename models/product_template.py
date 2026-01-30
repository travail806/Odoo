from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hours_per_day = fields.Float(
        string="Heures par jour",
        default=7.0,
        help="Nombre d'heures facturées par jour de formation"
    )
