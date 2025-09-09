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
        'report/report_layout.xml',
        'views/trscma_scope_management_tr.xml',
        'views/trscma_scope_management_menu_tr.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'treming_scope_management/static/src/scss/layout_treming.scss',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
