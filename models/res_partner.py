# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_transitops_driver = fields.Boolean(
        string='Is TransitOps Driver',
        help='Flag used to filter driver-eligible partners in Trip assignment '
             'without polluting the general contact list.',
    )
    license_number = fields.Char(string='License Number')
    license_category = fields.Selection(
        selection=[
            ('lmv', 'LMV - Light Motor Vehicle'),
            ('hmv', 'HMV - Heavy Motor Vehicle'),
            ('transport', 'Transport'),
            ('trailer', 'Trailer'),
        ],
        string='License Category',
    )
    license_expiry_date = fields.Date(string='License Expiry Date')
    safety_score = fields.Float(
        string='Safety Score',
        default=100.0,
        help='0-100. Lowered by incident logging in a later milestone.',
    )
    driver_status = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('on_trip', 'On Trip'),
            ('off_duty', 'Off Duty'),
            ('suspended', 'Suspended'),
        ],
        string='Driver Status',
        default='available',
    )

    @api.constrains('license_number', 'is_transitops_driver')
    def _check_license_number_unique(self):
        for partner in self:
            if partner.is_transitops_driver and partner.license_number:
                duplicate = self.search([
                    ('id', '!=', partner.id),
                    ('is_transitops_driver', '=', True),
                    ('license_number', '=', partner.license_number),
                ], limit=1)
                if duplicate:
                    raise ValidationError(
                        'License Number must be unique among drivers.'
                    )
