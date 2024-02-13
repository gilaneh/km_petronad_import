# -*- coding: utf-8 -*-
{
    'name': "km_petronad_import",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "Arash Homayounfar",
    'website': "https://gilaneh.com/",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Service Desk/Service Desk',
    'application': False,
    'version': '1.2.0',

    # any module necessary for this one to work correctly
    'depends': ['km_petronad', ],

    # always loaded
    'data': [
        'views/views.xml',
        'views/production_record.xml',
        'views/shutdown.xml',
        ],
    'assets': {

        },
    'license': 'LGPL-3',
}
