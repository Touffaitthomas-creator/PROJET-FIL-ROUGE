from dataclasses import dataclass


@dataclass(frozen=True)
class LocationConfig:
    """Localisation géographique de l'installation."""

    latitude: float
    longitude: float
    altitude: float
    timezone: str
    name: str = "PV site"


@dataclass(frozen=True)
class PVSystemConfig:
    """Configuration physique de l'installation photovoltaïque."""

    surface_m2: float

    tilt: float
    azimuth: float

    module_efficiency: float

    inverter_efficiency: float = 0.96

    temperature_coefficient: float = -0.004

    reference_temperature: float = 25.0