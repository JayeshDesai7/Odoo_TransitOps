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
        'maintenance',
        'hr_expense',
        'mail',
    ],
    'data': [
        'security/transitops_groups.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}