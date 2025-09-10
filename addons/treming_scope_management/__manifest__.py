# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Scopes',
    'version': '1.0',
    'category': 'Productivity/Scopes',
    'summary': 'Organize your quotations with scopes',
    'description': "This module allows you to organize quotations with scopes, integrating with sales, CRM, and stock management.",
    'depends': ['base', 'sale', 'stock', 'crm', 'product', 'web', 'mail', 'sale_management',
                'sale_quotation_builder', ],
    'auto_install': False,
    'data': [
        'security/ir.model.access.csv',
        'report/report_layout.xml',
        'views/trscma_scope_management_tr.xml',
        'views/trscma_scope_management_menu_tr.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'treming_scope_management/static/src/css/report_layout_treming.css',  # Use compiled CSS
        ],
        'web.report_assets_common': [
            'treming_scope_management/static/src/css/report_layout_treming.css',  # For report-specific styles
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
