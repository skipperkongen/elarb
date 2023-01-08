from dataclasses import dataclass

import pandas as pd
import numpy as np
import cvxpy as cp

from elarb.models import (
    Facility,
)


def create_policy_input(facility: Facility, df: pd.DataFrame,
                        initial_soc: float = 0.0):
    return Instance(
        facility=facility,
        spot_price=df.spot_price.values,
        pv_dc_kWh_m2=df.pv_dc_kWh_m2.values,
        net_tariff=df.net_tariff.values,
        spot_demand_kWh=df.spot_demand_kWh.values,
        spot_supply_kWh=df.spot_supply_kWh.values,
        initial_soc=initial_soc,
    )


@dataclass
class Instance:
    facility: Facility
    spot_price: np.ndarray
    pv_dc_kWh_m2: np.ndarray
    net_tariff: np.ndarray
    spot_demand_kWh: np.ndarray
    spot_supply_kWh: np.ndarray
    initial_soc: float = 0.0


@dataclass
class Solution:
    value: float
    x1: np.ndarray
    x2: np.ndarray
    x3: np.ndarray
    x4: np.ndarray
    x1_contrib: float
    x2_contrib: float
    x3_contrib: float
    x4_contrib: float
    panel_depreciation: float
    inverter_depreciation: float
    battery_depreciation: float
    battery_soc_kWh: np.ndarray


def optimise(input: Instance, solver='ECOS_BB') -> Solution:
    """
               ┌───────┐
        ┌─x1──▶│ Grid  │──┐
        │      └───────┘  │
    ┌───────┐      ▲      │
    │ Solar │      │x3    │x4
    └───────┘      │      │
        │      ┌───────┐  │
        └─x2──▶│Battery│◀─┘
               └───────┘
    """

    n = len(input.spot_price)

    # variables
    x1 = cp.Variable(n, nonneg=True)  # solar to grid
    x2 = cp.Variable(n, nonneg=True)  # solar to battery
    x3 = cp.Variable(n, nonneg=True)  # battery to grid
    x4 = cp.Variable(n, nonneg=True)  # grid to battery

    # grid
    spot_demand_kWh = cp.Parameter(n, nonneg=True)
    spot_demand_kWh.value = input.spot_demand_kWh
    spot_supply_kWh = cp.Parameter(n, nonneg=True)
    spot_supply_kWh.value = input.spot_supply_kWh

    # panels
    panel_supply_kWh = cp.Parameter(n, nonneg=True)
    irradiance_kWh = input.pv_dc_kWh_m2 * input.facility.panel.m2
    peak_kWh = np.zeros(n) + input.facility.panel.peak_kWh
    panel_supply_kWh.value = (
        input.facility.n_panels
        * np.minimum(irradiance_kWh, peak_kWh)
    )
    panel_depreciation = cp.Parameter(nonneg=True)
    panel_depreciation.value = (
        n
        * input.facility.n_panels
        * input.facility.panel.depreciation_per_hour
    )

    # batteries
    battery_residual = 1 - input.facility.battery.conversion_loss_pct
    # cumulative sum of input - output of battery over all times t
    battery_cap_kWh = input.facility.n_batteries * \
        input.facility.battery.capacity_kWh

    battery_soc_kWh_lag = cp.hstack([
        [input.initial_soc],
        (x2 * battery_residual + x4 * battery_residual - x3)[:-1]
    ])
    battery_soc_kWh = cp.cumsum(
        battery_soc_kWh_lag
    )
    battery_depreciation = cp.sum(
        x3) * input.facility.battery.depreciation_per_kWh

    # battery_soc_kWh = cp.cumsum(
    #     x2 * battery_residual + x4 * battery_residual - x3
    # )
    # battery_depreciation = cp.sum(x3) * input.battery.depreciation_per_kWh

    # inverters
    # input.facility.inverter.throughput_kWh
    # input.facility.inverter.conversion_loss_pct
    # input.facility.inverter.depreciation_per_hour
    inverter_depreciation = cp.Parameter(nonneg=True)
    inverter_depreciation.value = (
        n
        * input.facility.n_inverters
        * input.facility.inverter.depreciation_per_hour
    )

    # panel to grid
    yield1 = cp.Parameter(n)
    yield1.value = input.spot_price - input.net_tariff

    # solar to battery
    yield2 = cp.Parameter(n)
    yield2.value = np.zeros(n)

    # battery to grid
    yield3 = cp.Parameter(n)
    yield3.value = input.spot_price - input.net_tariff

    # grid to battery
    yield4 = cp.Parameter(n)
    yield4.value = -(input.spot_price + input.net_tariff)

    # objective
    x1_contrib = yield1@x1
    x2_contrib = yield2@x2
    x3_contrib = yield3@x3
    x4_contrib = yield4@x4
    objective = cp.Maximize(cp.sum(
        x1_contrib
        + x2_contrib
        + x3_contrib
        + x4_contrib
        - (panel_depreciation + inverter_depreciation + battery_depreciation)
    ))

    # constraints
    constraints = []
    # buying constraints
    constraints += [
        # TODO: check behavior of array <= array in constraint
        # buys cannot exceed supply of solar panels
        x1 + x2 <= panel_supply_kWh,
        # buys cannot exceed state of charge of battery
        x3 <= battery_soc_kWh,
        # buys cannot exceed supply (i.e., available to buy) of grid
        x4 <= spot_supply_kWh,
    ]
    # selling constraints
    constraints += [
        # sales to grid cannot exceed grid demand
        x1 + x3 <= spot_demand_kWh,
        # sales to battery cannot exceed remaining free space of battery
        x2 + x4 <= battery_cap_kWh - battery_soc_kWh,
    ]
    # capacity constraints
    constraints += [
        # SoC cannot exceed battery capacity
        cp.max(battery_soc_kWh) <= battery_cap_kWh,
    ]
    # throughput constraints
    constraints += [
        # cannot exceed inverter throughput
        x1 + x2 + x3 + x4 <= input.facility.n_inverters * \
        input.facility.inverter.throughput_kWh,
        # cannot exceed battery throughput
        x2 + x3 + x4 <= input.facility.n_batteries * \
        input.facility.battery.throughput_kWh,
        # cannot exceed grid throughput
        x1 + x3 + x4 <= input.facility.grid.throughput_kWh,
    ]

    prob = cp.Problem(objective, constraints)
    opt = prob.solve(solver=solver)

    return Solution(
        value=opt,
        x1=x1.value,
        x2=x2.value,
        x3=x3.value,
        x4=x4.value,
        x1_contrib=x1_contrib.value,
        x2_contrib=x2_contrib.value,
        x3_contrib=x3_contrib.value,
        x4_contrib=x4_contrib.value,
        panel_depreciation=panel_depreciation.value,
        inverter_depreciation=inverter_depreciation.value,
        battery_depreciation=battery_depreciation.value,
        battery_soc_kWh=battery_soc_kWh.value,
    )
