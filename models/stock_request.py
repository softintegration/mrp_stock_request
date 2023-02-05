# -*- coding: utf-8 -*- 

import datetime

from odoo import models, fields, api, _


class StockRequest(models.Model):
    _inherit = 'stock.request'


    mrp_production_ids = fields.Many2many('mrp.production','stock_request_mrp_production'
                                                  'stock_request_id','production_id')

