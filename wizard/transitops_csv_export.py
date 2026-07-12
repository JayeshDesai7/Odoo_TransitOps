# -*- coding: utf-8 -*-
import base64
import csv
import io

from odoo import fields, models


class TransitopsCsvExport(models.TransientModel):
    _name = 'transitops.csv.export'
    _description = 'TransitOps Report CSV Export'

    report_type = fields.Selection(
        selection=[
            ('fuel_efficiency', 'Fuel Efficiency'),
            ('fleet_utilization', 'Fleet Utilization'),
            ('operational_cost', 'Operational Cost'),
            ('vehicle_roi', 'Vehicle ROI'),
        ],
        required=True, default='vehicle_roi',
    )
    file_data = fields.Binary(readonly=True)
    file_name = fields.Char(readonly=True)

    def action_export(self):
        self.ensure_one()
        vehicles = self.env['fleet.vehicle'].search([])
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            'Vehicle', 'Fuel Cost', 'Maintenance Cost',
            'Operational Cost', 'Revenue', 'Fuel Efficiency (km/L)', 'ROI',
        ])
        for vehicle in vehicles:
            writer.writerow([
                vehicle.display_name,
                vehicle.total_fuel_cost,
                vehicle.total_maintenance_cost,
                vehicle.total_operational_cost,
                vehicle.total_trip_revenue,
                vehicle.fuel_efficiency,
                vehicle.roi,
            ])
        self.file_data = base64.b64encode(buffer.getvalue().encode('utf-8'))
        self.file_name = f'transitops_{self.report_type}.csv'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'transitops.csv.export',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
