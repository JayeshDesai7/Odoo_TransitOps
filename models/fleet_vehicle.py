# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FleetVehicle(models.Model):
    """Extends Odoo's core fleet.vehicle rather than creating a new model.

    Reused as-is from Fleet:
      - license_plate      -> Registration Number
      - model_id           -> Vehicle Name/Model (+ category for Type)
      - odometer            -> Odometer
      - car_value            -> Acquisition Cost
      - state_id              -> Status (Available/On Trip/In Shop/Retired
                                  are configured as fleet.vehicle.state
                                  records via data/demo, not hardcoded here)
      - driver_id             -> currently assigned driver
    """
    _inherit = 'fleet.vehicle'

    max_load_capacity = fields.Float(
        string='Max Load Capacity (kg)',
        help='Maximum cargo weight this vehicle can carry. '
             'Enforced against Trip cargo weight in the Trip Management milestone.',
    )

    _sql_constraints = [
        (
            'transitops_license_plate_unique',
            'unique(license_plate)',
            'Registration Number must be unique across the fleet.',
        ),
    ]

    @api.constrains('max_load_capacity')
    def _check_max_load_capacity(self):
        for vehicle in self:
            if vehicle.max_load_capacity < 0:
                raise ValidationError('Max Load Capacity cannot be negative.')
