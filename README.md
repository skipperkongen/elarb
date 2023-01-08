# El Arb

Profit-maximising control of inverteres in a PV + inverter + battery setup.

```
           ┌───────┐       
    ┌─x1──▶│ Grid  │──┐    
    │      └───────┘  │    
┌───────┐      ▲      │    
│ Solar │      │x3    │x4    
└───────┘      │      │    
    │      ┌───────┐  │    
    └─x2──▶│Battery│◀─┘    
           └───────┘       
```

## Installation

Install using pip:

```shell
pip install elarb
```

## Local development

```
make venv
source venv/bin/activate
make install_dev
make test
```

## Example

Below is an example of using the optimiser over 24 hours starting with an empty battery. 
The scenario roughly corresponds to a small facility in Denmark for 36 hours in July.
Since the optimiser requires a lot of parameters, e.g. for PV production, battery characteristics etc.,
the example is necessarily quite verbose.

```python
import numpy as np

from elarb.policy import optimal_policy, PolicyInput
from elarb.models import SolarPanel, Battery, GridConnection, Inverter, Facility

# solar panels: 470Wp JinKO TigerNeo N-Type 60HL4 BF, 1.57 kWh / time, costs 1565 DKK
panel = SolarPanel(m2=0.75, depreciation_per_hour=0.006)
# Deye SUN-12K-SG04LP3-EU
inverter = Inverter(depreciation_per_hour=0.05, throughput_kWh=15.6, conversion_loss_pct=0.03)
# battery: Powerwall LBATTS Powerwall, 8.8 kwh
# bat_cost_dkk = 21000; bat_cycles = 6000; bat_depreciation = np.round(bat_cost_dkk / (8.8*bat_cycles), 3)
battery = Battery(depreciation_per_kWh=0.3, throughput_kWh=3.3, capacity_kWh=8.8, conversion_loss_pct=0.03)
# DK grid, udvidet stikledning
amp = 63
volt = 400
grid = GridConnection(throughput_kWh=amp * volt / 1000)

# Connect components in a facility
facility=Facility(
    panel=panel,
    battery=battery,
    inverter=inverter,
    grid=grid,
    n_panels=12,
    n_batteries=1,
    n_inverters=1,
)


spot_price = np.array([
    2.94, 2.73, 2.72, 3.01, 3.03, 3.44, 3.65, 3.82, 3.75, 3.61, 3.43,
    3.16, 3.16, 1.47, 1.47, 1.47, 1.47, 1.47, 3.03, 3.15, 3.07, 2.89,
    2.5 , 2.3 , 2.  , 1.76, 1.84, 2.17, 2.36, 2.89, 3.17, 3.38, 3.48,
    3.47, 3.47, 3.29])

pv_kwh = np.array([
    0.32, 0.27, 0.2 , 0.13, 0.09, 0.06, 0.02, 0.  , 0.  , 0.  , 0.  ,
    0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.02, 0.07, 0.16, 0.3 , 0.47,
    0.48, 0.46, 0.33, 0.34, 0.28, 0.23, 0.16, 0.1 , 0.04, 0.01, 0.  ,
    0.  , 0.  , 0.  ])
# https://radiuselnet.dk/elnetkunder/tariffer-og-netabonnement/
net_tariff = np.array([
    0.25, 0.25, 0.25, 0.25, 0.25, 0.66, 0.66, 0.66, 
    0.66, 0.25, 0.25, 0.25, 0.17, 0.17, 0.17, 0.17, 
    0.17, 0.17, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 
    0.25, 0.25, 0.25, 0.25, 0.25, 0.66, 0.66, 0.66, 
    0.66, 0.25, 0.25, 0.25, ])
spot_demand_kWh = np.zeros(36) + 9999
spot_supply_kWh = np.zeros(36) + 9999

policy_input = PolicyInput(
    facility=facility,
    spot_price=spot_price,
    pv_dc_kWh_m2=pv_kwh,
    net_tariff=net_tariff,
    spot_demand_kWh=spot_demand_kWh,
    spot_supply_kWh=spot_supply_kWh,
    initial_soc=0.0
)

res = optimal_policy(policy_input)

print()
print('Result')
print('- Profit:', np.round(res.value, 3))
print('- PV contribution:', np.round(res.x1_contrib, 3))
print('- X2 contribution:', np.round(res.x2_contrib, 3))
print('- X3 contribution:', np.round(res.x3_contrib, 3))
print('- X4 contribution:', np.round(res.x4_contrib, 3))
print('- Panel deprecation:', np.round(res.panel_depreciation, 3))
print('- Inverter deprecation:', np.round(res.inverter_depreciation, 3))
print('- Battery deprecation:', np.round(res.battery_depreciation, 3))
print('- Battery soc:', res.battery_soc_kWh.round(3))

"""
Result
- Profit: 108.738
- PV contribution: 56.369
- X2 contribution: 0.0
- X3 contribution: 79.023
- X4 contribution: -14.574
- Panel deprecation: 2.592
- Inverter deprecation: 1.8
- Battery deprecation: 7.688
- Battery soc: [0.    2.794 5.151 6.897 8.032 8.032 8.032 8.032 6.6   6.6   3.3   0.
 0.    0.    2.081 4.035 6.198 8.62  8.795 6.6   3.3   0.    0.    0.
 0.    2.881 5.849 8.294 8.785 8.8   8.8   8.8   8.8   8.8   5.5   2.2  ]
"""
```

