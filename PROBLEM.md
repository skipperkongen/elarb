# Problem definition

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
|x1(t) + x4(t) ≤ d_grid(t)|the amound to buy from the solar panel and the grid cannot exceed the demand of the battery|
|max (init_battery + Σ_t=0^i (x2(t)+x4(t)-x3(t)) ≤ C_battery, ∀ i ∈ [1, T]|Capacity constraint of battery. Compute the cumulative sum of input/output of battery (x2, x3, x4) up to t for all t, which must be below capacity for all t|
