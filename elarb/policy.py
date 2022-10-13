from dataclasses import dataclass

import numpy as np
import cvxpy as cp

from elarb.models import (
    SolarPanel,
    Battery,
    Inverter,
    Grid,
)


@dataclass
class PolicyInput:
    solar: SolarPanel
    battery: Battery
    inverter: Inverter
    grid: Grid


@dataclass
class PolicyOutput:
    value: float
    x1: np.ndarray
    x2: np.ndarray
    x3: np.ndarray
    x4: np.ndarray


def get_optimal_policy(input: PolicyInput) -> PolicyOutput:
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

    n = len(input.grid.spot_price)

    # variables
    x1 = cp.Variable(n, nonneg=True)  # solar to grid
    x2 = cp.Variable(n, nonneg=True)  # solar to battery
    x3 = cp.Variable(n, nonneg=True)  # battery to grid
    x4 = cp.Variable(n, nonneg=True)  # grid to battery

    # grid
    grid_demand = cp.Parameter(n, nonneg=True)
    grid_demand.value = input.grid.demand_kWh
    grid_supply = cp.Parameter(n, nonneg=True)
    grid_supply.value = input.grid.supply_kWh

    # solar
    solar_supply = cp.Parameter(n, nonneg=True)
    solar_supply.value = input.solar.supply_kWh


    # battery
    battery_residual = 1 - input.battery.conversion_loss_pct
    # cumulative sum of input - output of battery over all times t
    battery_soc = cp.cumsum(
        x2 * battery_residual + x4 * battery_residual - x3
    )

    # inverter
    # input.inverter.throughput_kWh
    # input.inverter.conversion_loss_pct
    # input.inverter.depreciation_per_hour

    # solar to grid
    yield1 = cp.Parameter(n)
    yield1.value = input.grid.spot_price

    # solar to battery
    yield2 = cp.Parameter(n)
    yield2.value = np.zeros(n)

    # battery to grid
    yield3 = cp.Parameter(n)
    yield3.value = input.grid.spot_price - input.battery.depreciation_per_kWh

    # grid to battery
    yield4 = cp.Parameter(n)
    yield4.value = -input.grid.spot_price # - bat_depreciation

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
        - input.solar.depreciation_per_hour
        - input.inverter.depreciation_per_hour
    ))

    # constraints
    constraints = []
    # buying constraints
    constraints += [
        # buys cannot exceed output of solar panels
        x1 + x2 <= solar_supply,
        # buys cannot exceed battery state of charge
        x3 <= battery_soc,
        # buys cannot exceed grid supply (available to buy)
        x4 <= grid_supply,
    ]
    # selling constraints
    constraints += [
        # sales cannot exceed grid demand
        x1 + x3 <= grid_demand,
        # sales cannot exceed battery capacity - soc
        x2 + x4 <= input.battery.capacity_kWh - battery_soc,
    ]
    # capacity constraints
    constraints += [
        # SoC cannot exceed battery capacity
        cp.max(battery_soc) <= input.battery.capacity_kWh,
    ]
    # throughput constraints
    constraints += [
        # cannot exceed inverter throughput
        x1 + x2 + x3 + x4 <= input.inverter.throughput_kWh,
        # cannot exceed battery throughput
        x2 + x3 + x4 <= input.battery.throughput_kWh,
        # cannot exceed grid throughput
        x1 + x3 + x4 <= input.grid.throughput_kWh,
    ]

    prob = cp.Problem(objective, constraints)
    opt = prob.solve()

    return PolicyOutput(
        value=opt,
        x1=x1.value,
        x2=x2.value,
        x3=x3.value,
        x4=x4.value,
    )
