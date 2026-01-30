{
    "name": "Invoice Billing Period",
    "version": "1.0",
    "category": "Accounting",
    "summary": "Link recurring products to calendar events",
    "depends": [
        "calendar",
        "product",
        "account",
    ],
    "data": [
        "views/calendar_event_view.xml",
        "views/account_move_view.xml",
        "views/product_template_view.xml",
    ],
    "installable": True,
}
