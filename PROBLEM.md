# Problem definition

There are three types of resources in the problem:
- Solar panels
- Battery
- Grid


We will assume that all resources are located all in the same grid region, e.g. DK1 or DK2.

The problem has the markov property in that the current state only depends on the previous state.

## Problem formulation

Consult the tables below for variable definitions.

$$
\begin{align*}
\max \Sigma_{t \in T} & \quad sell_{grid}(t) \cdot price_{grid}(t) \\
& \quad - buy_{solar}(t) \cdot price_{solar}(t) \\
& \quad - buy_{grid}(t) \cdot price_{grid}(t) \\
& \quad - buy_{battery}(t) \cdot price_{battery}(t)) \\
\text{s.t.} &  \\
& TODO \\
\end{align*}
$$

Notes:
- You pay a price only when you buy kWh from the battery, not when you sell kWh to it


## Variables

Time is discretised to buckets of 1 hour.

### Decision

|Variable|Description|
|-|-|
|sell_grid(t) ∈ Z+|The amount of kWh to sell to the grid at time *t* as a fraction of available demand|
|sell_battery(t) ∈ Z+|The amount of kWh to sell to the battery at time *t* as a fraction of available demand; does not pay anything|
|buy_solar(t) ∈ Z+|The amount of kWh to buy from solar at time *t*|
|buy_grid(t) ∈ Z+|The amount of kWh to buy from the grid at time *t*|
|buy_battery(t) ∈ Z+]|The amount of kWh to buy from the battery at time *t* as a fraction of available supply|

### Prices

We assume that the price is the same regardless of whether you buy or sell. This can easily be generalised to different prices for buying and selling.

|Variable|Description|
|-|-|
|price_solar(t)|The price of buying 1 kWh from the solar panel, which depends on approximate depreciation of the panel per kWh produced|
|price_grid(t)|The price of buying/selling 1 kWh from/to the grid, at time *t*, which equals the spot price in the region|
|price_battery(t)|The price to buy/sell 1 kWh from the battery, which equals the approximate depreciation of the battery per kWh stored|

### Revenue

Only applicable to the grid. Since you cannot sell kWh to the solar panels and the battery does not pay anything.

|Variable|Description|
|-|-|
|revenue_grid(t) ∈ Z+|The revenue from selling 1 kWh to the grid, at time *t* in the given region, which equals the spot price|

### Supply

|Variable|Description|
|-|-|
|supply_solar(t) ∈ Z+|The amount of kWh available to purchase/produce from the solar panel at time *t*, which e.g. depends on how much the sun shines at time *t*|
|supply_grid(t) ∈ Z+|The amount of kWh available to purchase from the grid at time *t* in the given region|
|supply_battery(t) ∈ Z+ |The amount of kWh available to purchase/discharge from the battery at time t, which depends, e.g., on the charge and conversion loss of the battery at time *t*|

### Demand

|Variable|Description|
|-|-|
|demand_grid(t) ∈ Z+|The amount of kWh that can be sold to the grid at time *t*|
|demand_battery(t) ∈ Z+|The amount of kWh that can be sold to the battery at time t, which depends, e.g., on the charge, capacity and conversion loss of the battery at time *t*|

## Constraints

For all resource types:
- Sales cannot exceed demand
- Sales cannot exceed amount purchached from other resources
- Purchases cannot exceed supply
