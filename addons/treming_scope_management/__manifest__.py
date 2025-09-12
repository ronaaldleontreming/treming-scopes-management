# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# noinspection PyStatementEffect
{
    'name': 'Scopes',
    'version': '1.0',
    'category': 'Productivity/Scopes',
    'summary': 'Organize your quotations with scopes',
    'description': "This module allows you to organize quotations with scopes, integrating with sales, CRM, and stock management.",
    'depends': ['base', 'sale', 'stock', 'crm', 'product', 'web', 'mail', 'sale_management', 'sale_quotation_builder', 'documents', 'account'],
    'auto_install': False,
    'data': [
        'security/ir.model.access.csv',
        'views/crm_team.xml',
        'views/sale_order.xml',
        'views/trscma_scope_management_tr.xml',
        'views/product_views.xml',
        'report/report_scope_proposal.xml',
        'views/trscma_scope_management_menu_tr.xml',
        'report/report_layout.xml',
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
