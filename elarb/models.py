from dataclasses import dataclass

import numpy as np


@dataclass
class SolarPanel:
    m2: float = 1.0
    depreciation_per_hour: float = 0.0


@dataclass
class Battery:
    capacity_kWh: float
    throughput_kWh: float
    conversion_loss_pct: float = 0.0
    depreciation_per_kWh: float = 0.0


@dataclass
class GridConnection:
    throughput_kWh: float


@dataclass
class Inverter:
    throughput_kWh: float
    depreciation_per_hour: float = 0.0
    conversion_loss_pct: float = 0.0
