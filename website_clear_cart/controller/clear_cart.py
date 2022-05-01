from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import route, request
from logging import getLogger

_logger = getLogger(__name__)

class WebsiteSaleCart(WebsiteSale):

    @route('/website/clear/cart',type='http',auth='public',website=True)
    def website_clear_cart(self):
        sale_order = request.website.sale_get_order()
        if sale_order.order_line:
            sale_order.order_line.unlink()
            return request.redirect('/shop/cart')
    