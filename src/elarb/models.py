from dataclasses import dataclass


@dataclass
class SolarPanel:
    m2: float = 0.75
    peak_kWh = 0.47
    depreciation_per_hour: float = 0.0059


@dataclass
class Battery:
    capacity_kWh: float = 8.8
    throughput_kWh: float = 3.3
    conversion_loss_pct: float = 0.03
    depreciation_per_kWh: float = 0.398


@dataclass
class GridConnection:
    throughput_kWh: float = 25.2


@dataclass
class Inverter:
    throughput_kWh: float = 15.6
    depreciation_per_hour: float = 0.0
    conversion_loss_pct: float = 0.03


@dataclass
class Facility:
    panel: SolarPanel
    battery: Battery
    inverter: Inverter
    grid: GridConnection
    n_panels: int = 1
    n_batteries: int = 1
    n_inverters: int = 1
