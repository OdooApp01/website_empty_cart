# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug import urls
from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.addons.payment import utils as payment_utils

from logging import getLogger
_logger = getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return cash free specific rendering values.
        Note: self.ensure_one() from `_get_processing_values`
        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'cash_free':
            return res
        currency_record = self.env['res.currency'].browse(processing_values.get('currency_id'))
        tx_values = {
            'partner_id': self.partner_id.id,
            'partner_email': self.partner_email,
            'partner_phone': self.partner_phone,
            'order_id'     : processing_values.get('reference'),
            'currency'     : currency_record
             }
        processing_values.update(tx_values)
        tx_data = self.acquirer_id._get_tx_generated_values(processing_values)

        return tx_data

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        """ Override of payment to find the transaction based on cash free data.
        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        :raise: ValidationError if the signature can not be verified
        """
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'cash_free':
            return tx
        reference = data.get('order_id')
        tx = self.search([('reference', '=', reference), ('provider', '=', 'cash_free')])
        if not tx:
            raise ValidationError(
                "Cash Free: " + _("No transaction found matching reference %s.", reference)
            )
        tx.acquirer_reference = tx.provider
        return tx

    def _process_feedback_data(self, data):
        """ Override of payment to process the transaction based on Cash Free data.
        Note: self.ensure_one()
        :param dict data: The feedback data sent by the provider
        :return: None
        """
        super()._process_feedback_data(data)
        if self.provider != 'cash_free':
            return
        status = data.get('payment_status')
        # self.acquirer_reference = data.get('cash_free')
        if status == 'SUCCESS':
            self._set_done()
        elif status == "CANCELLED":
            self._set_cancelled()
        elif status == "PENDING":
            self._set_pending()
        else:  # 'failure'
            error_code = data.get('payment_message')
            self._set_error(
                "Cash Free: " + _("The payment encountered an error with code:  %s", error_code)
            )
