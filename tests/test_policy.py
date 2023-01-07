#!/usr/bin/env python

"""Tests for `elarb` package."""

import pytest
import numpy as np

from elarb.policy import (
    optimal_policy,
    PolicyInput,
)
from elarb.models import (
    SolarPanel,
    Battery,
    GridConnection,
    Inverter,
    Facility,
)


@pytest.fixture
def fortytwo():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return 42


def test_arbitrage_only():
    """Sample pytest test function with the pytest fixture as an argument."""

    facility = Facility(
        panel=SolarPanel(),
        battery=Battery(throughput_kWh=1, capacity_kWh=1),
        inverter=Inverter(throughput_kWh=1),
        grid=GridConnection(throughput_kWh=1),
        n_panels=0,
        n_batteries=1,
        n_inverters=1,
    )

    policy_input = PolicyInput(
        facility=facility,
        net_tariff=0.0,
        spot_price=np.array([0, 1]),
        pv_dc_kWh_m2=np.zeros(2),
        spot_demand_kWh=np.ones(2),
        spot_supply_kWh=np.ones(2),
        initial_soc=0.0
    )

    res = optimal_policy(policy_input)
    assert (res.x1.round(2) == np.zeros(2)).all()  # no solar
    assert (res.x2.round(2) == np.zeros(2)).all()  # no solar
    assert (res.x3.round(2) == np.array([0, 0.97])).all()  # sell later
    assert (res.x4.round(2) == np.array([1, 0])).all()  # buy first
