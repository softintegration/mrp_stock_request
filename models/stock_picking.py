# -*- coding: utf-8 -*- 

import datetime

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    mrp_production_ids = fields.Many2many('mrp.production', 'stock_picking_mrp_production'
                                                            'picking_id', 'production_id',
                                          string="Origin manufacturing orders")
    mrp_production_ids_count = fields.Integer(compute='_compute_mrp_production_ids_count')

    @api.depends('mrp_production_ids')
    def _compute_mrp_production_ids_count(self):
        for each in self:
            each.mrp_production_ids_count = len(each.mrp_production_ids)


