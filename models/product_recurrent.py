from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_recurrent_visible = fields.Boolean(
        compute='_compute_is_recurrent_visible',
        store=False
    )

    is_product_recurrent = fields.Boolean(
        string="Est recurrent ?",
        help="Indique si ce produit correspond a une prestation recurrente",
        store=True  # important pour que les onchanges voient la valeur du champ
    )

    x_color_index = fields.Integer(
        string="Couleur calendrier",
        default=0,
        help="Index de couleur (0 à 11) utilisé pour colorer les événements liés à ce produit sur le calendrier."
    )


    @api.depends('type')
    def _compute_is_recurrent_visible(self):
        for product in self:
            product.is_recurrent_visible = (product.type == 'service')

    @api.constrains('is_product_recurrent', 'type')
    def _check_is_recurrent_type(self):
        for product in self:
            if product.is_product_recurrent and product.type != 'service':
                raise UserError("Seuls les produits de type 'Service' peuvent etre recurrents.")

    @api.onchange('type')
    def _onchange_type_recurrent(self):
        for product in self:
            if product.type != 'service':
                product.is_product_recurrent = False

