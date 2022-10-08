# Problem definition

The problem has the markov property.

We will assume that solar panels, grid and batteries are all in the same region, e.g. DK1 or DK2.

## Variables

Time is discretised to buckets of 1 hour.

### Decision

|Variable|Description|
|-|-|
|x_solar(t) ∈ [0,1]|The amount of kWh to buy from solar at time *t* as a fraction of available supply|
|x_grid(t) ∈ [0,1]|The amount of kWh to buy from the grid at time *t* as a fraction of available supply|
|x_battery(t) ∈ [0,1]|The amount of kWh to buy from the battery at time *t* as a fraction of available supply|
|y_grid(t) ∈ [0,1]|The amount of kWh to sell to the grid at time *t* as a fraction of available demand|
|y_battery(t) ∈ [0,1]|The amount of kWh to sell to the battery at time *t* as a fraction of available demand|

### Buy

|Variable|Description|
|-|-|
|buy_solar(t)|The cost to buy 1 kWh from the solar panel, which depends on approximate depreciation of the panel per kWh produced|
|buy_grid(t)|The cost to buy 1 kWh from the grid, at time *t*, which equals the spot price in the region|
|buy_battery|The cost to buy 1 kWh from the battery, which equals the approximate depreciation of the battery per kWh stored|

### Sell

Not applicable to the solar panels, since you cannot sell kWh to them.

|Variable|Description|
|-|-|
|sell_grid(t) ∈ Z+|The revenue from selling 1 kWh to the grid, at time *t* in region *r*, which equals the spot price|
|sell_battery(t) = 0|The revenue from selling 1 kWh to the battery, which always equals zero|

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

- Selling can't exceed demand, for all resource types
- Buying can't exceed supply, for all resource types

## Problem

$$
\max \Sigma x
$$
