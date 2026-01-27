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
        "account",
    ],
    "data": [
        "views/calendar_event_view.xml",
        "views/product_recurrent_view.xml",
        "views/account_move_view.xml"
    ],
    "installable": True,
}
