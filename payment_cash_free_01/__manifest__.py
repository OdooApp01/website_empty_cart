
{
    'name': 'Payment Acquirer Cash Free 01',
    'version': '15.0.0',
    'category': 'Accounting/Payment Acquirers',
    'sequence': 377,
    'summary': 'Payment Acquirer: Payment Cash Free Implementation',
    'description': """
        Cash Free Payment Acquirer for India.
        Cash Free is a indian payment gateway supports many currency.
        """,
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_payumoney_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'application': True,
    'pre_init_hook':'pre_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'price': 20,
    'currency': 'USD',
    'license': 'LGPL-3',

}
