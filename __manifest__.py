# -*- coding: utf-8 -*- 


{
 'name': 'Manufacturing stock request',
 'author': 'Soft-integration',
 'application': False,
 'installable': True,
 'auto_install': False,
 'qweb': [],
 'description': False,
 'images': [],
 'version': '1.0.1',
 'category': 'Manufacturing/Stock',
 'demo': [],
 'depends': ['mrp','stock_request'],
 'data': [
     'security/mrp_stock_request_security.xml',
     'security/ir.model.access.csv',
     'views/mrp_production_views.xml',
     'wizard/stock_request_create_views.xml'
    ],
 'license': 'LGPL-3',
 }