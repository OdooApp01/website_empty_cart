# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hashlib
import requests
import json
from odoo import api, fields, models
from odoo.exceptions import UserError
from logging import getLogger

_logger = getLogger(__name__)



class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('cash_free', "Cash Free")], ondelete={'cash_free': 'set default'})
    cash_free_app_id = fields.Char(
        string="APP ID", required_if_provider='cash_free', groups='base.group_system')
    cash_free_api_key = fields.Char(
        string="API KEY", help="The key solely used to identify the account api key",
        required_if_provider='cash_free')
    
    API_END = {'test':'https://sandbox.cashfree.com/pg/orders',
                'enabled':'https://api.cashfree.com/pg/orders'}
    

    # @api.model
    # def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
    #     """ Override of payment to unlist cash free acquirers when the currency is not INR. """
    #     acquirers = super()._get_compatible_acquirers(*args, currency_id=currency_id, **kwargs)
    #     currency = self.env['res.currency'].browse(currency_id).exists()
    #     if currency and currency.name != 'INR':
    #         acquirers = acquirers.filtered(lambda a: a.provider != 'cash_free')
    #     return acquirers

    def _get_request_data(self, payload):
        headers = {
        "Accept": "application/json",
        "x-client-id": self.cash_free_app_id,
        "x-client-secret": self.cash_free_api_key,
        "x-api-version": "2022-01-01",
        "Content-Type": "application/json"
         }
        url = self.API_END.get(self.state)
        response = requests.post(url, json=payload, headers=headers)
        response = json.loads(response.text)
        if not response.get('payment_link'):
            raise UserError(response.get('message'))
        return response

    def _tx_prepare_values(self,data):
        base_url = self.env['ir.config_parameter'].search([('key','=','web.base.url')],limit=1)
        payload = {
        "customer_details": {
            "customer_id": str(data.get('partner_id')),
            "customer_email": data.get('parnter_email'),
            "customer_phone": data.get('partner_phone')
        },
        "order_meta": {"return_url": base_url.value+'/payment/cash_free/return?order_id={order_id}&order_token={order_token}'},
        "order_id": data.get('order_id'),
        "order_amount": data.get('amount'),
        "order_currency": "INR"
        }
        return payload

    def _get_tx_generated_values(self,data):
        payload = self._tx_prepare_values(data)
        tx_url = self._get_request_data(payload)
        data['api_url'] = tx_url.get('payment_link')
        return data
        

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'cash_free':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_cash_free_01.payment_method_cash_free').id
