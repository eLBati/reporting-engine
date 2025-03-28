{
    'name': "Report PDF Fixed Position",
    'summary': "",
    'author': "Innovyou",
    'website': "http://www.innovyou.it",
    'category': 'web',
    'version': '16.0.1.0.0',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'mail',
        'web'
    ],
    'assets': {
        "web.assets_backend": [
            "report_pdf_fixed_position/static/src/js/widget_owl.js",
            "report_pdf_fixed_position/static/src/xml/widget_template.xml",
            "report_pdf_fixed_position/static/src/scss/modal.scss",
        ],
    },
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'menu/actions.xml',
        'menu/items.xml',

        'views/report_views.xml',
        'views/report_placeholder_views.xml',
        'views/report_placeholder_font_views.xml',

        'wizards/views/preview_wizard_views.xml',
    ],
    'post_init_hook': 'post_init_hook'
}