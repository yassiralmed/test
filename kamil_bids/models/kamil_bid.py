from odoo import models, fields, api,_

class KamilBid(models.Model):

	_name = 'kamil.bid'

	number = fields.Char(string='Number')
	name = fields.Char(string='Description')
	date = fields.Date( default=fields.Date.today() )
	forest_id = fields.Many2one('kamil.farm', string='Forest')
	state =fields.Selection([('draft','Draft'),('open','Open'),('close','Closed')], 'State', default='draft')
	line_ids = fields.One2many('kamil.bid.line','bid_id')
	sale_order_ids = fields.One2many('sale.order','the_bid_id')
	note = fields.Text()


	@api.multi
	def do_open(self):
		self.state = 'open'


	@api.multi
	def do_close(self):
		self.state = 'close'


	@api.model
	def create(self ,vals):
		vals['number'] = self.env['ir.sequence'].next_by_code('kamil.bid.sequence')
		return super(KamilBid,self).create(vals)

	@api.multi
	def action_view_sales_orders(self):
		action =self.env.ref('sale.action_orders')
		result =action.read()[0]
		for line in self.line_ids:
			result['context']={'default_the_bid_id':self.id}
			result['domain']=[('the_bid_id','=',self.id)]
			return result




class KamilBidLine(models.Model):
	
	_name = 'kamil.bid.line'

	product_id =fields.Many2one('product.product',string='Item')
	price = fields.Float(string='initial price')
	product_quantity =fields.Float(string='Quantity')
	product_uom_id = fields.Many2one('uom.uom',string='Unit Of Measure')
	
	bid_id =fields.Many2one('kamil.bid')

	@api.multi
	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id.uom_id:
			self.product_uom_id =self.product_id.uom_id.id 



class InheritSalesOrder(models.Model):

	_inherit = 'sale.order'

	the_bid_id = fields.Many2one('kamil.bid',string='Bid')

	@api.onchange('the_bid_id')
	def onchange_allowed_line_ids(self):
		for rec in self:
			products=[]
			if self.the_bid_id:
				for product in rec.the_bid_id.line_ids:
					products.append( (0,0,{
							'product_id':product.product_id.id,
							'product_uom':product.product_uom_id.id,
							'product_uom_qty' : product.product_quantity,
							'price_unit' : product.price,
							'name' : product.product_id.description_sale or product.product_id.name ,
							}) )
			self.order_line = products


class ProductProduct(models.Model):
	
	_inherit = 'product.template'

	is_forests_product = fields.Boolean(string='Is Forests And Nurseries Product ?')