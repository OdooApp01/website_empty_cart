# Part of Odoo. See LICENSE file for full copyright and licensing details.

from . import controllers
from . import models
from odoo.exceptions import ValidationError

from odoo.addons.payment import reset_payment_acquirer


def uninstall_hook(cr, registry):
    reset_payment_acquirer(cr, registry, 'cash_free')

def pre_init_hook(self):
    from odoo.release import series
    if series !='15.0':
        raise ValidationError("This server support 15.0 version not {}".format(series))