## Theory

There are four types of resources in the problem:
- Solar panels
- Inverter
- Battery
- Grid

We will assume that all resources are located all in the same grid region, e.g. DK1 or DK2.

The problem has the markov property in that the current state only depends on the previous state.

Graph of who can send kWh to who:

```
           ┌───────┐       
    ┌─x1──▶│ Grid  │──┐    
    │      └───────┘  │    
┌───────┐      ▲      │    
│ Solar │      │x3    │x4    
└───────┘      │      │    
    │      ┌───────┐  │    
    └─x2──▶│Battery│◀─┘    
           └───────┘       
```

### Problem formulation

> think about how/if to include conversion loss in formula. Can it be modelled as a "tax" on x3?

Problem formulation:

$$
\begin{align*}
\underset{x}{\mathrm{argmax}} \quad \Sigma_{t \in T}
& \quad x1(t) \cdot p_{grid}(t) - x1(t) \cdot p_{solar}(t) \\
& + \quad x2(t) \cdot p_{battery}(t) - x2(t) \cdot p_{solar}(t) \\
& + \quad x3(t) \cdot p_{grid}(t) - x3(t) \cdot p_{battery}(t) \\
& + \quad x4(t) \cdot p_{battery}(t) - x4(t) \cdot p_{grid}(t) \\
\text{s.t.} &  \\
& \quad x1(t) + x3(t) \leq d_{grid}(t) \\
& \quad x2(t) + x4(t) \leq d_{battery}(t) \\
& \quad x1(t) + x2(t) \leq s_{solar}(t) \\
& \quad x3(t) \leq s_{battery}(t) \\
& \quad x4(t) \leq s_{grid}(t) \\
& \quad x1(t) + x4(t) \leq d_{grid}(t) \\
& \quad max \lbrace init_{battery} + \Sigma_{t=0}^{i} x2(t)+x4(t)-x3(t) \rbrace \leq C_{battery}, \forall i \in \lbrack 1, T \rbrack \\
& x1(t) \in \mathbb{Z}^+, x2(t) \in \mathbb{Z}^+, x3(t) \in \mathbb{Z}^+, x4(t) \in \mathbb{Z}^+, \quad \forall t \\
\end{align*}
$$

