from dataclasses import dataclass

from src.core.models.pv_models import (
    LocationConfig,
    PVSystemConfig,
)


@dataclass
class PVSystem:
    location: LocationConfig
    config: PVSystemConfig

    @property
    def peak_power_kw(self) -> float:
        """
        Puissance crête approximative de l'installation.

        Hypothèse :
        irradiance STC = 1000 W/m².
        """

        power_w = (
            self.config.surface_m2
            * 1000
            * self.config.module_efficiency
        )

        return power_w / 1000