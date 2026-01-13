from odoo import models, fields

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    recurring_product_id = fields.Many2one(
        'product.product',
        string="Produit récurrent",
        domain="[('type','=','service')]"
    )
