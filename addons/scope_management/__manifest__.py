# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Scopes',
    'version': '1.0',
    'category': 'Productivity/Scopes',
    'summary': 'Organize your quotazion with scopes',
    'depends': ['base', 'sale', 'stock', 'crm', 'product', 'web', 'mail', 'sale_management','sale_quotation_builder',],
    'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'views/scope_management_views.xml',
        'views/scope_management_menus.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'scope_management/static/src/scss/layout_*.scss',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
