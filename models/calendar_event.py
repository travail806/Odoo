from odoo import models, fields

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    recurring_product_id = fields.Many2one(
        'product.product',
        string="Produit récurrent",
        domain="[('type','=','service'),('is_product_recurrent','=',True)]"
    )

    x_event_color_index = fields.Integer(
        related='recurring_product_id.x_color_index',
        store=True,
        string="Couleur (produit)"
    )
    
   