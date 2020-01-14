{
    'name': 'Sales performance',
    'version': '13.0.1.0.0',
    'category': 'Sale',
    'author': 'SYENTYS',
    'website': 'http://www.syentys.com',
    'depends': [
        'sale',
        'product_extend',
        'point_of_sale',
        'sales_team',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Views
        'views/sale_performance_view.xml',
    ],
    'installable': True,
}
