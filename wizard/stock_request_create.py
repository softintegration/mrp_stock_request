# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class StockRequestCreate(models.TransientModel):
    _name = 'stock.request.create'

    mrp_production_ids = fields.Many2many('mrp.production', 'stock_request_create_mrp_production', 'request_create_id',
                                          'production_order_id',
                                          required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,)
    location_id = fields.Many2one('stock.location', 'Source Location', required=False,
                                  domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                  states={'draft': [('readonly', False)]}, check_company=True,
                                  help="Location where the system will request components from.")
    date = fields.Datetime('Date',default=fields.Datetime.now)
    picking_type_id = fields.Many2one('stock.picking.type',string='Operation Type')
    item_ids = fields.One2many('stock.request.create.item','request_id',)

    def apply(self):
        if self.env.context.get('active_ids') and self.env.context.get('active_model') == 'mrp.production':
            mrp_productions = self.env['mrp.production'].browse(self.env.context.get('active_ids'))
        elif self.request_ids:
            mrp_productions = self.mrp_production_ids
        else:
            raise UserError(_("No Manufacturing source detected!"))
        mrp_productions._action_make_stock_request(self.location_id,
                                                   self.item_ids,
                                                   date=self.date,
                                                   picking_type_id=self.picking_type_id)



class StockRequestCreateItem(models.TransientModel):
    _name = 'stock.request.create.item'

    request_id = fields.Many2one('stock.request.create')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string="Quantity", digits='Product Unit of Measure')
    quantity_to_request = fields.Float(string="Quantity to request", digits='Product Unit of Measure', requied=True)
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure', required=True)
    move_raw_ids = fields.Many2many('stock.move',string="Source Manufacturing order Components")
    scheduled_date = fields.Datetime('Scheduled Date', default=fields.Datetime.now, )