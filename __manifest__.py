{
    "name": "Facturation pour services recurrents",
    "version": "1.0",
    "category": "Accounting",
    "author": "Alkyde Patrimoine",
    "license":"LGPL-3",
    "summary": "Link recurring products to calendar events",
    "depends": [
        "calendar",
        "product",
        "account"
    ],
    "data": [
        "views/calendar_event_view.xml",
        "views/calendar_event_calendar_view.xml",
        "views/product_recurrent_view.xml",
        "views/account_move_view.xml",
        "views/report_invoice.xml",
        "views/res_partner_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "calendar_prod_rec/static/src/js/attendee_calendar_model_patch.js",
            "calendar_prod_rec/static/src/scss/calendar_colors.scss",
            ],
    },
    "installable": True,
}
