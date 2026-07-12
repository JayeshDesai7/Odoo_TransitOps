{
    'name': 'TransitOps - Smart Transport Operations',
    'version': '19.0.1.0.0',
    'category': 'Operations/Fleet',
    'summary': 'Vehicle, driver, dispatch, maintenance and expense management on top of Fleet',
    'description': """
TransitOps
==========
Milestone 1: Foundation
- Extends fleet.vehicle with max load capacity and registration uniqueness.
- Extends res.partner with license category, safety score, and driver status.
- Defines the 4 TransitOps roles: Fleet Manager, Dispatcher, Safety Officer, Financial Analyst.
""",
    'author': 'TransitOps Hackathon Team (Dev, Jayesh, Chirag)',
    'depends': [
        'fleet',
        'hr',
        'hr_expense',
        'mail',
    ],
    'data': [
        'security/transitops_groups.xml',
        'security/ir.model.access.csv',
        'security/transitops_record_rules.xml',
        'data/fleet_vehicle_state_data.xml',
        'views/transitops_dashboard_action.xml',
        'views/fleet_trip_views.xml',
        'views/fleet_vehicle_views.xml',
        'wizard/transitops_csv_export_views.xml',
        'views/transitops_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'transitops/static/src/js/transitops_dashboard.js',
            'transitops/static/src/xml/transitops_dashboard.xml',
            'transitops/static/src/scss/transitops_dashboard.scss',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
