# -*- coding: utf-8 -*-
from odoo import api, fields, models


class FleetVehicleLogServices(models.Model):
    """Reuses fleet.vehicle.log.services (Fleet's own vehicle-linked service/
    cost log) instead of pulling in the generic 'maintenance' app, which has
    no native vehicle awareness. Spec 3.6: creating an active record flips
    the vehicle to In Shop; closing it restores Available (unless Retired).
    """
    _inherit = 'fleet.vehicle.log.services'

    active_maintenance = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck (or use the Close button) once the service is done.',
    )

    liter = fields.Float(
        string='Liters',
        help='Amount of fuel in liters (for refueling logs)',
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        state_in_shop = self.env.ref('transitops.fleet_vehicle_state_in_shop')
        for record in records:
            if record.active_maintenance and record.vehicle_id:
                record.vehicle_id.state_id = state_in_shop
        return records

    def action_close_maintenance(self):
        state_available = self.env.ref('transitops.fleet_vehicle_state_available')
        state_retired = self.env.ref('transitops.fleet_vehicle_state_retired')
        for record in self:
            record.active_maintenance = False
            if record.vehicle_id.state_id != state_retired:
                # Only restore to Available if no OTHER active service
                # record still holds this vehicle In Shop.
                other_active = self.search([
                    ('vehicle_id', '=', record.vehicle_id.id),
                    ('active_maintenance', '=', True),
                    ('id', '!=', record.id),
                ], limit=1)
                if not other_active:
                    record.vehicle_id.state_id = state_available
