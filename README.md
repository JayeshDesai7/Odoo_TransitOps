# TransitOps — Smart Transport Operations

An Odoo 19 application module for managing fleet vehicles, drivers, trip dispatch, maintenance, and operational analytics. Built on top of Odoo's **Fleet**, **HR**, and **HR Expense** apps.

**Version:** 19.0.1.0.0  
**License:** LGPL-3  
**Authors:** TransitOps Hackathon Team (Dev, Jayesh, Chirag)

---

## Features

### Vehicle Management
- Extends `fleet.vehicle` with **max load capacity** (enforced against trip cargo weight)
- **Unique registration numbers** across the fleet
- Custom vehicle lifecycle states: **Available**, **On Trip**, **In Shop**, **Retired**
- Computed operational metrics per vehicle:
  - Total fuel cost, maintenance cost, and combined operational cost
  - Trip revenue, ROI, and fuel efficiency (km/L)

### Driver Management
- Extends `res.partner` with driver-specific fields:
  - License number, category (LMV / HMV / Transport / Trailer), and expiry date
  - Safety score (0–100)
  - Driver status: Available, On Trip, Off Duty, Suspended
- Unique license numbers among flagged drivers

### Trip Dispatch
- New `fleet.trip` model with a full dispatch lifecycle:
  - **Draft → Dispatched → Completed** (or Cancelled)
- Automatic vehicle and driver status updates on dispatch and completion
- Business rule enforcement:
  - Cargo weight cannot exceed vehicle max load capacity
  - Suspended drivers, expired licenses, and unavailable vehicles are blocked
  - Retired or in-shop vehicles cannot be dispatched

### Maintenance
- Extends `fleet.vehicle.log.services` with fuel liters and active maintenance tracking
- Creating an active service record sets the vehicle to **In Shop**
- Closing maintenance restores the vehicle to **Available** (unless Retired)

### Dashboard
- OWL-based dashboard with real-time KPIs:
  - Active / available / in-shop vehicles
  - Active and pending trips
  - Drivers on duty and fleet utilization %
- Filterable by vehicle type and status
- Per-vehicle analytics: fuel efficiency, operational cost, ROI

### Reports
- CSV export wizard for:
  - Fuel Efficiency
  - Fleet Utilization
  - Operational Cost
  - Vehicle ROI

### Security & Roles
Four TransitOps roles with scoped access:

| Role | Capabilities |
|---|---|
| **Fleet Manager** | Full fleet, trip, and maintenance management |
| **Dispatcher** | Create and manage trips; assign vehicles and drivers |
| **Safety Officer** | Read-only access to driver and vehicle compliance data |
| **Financial Analyst** | Read-only access to cost and revenue data |

Record rules enforce read-only access for Safety Officer and Financial Analyst, and prevent dispatchers from modifying retired vehicles.

---

## Requirements

- **Odoo 19**
- Odoo modules: `fleet`, `hr`, `hr_expense`, `mail`

---

## Installation

1. Clone or copy this repository into your Odoo addons directory and rename the folder to `transitops`:

   ```bash
   cp -r Odoo_TransitOps /path/to/odoo/addons/transitops
   ```

2. Restart the Odoo server and update the apps list:

   ```bash
   ./odoo-bin -c odoo.conf -u all -d your_database --stop-after-init
   ```

   Or from the Odoo UI: **Apps → Update Apps List**.

3. Search for **TransitOps** in Apps and click **Install**.

4. Assign users to the appropriate TransitOps roles under **Settings → Users → Access Rights**.

---

## Usage

After installation, open the **TransitOps** app from the main menu.

### Setup
1. **Vehicles** — Add fleet vehicles with registration number and max load capacity.
2. **Drivers** — Create contacts flagged as TransitOps drivers with license details.
3. **Maintenance** — Log fuel and service records on vehicle forms.

### Dispatch a Trip
1. Go to **TransitOps → Trips → Create**.
2. Enter source, destination, vehicle, driver, and cargo weight.
3. Click **Dispatch** to assign the trip (vehicle → On Trip, driver → On Trip).
4. On completion, enter final odometer and fuel consumed, then click **Complete**.

### Dashboard & Reports
- **Dashboard** — Monitor fleet KPIs and per-vehicle analytics.
- **Reports** — Export CSV reports for fuel efficiency, utilization, costs, and ROI.

---

## Project Structure

```
transitops/
├── __init__.py
├── __manifest__.py
├── data/
│   └── fleet_vehicle_state_data.xml    # Vehicle states & trip sequence
├── models/
│   ├── fleet_trip.py                   # Trip dispatch model & workflow
│   ├── fleet_vehicle.py                # Vehicle extensions & ROI metrics
│   ├── fleet_vehicle_log_services.py   # Maintenance & fuel logging
│   └── res_partner.py                  # Driver fields & validation
├── security/
│   ├── transitops_groups.xml           # Role definitions
│   ├── ir.model.access.csv             # Model access rights
│   └── transitops_record_rules.xml     # Record-level security rules
├── static/
│   └── src/
│       ├── js/transitops_dashboard.js    # Dashboard OWL component
│       ├── xml/transitops_dashboard.xml  # Dashboard template
│       └── scss/transitops_dashboard.scss
├── views/
│   ├── fleet_trip_views.xml
│   ├── fleet_vehicle_views.xml
│   ├── transitops_dashboard_action.xml
│   └── transitops_menus.xml
└── wizard/
    ├── transitops_csv_export.py        # CSV report export wizard
    └── transitops_csv_export_views.xml
```

---

## Milestone 1 — Foundation

This release covers the foundation milestone:

- Vehicle and driver model extensions
- Trip dispatch workflow with business rules
- Four TransitOps security roles
- Operational cost and ROI computations
- Dashboard and CSV reporting

---




