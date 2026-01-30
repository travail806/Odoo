from odoo import models, fields

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    recurring_product_id = fields.Many2one(
        'product.product',
        string="Produit récurrent",
<<<<<<< HEAD
        domain="[('is_product_recurrent','=',True), ('type','=','service')]"
=======
        domain="[('type','=','service'),('is_product_recurrent','=',True)]"
>>>>>>> 2fd2036bc81872e200f81e0d0d3162fb85e4aff2
    )
