# my_library/__manifest__.py
{
    'name': 'My Library',
    'version': '1.5.1',
    'summary': 'Manage your book collection and library members',
    'sequence': 10,
    'description': """
        A module to manage books and library members.
    """,
    'category': 'Custom',
    'author': 'Kshitij Pandey',
    'website': 'https://www.yourwebsite.com',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/library_book_views.xml',
        'views/library_member_views.xml',
        'views/library_loan_views.xml',
        'views/library_menu.xml', # <--- ENSURE THIS LINE IS PRESENT
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}