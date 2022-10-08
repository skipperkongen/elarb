# Problem definition

> TODO: add battery capacity constraint

There are three types of resources in the problem:
- Solar panels
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

## Problem formulation

Problem formulation:

$$
\begin{align*}
\max \Sigma_{t \in T} & \quad x1(t) \cdot p_{grid}(t) \\
& \quad + x3(t) \cdot p_{grid}(t) \\
& \quad - x1(t) \cdot p_{solar}(t) \\
& \quad - x2(t) \cdot p_{solar}(t) \\
& \quad - x3(t) \cdot p_{battery}(t) \\
& \quad - x4(t) \cdot p_{grid}(t) \\
\text{s.t.} &  \\
& \quad x1(t) + x3(t) \leq d_{grid}(t) \\
& \quad x2(t) + x4(t) \leq d_{battery}(t) \\
& \quad x1(t) + x2(t) \leq s_solar(t) \\
& \quad x3(t) \leq s_{battery}(t) \\
& \quad x4(t) \leq s_grid(t) \\
& \quad x1(t) + x4(t) \leq d_{grid}(t) \\
& x1(t) \in \mathbb{Z}^+, x2(t) \in \mathbb{Z}^+, x3(t) \in \mathbb{Z}^+, x4(t) \in \mathbb{Z}^+, \quad \forall t \\
\end{align*}
$$

Notes:
- Time *t* is discretised into buckets of one hour and capital *T* denotes the last time bucket
- Consult the tables below for all variable and constraint descriptions

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
|f_battery ∈ [0,1]|The state of charge (SoC) of the battery in percent|
|C_battery|The capacity of the battery in kWh|

## Constraints

|Expression|Description|
|-|-|
|x1(t) + x3(t) <= d_grid(t)|the amount to sell to the grid cannot exceed the demand of the grid (theoretical)|
|x2(t) + x4(t) <= d_battery(t)|the amount to sell to the battery cannot exceed the demand (i.e. capability to charge) of the battery|
|x1(t) + x2(t) = s_solar(t)|The amount sold to the grid plus the battery cannot exceed the kWh produced by solar panels|
|x3(t) <= s_battery(t)|the amound to buy from battery cannot exceed the supply of the battery|
|x4(t) <= s_grid(t)|the amound to buy from grid cannot exceed the supply of the grid|
|x1(t) + x4(t) <= d_grid(t)|the amound to buy from the solar panel and the grid cannot exceed the demand of the battery|
