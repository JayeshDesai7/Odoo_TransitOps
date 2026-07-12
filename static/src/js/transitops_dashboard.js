/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class TransitopsDashboard extends Component {
    static template = "transitops.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            kpis: {
                active_vehicles: 0,
                available_vehicles: 0,
                in_shop_vehicles: 0,
                active_trips: 0,
                pending_trips: 0,
                drivers_on_duty: 0,
                fleet_utilization: 0,
            },
            filters: { vehicle_type: false, status: false, region: false },
            vehicleTypes: [],
            analytics: [], // per-vehicle: name, fuel_efficiency, total_operational_cost, roi
        });
        onWillStart(async () => {
            await this.loadFilterOptions();
            await this.loadKpis();
            await this.loadAnalytics();
        });
    }

    _buildVehicleDomain() {
        const domain = [];
        if (this.state.filters.vehicle_type) {
            domain.push(["model_id.vehicle_type", "=", this.state.filters.vehicle_type]);
        }
        if (this.state.filters.status) {
            domain.push(["state_id.name", "=", this.state.filters.status]);
        }
        // 'region' has no native Fleet field — deliberately left as a
        // client-side no-op filter until a region field is added to
        // fleet.vehicle; flagging rather than silently dropping it.
        return domain;
    }

    async loadFilterOptions() {
        this.state.vehicleTypes = await this.orm.call(
            "fleet.vehicle.model.category", "search_read", [[], ["id", "name"]]
        );
    }

    async onFilterChange(field, value) {
        this.state.filters[field] = value || false;
        await this.loadKpis();
        await this.loadAnalytics();
    }

    async loadKpis() {
        const domain = this._buildVehicleDomain();
        const [totalVehicles, availableVehicles, inShopVehicles,
               activeTrips, pendingTrips, driversOnDuty] = await Promise.all([
            this.orm.searchCount("fleet.vehicle", [
                ...domain, ["state_id.name", "!=", "Retired"]]),
            this.orm.searchCount("fleet.vehicle", [
                ...domain, ["state_id.name", "=", "Available"]]),
            this.orm.searchCount("fleet.vehicle", [
                ...domain, ["state_id.name", "=", "In Shop"]]),
            this.orm.searchCount("fleet.trip", [["state", "=", "dispatched"]]),
            this.orm.searchCount("fleet.trip", [["state", "=", "draft"]]),
            this.orm.searchCount("res.partner", [
                ["is_transitops_driver", "=", true],
                ["driver_status", "=", "on_trip"]]),
        ]);
        const onTripVehicles = totalVehicles - availableVehicles - inShopVehicles;
        this.state.kpis = {
            active_vehicles: totalVehicles,
            available_vehicles: availableVehicles,
            in_shop_vehicles: inShopVehicles,
            active_trips: activeTrips,
            pending_trips: pendingTrips,
            drivers_on_duty: driversOnDuty,
            fleet_utilization: totalVehicles
                ? Math.round((onTripVehicles / totalVehicles) * 100)
                : 0,
        };
    }

    async loadAnalytics() {
        const domain = this._buildVehicleDomain();
        this.state.analytics = await this.orm.searchRead(
            "fleet.vehicle", domain,
            ["display_name", "fuel_efficiency", "total_operational_cost", "roi"],
            { limit: 20 }
        );
    }
}

registry.category("actions").add("transitops_dashboard", TransitopsDashboard);
