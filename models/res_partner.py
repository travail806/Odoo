from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_num_service= fields.Char(
        string="Numéro de service",
        help="Numéro de service(code établissement interne, etc.)"
    )