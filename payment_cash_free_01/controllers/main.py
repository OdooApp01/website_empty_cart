# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import requests
import json

from odoo import http
from odoo.http import request


_logger = logging.getLogger(__name__)


class CashFreeController(http.Controller):
    _return_url = '/payment/cash_free/return'
    payment_status_url = "https://sandbox.cashfree.com/pg/orders/{}/payments"

    @http.route(_return_url, type='http', auth='public', methods=['GET', 'POST'], csrf=False,save_session=False)
    def cash_free_return_01(self, **data):
        """ Process the data returned by cash free after redirection.
            after the redirection get the payment details like status.
        :param dict data: The feedback data to process
        """
        acquirer = request.env['payment.acquirer'].search([('provider','=','cash_free')],limit=1)
        HEADERS = {"Accept":"application/Json",
                  "x-client-id": acquirer.cash_free_app_id,
                  "x-client-secret": acquirer.cash_free_api_key,
                  "x-api-version": "2022-01-01"
                  }
        order_id = data.get('order_id')

        payment_status = requests.get(self.payment_status_url.format(order_id),headers=HEADERS)
        payment_status = json.loads(payment_status.text)[0]
        _logger.info("entering handle_feedback_data with data:\n%s", payment_status)
        payment_status['reference'] = order_id

        _logger.info("entering handle_feedback_data with data:\n%s", data)
        request.env['payment.transaction'].sudo()._handle_feedback_data('cash_free', payment_status)
        return request.redirect('/payment/status')
