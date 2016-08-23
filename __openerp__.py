{
    'name': "Sale order expiration and reminder for contract consultancy",
    'version': '9.0.1.0',
    'depends': ['sale'],
    'author': "Bernard DELHEZ, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",
    'category': 'Sale',
    'description': 
    """Sale order expiration and reminder for contract consultancy.

- Adds an expiration date in sale order.
- Adds a selection for the expiration management.
- Adds a computed field of the number of days of the expiration date.
- Adds a cron to remind the expiration < 30 days every monday.

This module has been developed by Bernard DELHEZ @ AbAKUS it-solution.
    """,
    'data': ['views/sale_order_view.xml',
             'data/sale_order_cron.xml'],
}
