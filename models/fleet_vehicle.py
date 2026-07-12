# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    max_load_capacity = fields.Float(
        string='Max Load Capacity (kg)',
        help='Maximum cargo weight this vehicle can carry. '
             'Enforced against Trip cargo weight.',
    )

    total_fuel_cost = fields.Monetary(
        compute='_compute_operational_costs', store=True,
        currency_field='currency_id',
    )
    total_maintenance_cost = fields.Monetary(
        compute='_compute_operational_costs', store=True,
        currency_field='currency_id',
    )
    total_operational_cost = fields.Monetary(
        compute='_compute_operational_costs', store=True,
        currency_field='currency_id',
        help='Fuel + Maintenance, per spec 3.7.',
    )
    total_trip_revenue = fields.Monetary(
        compute='_compute_operational_costs', store=True,
        currency_field='currency_id',
    )
    roi = fields.Float(
        string='ROI',
        compute='_compute_operational_costs', store=True,
        help='(Revenue - (Maintenance + Fuel)) / Acquisition Cost',
    )
    fuel_efficiency = fields.Float(
        string='Fuel Efficiency (km/L)',
        compute='_compute_operational_costs', store=True,
    )
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id,
    )

    log_fuel = fields.One2many(
        'fleet.vehicle.log.services',
        compute='_compute_log_fuel',
        string='Fuel Logs',
    )

    @api.depends('log_services.service_type_id', 'log_services.amount', 'log_services.liter')
    def _compute_log_fuel(self):
        refueling_type = self.env.ref('fleet.type_service_refueling', raise_if_not_found=False)
        refueling_id = refueling_type.id if refueling_type else False
        for vehicle in self:
            if refueling_id:
                vehicle.log_fuel = vehicle.log_services.filtered(
                    lambda s: s.service_type_id.id == refueling_id
                )
            else:
                vehicle.log_fuel = vehicle.log_services.filtered(
                    lambda s: s.service_type_id.name == 'Refueling'
                )

    @api.depends(
        'log_services.amount', 'log_services.liter', 'log_services.service_type_id',
        'trip_ids.revenue', 'trip_ids.state', 'trip_ids.planned_distance',
        'car_value',
    )
    def _compute_operational_costs(self):
        refueling_type = self.env.ref('fleet.type_service_refueling', raise_if_not_found=False)
        refueling_id = refueling_type.id if refueling_type else False

        for vehicle in self:
            if refueling_id:
                fuel_logs = vehicle.log_services.filtered(lambda s: s.service_type_id.id == refueling_id)
                maintenance_logs = vehicle.log_services.filtered(lambda s: s.service_type_id.id != refueling_id)
            else:
                fuel_logs = vehicle.log_services.filtered(lambda s: s.service_type_id.name == 'Refueling')
                maintenance_logs = vehicle.log_services.filtered(lambda s: s.service_type_id.name != 'Refueling')

            vehicle.total_maintenance_cost = sum(maintenance_logs.mapped('amount'))
            vehicle.total_fuel_cost = sum(fuel_logs.mapped('amount'))
            vehicle.total_operational_cost = (
                vehicle.total_maintenance_cost + vehicle.total_fuel_cost
            )
            completed_trips = vehicle.trip_ids.filtered(
                lambda t: t.state == 'completed')
            vehicle.total_trip_revenue = sum(completed_trips.mapped('revenue'))
            vehicle.roi = (
                (vehicle.total_trip_revenue - vehicle.total_operational_cost)
                / vehicle.car_value if vehicle.car_value else 0.0
            )
            total_liters = sum(fuel_logs.mapped('liter'))
            total_distance = sum(completed_trips.mapped('planned_distance'))
            vehicle.fuel_efficiency = (
                total_distance / total_liters if total_liters else 0.0
            )

    trip_ids = fields.One2many('fleet.trip', 'vehicle_id', string='Trips')

    _sql_constraints = [
        ('transitops_license_plate_unique',
        'unique(license_plate)',
        'Registration Number must be unique across the fleet.',
        ),
            ]

    @api.constrains('max_load_capacity')
    def _check_max_load_capacity(self):
        for vehicle in self:
            if vehicle.max_load_capacity < 0:
                raise ValidationError('Max Load Capacity cannot be negative.')
