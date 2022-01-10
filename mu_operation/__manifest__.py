# Copyright Alitec (<http://alitec.sg>).
{
    'name': 'May-mizu Operation',
    'version': '14.00.00.32',
    'category': 'Alitec',
    'sequence': 60,
    'summary': '',
    'description': """
Customisation for Operational data
=======================================
    - Last updated: 07-JAN-2021
    """,
    'author': 'Alitec Pte Ltd',
    'license': 'LGPL-3',
    'depends': ['sale', 'purchase','stock',
                ],
    'data': [
        'data/email_template.xml',
        # 'views/sale.xml',
        # 'views/forecasted_report.xml',
        # 'views/purchase.xml',
        # 'views/stock.xml',
        # 'views/invoice.xml',
        # 'views/partner.xml',
        # 'views/mrp.xml',
        # 'views/product.xml',
        # 'views/product_customer_name.xml',
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
