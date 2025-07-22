{
    'name': 'My Library',
    'version': '1.4',
    'summary': 'Manage your book collection and library members',
    'sequence': 10,
    'description': """
        A module to manage books and library members.
    """,
    'category': 'Custom',
    'author': 'Kshitij Pandey',
    'website': 'https://www.yourwebsite.com',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/library_book_views.xml',
        'views/library_member_views.xml',
        'views/library_loan_views.xml', 
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}