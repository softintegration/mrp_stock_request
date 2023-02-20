# -*- coding: utf-8 -*- 

import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    stock_request_count = fields.Integer(compute='_compute_stock_request_count')

    def _compute_stock_request_count(self):
        for each in self:
            each.stock_request_count = self._get_stock_requests(count=True)

    def action_view_stock_requests(self):
        self.ensure_one()
        stock_request_ids = self._get_stock_requests().ids
        action = self.env.ref('stock_request.action_stock_request')
        return_action = {
            'name': action.name,
            'res_model': action.res_model,
            'type': action.type,
            'target': 'current',
        }
        if len(stock_request_ids) == 1:
            return_action['res_id'] = stock_request_ids[0]
            return_action['view_mode'] = 'form'
            return_action['view_id'] = self.env.ref('stock_request.stock_request_form_view').id
        else:
            return_action['view_mode'] = 'tree,form'
            return_action['domain'] = [('id', 'in', stock_request_ids)]
            return_action['views'] = action.views
        return return_action

    def _get_stock_requests(self, count=False):
        self.ensure_one()
        domain = [('mrp_production_ids', 'in', self.id)]
        if count:
            return self.env['stock.request'].search_count(domain)
        return self.env['stock.request'].search(domain)

    def action_make_stock_request(self):
        location_src_ids = self.mapped("location_src_id")
        if len(location_src_ids) > 1:
            raise ValidationError(_("All the selected Production Orders must have the same Components Location!"))
        for each in self:
            if each.state not in ("confirmed", "progress"):
                raise ValidationError(_("Only Confirmed/In progress Production orders can request the stock!"))
        product_product_uom_id = {}
        for move in self.mapped("move_raw_ids"):
            move_key = '%s_%s' % (move.product_id.id, move.product_uom.id)
            if move_key in product_product_uom_id.keys():
                product_product_uom_id[move_key].update(
                    {'quantity': product_product_uom_id[move_key]['quantity'] + move.product_uom_qty,
                     'quantity_to_request': product_product_uom_id[move_key][
                                                'quantity_to_request'] + move.product_uom_qty,
                     })
                product_product_uom_id[move_key]['move_raw_ids'][0][2].append(move.id)
            else:
                product_product_uom_id[move_key] = {'product_id': move.product_id.id,
                                                    'product_uom_id': move.product_uom.id,
                                                    'quantity': move.product_uom_qty,
                                                    'quantity_to_request': move.product_uom_qty,
                                                    'move_raw_ids': [(6, 0, move.ids)]}
        new_wizard = self.env['stock.request.create'].create({
            'mrp_production_ids': [(6, 0, self.ids)],
            'company_id': self.mapped("company_id").ids[0],
            'item_ids': [(0, 0, item) for __, item in product_product_uom_id.items()]
        })
        view_id = self.env.ref('mrp_stock_request.view_stock_request_create').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create stock request'),
            'view_mode': 'form',
            'res_model': 'stock.request.create',
            'target': 'new',
            'res_id': new_wizard.id,
            'views': [[view_id, 'form']],
            'context': self.env.context
        }

    def _action_make_stock_request(self, location_id, items, date=False, scheduled_date=False, picking_type_id=False):
        if not location_id:
            raise ValidationError(_('Source Location must be specified!'))
        if not items:
            raise ValidationError(_("At least one product must be specified to create stock request"))
        for item in items:
            if float_compare(item.quantity_to_request, 0.0, precision_rounding=item.product_uom_id.rounding) <= 0:
                raise ValidationError(_('All the lines must have positive Quantity to request!'))
        stock_request_dict = self._prepare_stock_request(location_id, items,date=date,scheduled_date=scheduled_date,
                                                         picking_type_id=picking_type_id)
        stock_request = self.env['stock.request'].create(stock_request_dict)
        return stock_request

    def _prepare_stock_request(self, location_id, items,date=False, scheduled_date=False, picking_type_id=False):
        stock_request_dict = {
            'mrp_production_ids': [(6, 0, self.ids)],
            'location_id': location_id.id,
            'location_dest_id': self.mapped("location_src_id").ids[0],
            'company_id': self.mapped("company_id").ids[0],
            'move_line_ids': [(0, 0, {
                'product_id': item.product_id.id,
                'product_uom_id': item.product_uom_id.id,
                'product_uom_qty': item.quantity_to_request,
                'location_id': location_id.id,
                'location_dest_id': self.mapped("location_src_id").ids[0],
                'move_raw_ids': [(6, 0, item.move_raw_ids.ids)],
                'company_id': self.mapped("company_id").ids[0],
            }) for item in items]
        }
        if date:
            stock_request_dict.update({'date':date})
        if scheduled_date:
            stock_request_dict.update({'scheduled_date':scheduled_date})
        if picking_type_id:
            stock_request_dict.update({'picking_type_id':picking_type_id and picking_type_id.id})
        return stock_request_dict