Tips:
- We can use cvxpy's [cumsum](https://www.cvxpy.org/api_reference/cvxpy.atoms.affine.html#cumsum) along with [max](https://www.cvxpy.org/api_reference/cvxpy.atoms.other_atoms.html#max) for capacity constraint! The sum over time (x2+x4-x3).

Notes:
- We can assume that $d_{grid} = \infty, \forall t$, but the constraint is included anyway
- Instead of $d_{battery}(t)$ we should model that the net amount sold to battery in previous time (i.e. all t' < t) plus the initial charge cannot exceed the capacity, for all t.
- Time *t* is discretised into buckets of one hour and capital *T* denotes the last time bucket
- Consult the tables below for all variable and constraint descriptions
- Maybe we need a higher $p_{battery}$ when SoC < 10%, because higher depreciation
- Maybe we need an initial SoC for the battery, in order to model the capacity constraint correctly

## Variables


### Decision

|Variable|Description|
|-|-|
|x1(t) ∈ Z+|kWh to buy from of solar and sell to grid at time *t*|
|x2(t) ∈ Z+|kWh to buy from solar and sell to battery at time *t*|
|x3(t) ∈ Z+|kWh to buy from battery and sell to grid at time *t*|
|x4(t) ∈ Z+|kWh to buy from grid and sell to battery at time *t*|

### Prices

We assume that the price is the same regardless of whether you buy or sell. This can easily be generalised to different prices for buying and selling.

|Variable|Description|
|-|-|
|p_solar(t) ∈ Z+|The price of buying 1 kWh from the solar panel at time *t*, which depends on the depreciation of the panel per kWh produced|
|p_grid(t) ∈ Z+|The price to buy/sell 1 kWh from/to the grid, at time *t*, which equals the spot price in the region|
|p_battery(t) ∈ Z+|The price to buy/sell 1 kWh from the battery, which equals the approximate depreciation of the battery per kWh stored|

### Supply

|Variable|Description|
|-|-|
|s_solar(t) ∈ Z+|The amount of kWh produced by the solar panel at time *t*, which depends, e.g., on how much the sun shines at time *t*|
|s_grid(t) ∈ Z+|The amount of kWh available to buy from the grid at time *t* in the given region|
|s_battery(t) ∈ Z+ |The amount of kWh available to buy from the battery at time *t*, which depends on the current SoC, the discharge speed and the conversion loss|

### Demand

|Variable|Description|
|-|-|
|d_grid(t) ∈ Z+|The amount of kWh that can be sold to the grid at time *t*|
|d_battery(t) ∈ Z+|The amount of kWh that can be sold to the battery at time *t*, which depends on the current SoC, the charge speed and the conversion loss|

### Capacity

|Variable|Description|
|-|-|
|init_battery ∈ Z+|The initial state of charge (SoC) of the battery in kWh|
|C_battery|The capacity of the battery in kWh|

## Constraints

|Expression|Description|
|-|-|
|x1(t) + x3(t) ≤ d_grid(t)|the amount to sell to the grid cannot exceed the demand of the grid (theoretical)|
|x2(t) + x4(t) ≤ d_battery(t)|the amount to sell to the battery cannot exceed the demand (i.e. capability to charge) of the battery|
|x1(t) + x2(t) ≤ s_solar(t)|The amount sold to the grid plus the battery cannot exceed the kWh produced by solar panels|
|x3(t) ≤ s_battery(t)|the amound to buy from battery cannot exceed the supply of the battery|
|x4(t) ≤ s_grid(t)|the amound to buy from grid cannot exceed the supply of the grid|
|x1(t) + x4(t) ≤ d_grid(t) (???)|Note: mistake here? The amound to buy from the solar panel and the grid cannot exceed the demand of the battery|
|max (init_battery + Σ_t=0^i (x2(t)+x4(t)-x3(t)) ≤ C_battery, ∀ i ∈ [1, T]|Capacity constraint of battery. Compute the cumulative sum of input/output of battery (x2, x3, x4) up to t for all t, which must be below capacity for all t|
