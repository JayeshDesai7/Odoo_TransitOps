# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class FleetTrip(models.Model):
    _name = "fleet.trip"
    _description = "TransitOps Trip"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        default=lambda self: "New",
        copy=False,
        readonly=True,
    )
    source = fields.Char(required=True, tracking=True)
    destination = fields.Char(required=True, tracking=True)
    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehicle",
        required=True,
        tracking=True,
        domain="[('state_id.name', '=', 'Available')]",
    )
    driver_id = fields.Many2one(
        "res.partner",
        string="Driver",
        required=True,
        tracking=True,
        domain="[('is_transitops_driver', '=', True), "
        "('driver_status', '=', 'available')]",
    )
    cargo_weight = fields.Float(required=True)
    planned_distance = fields.Float(string="Planned Distance (km)")
    final_odometer = fields.Float(string="Final Odometer")
    fuel_consumed = fields.Float(string="Fuel Consumed (L)")
    revenue = fields.Float(
        string="Trip Revenue",
        help="Manual entry — feeds the Vehicle ROI report. "
        "No billing/invoicing link exists for trips yet.",
    )
    dispatch_date = fields.Datetime(readonly=True)
    completion_date = fields.Datetime(readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("dispatched", "Dispatched"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fleet.trip") or "New"
                )
        return super().create(vals_list)

    # ---- Mandatory Business Rules (Doc 2, section 4) ----
    @api.constrains("cargo_weight", "vehicle_id")
    def _check_cargo_capacity(self):
        for trip in self:
            if (
                trip.vehicle_id
                and trip.cargo_weight > trip.vehicle_id.max_load_capacity
            ):
                raise ValidationError(
                    f"Cargo Weight ({trip.cargo_weight} kg) exceeds "
                    f"{trip.vehicle_id.display_name}'s max load capacity "
                    f"({trip.vehicle_id.max_load_capacity} kg)."
                )

    def _check_driver_eligible(self, driver):
        if driver.driver_status == "suspended":
            raise UserError(f"{driver.name} is Suspended and cannot be assigned.")
        if (
            driver.license_expiry_date
            and driver.license_expiry_date < fields.Date.today()
        ):
            raise UserError(
                f"{driver.name}'s license expired on "
                f"{driver.license_expiry_date}; cannot be assigned."
            )
        if driver.driver_status == "on_trip":
            raise UserError(f"{driver.name} is already On Trip.")

    def _check_vehicle_eligible(self, vehicle):
        state_name = vehicle.state_id.name if vehicle.state_id else False
        if state_name in ("Retired", "In Shop"):
            raise UserError(
                f"{vehicle.display_name} is {state_name} and cannot be dispatched."
            )
        if state_name == "On Trip":
            raise UserError(f"{vehicle.display_name} is already On Trip.")

    def action_dispatch(self):
        state_on_trip = self.env.ref("transitops.fleet_vehicle_state_on_trip")
        for trip in self:
            if trip.state != "draft":
                raise UserError("Only Draft trips can be dispatched.")
            trip._check_vehicle_eligible(trip.vehicle_id)
            trip._check_driver_eligible(trip.driver_id)
            trip.vehicle_id.state_id = state_on_trip
            trip.driver_id.driver_status = "on_trip"
            trip.write(
                {
                    "state": "dispatched",
                    "dispatch_date": fields.Datetime.now(),
                }
            )

    def action_complete(self):
        state_available = self.env.ref("transitops.fleet_vehicle_state_available")
        for trip in self:
            if trip.state != "dispatched":
                raise UserError("Only Dispatched trips can be completed.")
            trip.vehicle_id.state_id = state_available
            trip.vehicle_id.odometer = trip.final_odometer or trip.vehicle_id.odometer
            trip.driver_id.driver_status = "available"
            trip.write(
                {
                    "state": "completed",
                    "completion_date": fields.Datetime.now(),
                }
            )

    def action_cancel(self):
        state_available = self.env.ref("transitops.fleet_vehicle_state_available")
        for trip in self:
            if trip.state == "completed":
                raise UserError("Completed trips cannot be cancelled.")
            if trip.state == "dispatched":
                trip.vehicle_id.state_id = state_available
                trip.driver_id.driver_status = "available"
            trip.state = "cancelled"
