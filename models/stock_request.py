# -*- coding: utf-8 -*- 

import datetime

from odoo import models, fields, api, _


class StockRequest(models.Model):
    _inherit = 'stock.request'

    mrp_production_ids = fields.Many2many('mrp.production', 'stock_request_mrp_production'
                                                            'stock_request_id', 'production_id',
                                          string="Origin manufacturing orders")
    mrp_production_ids_count = fields.Integer(compute='_compute_mrp_production_ids_count')
    move_raw_ids_count = fields.Integer(compute='_compute_move_raw_ids_count')

    @api.depends('mrp_production_ids')
    def _compute_mrp_production_ids_count(self):
        for each in self:
            each.mrp_production_ids_count = len(each.mrp_production_ids)

    @api.depends('move_line_ids.move_raw_ids')
    def _compute_move_raw_ids_count(self):
        for each in self:
            each.move_raw_ids_count = len(each.move_line_ids.mapped("move_raw_ids"))

    def action_view_move_raw_ids(self):
        self.ensure_one()
        move_raw_ids = self.move_line_ids.mapped("move_raw_ids").ids
        # TODO:here we have to create specific tree view
        action = self.env.ref('mrp_stock_request.action_mrp_production_move_raw')
        return {
            'name': action.name,
            'res_model': action.res_model,
            'type': action.type,
            'target': 'current',
            'view_mode':'tree',
            'domain':[('id', 'in', move_raw_ids)],
            'view_id':action.view_id.id,
            'search_view_id':[action.search_view_id.id, 'search'],
            'context':action.context
        }


class StockRequestLine(models.Model):
    _inherit = "stock.request.line"

    move_raw_ids = fields.Many2many('stock.move', 'srock_request_line_stock_move', 'request_line_id', 'move_id',
                                    string="Source Manufacturing order Components")
