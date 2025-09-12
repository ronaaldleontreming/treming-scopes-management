from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'
    scope_id = fields.Many2one(
        'scope.management',
        string="Scope",
        readonly=True,
    )
