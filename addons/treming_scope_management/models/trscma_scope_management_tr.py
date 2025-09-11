from odoo import api, models, fields
from odoo.tools import html2plaintext

class ScopeManagement(models.Model):
    #Model name & description. Inherits from models.Model (Odoo base class)
    _name = 'scope.management'
    _description = 'Scopes Management'

    name = fields.Char(string='Service', required=True)
    description = fields.Html(string='Description')
    sales_team = fields.Many2one('crm.team', string='Sales Team')
    active = fields.Boolean(default=True)

    # Relación con el producto (cada scope tiene UN producto)
    product_id = fields.Many2one('product.product', string='Product')

    # Relación con la orden (cada scope pertenece a UNA orden)
    sale_order_id = fields.Many2one("sale.order", string="Sale Order")

    # Restricción SQL para enforzar unicidad: solo UN scope por producto
    _sql_constraints = [
        ('unique_product_id', 'unique(product_id)', '¡Ya existe una definición de alcances para este producto! No se permiten duplicados.')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('description') and not vals.get('name'):
                text = html2plaintext(vals['description'])
                name = text.strip().replace('*', '').partition("\n")[0]
                vals['name'] = (name[:97] + '...') if len(name) > 100 else name
        records = super().create(vals_list)
        for record in records:
            if record.product_id:
                record.product_id.write({'scope_id': record.id})
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'product_id' in vals:
            for record in self:
                if record.product_id:
                    # Sincronizar automáticamente: actualizar el scope en el producto
                    record.product_id.write({'scope_id': record.id})
                # Si se quita el producto, limpiar el scope_id en el producto anterior (opcional, para limpieza)
                if vals.get('product_id') is False and record.product_id:
                    record.product_id.write({'scope_id': False})
        return res