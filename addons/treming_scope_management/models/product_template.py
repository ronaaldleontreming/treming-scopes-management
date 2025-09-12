from odoo import models, api, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    attachment_count = fields.Integer(compute='_compute_attachment_count')

    def _compute_attachment_count(self):
        for product in self:
            product.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'product.template'),
                ('res_id', '=', product.id),
                ('mimetype', 'ilike', 'pdf')
            ])

    def action_digital_files(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Digital Files',
            'res_model': 'ir.attachment',
            'domain': [('res_model', '=', 'product.template'), ('res_id', '=', self.id), ('mimetype', 'ilike', 'pdf')],
            'view_mode': 'tree,form',
            'target': 'current',
            'context': {
                'default_res_model': 'product.template',
                'default_res_id': self.id,
                'default_mimetype': 'application/pdf',
                'default_type': 'binary',
            },
        }

class ProductProduct(models.Model):
    _inherit = 'product.product'

    attachment_count = fields.Integer(compute='_compute_attachment_count')

    def _compute_attachment_count(self):
        for product in self:
            product.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'product.template'),
                ('res_id', '=', product.product_tmpl_id.id),
                ('mimetype', 'ilike', 'pdf')
            ])

    def action_digital_files(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Digital Files',
            'res_model': 'ir.attachment',
            'domain': [('res_model', '=', 'product.template'), ('res_id', '=', self.product_tmpl_id.id), ('mimetype', 'ilike', 'pdf')],
            'view_mode': 'tree,form',
            'target': 'current',
            'context': {
                'default_res_model': 'product.template',
                'default_res_id': self.product_tmpl_id.id,
                'default_mimetype': 'application/pdf',
                'default_type': 'binary',
            },
        }