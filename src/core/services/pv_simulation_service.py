import pandas as pd
import pvlib

from src.core.domain.pv_system import PVSystem
from src.core.models.simulation_models import PVSimulationResult


class PVSimulationService:

    def simulate(
        self,
        system: PVSystem,
        weather: pd.DataFrame,
    ) -> PVSimulationResult:

        location = pvlib.location.Location(
            latitude=system.location.latitude,
            longitude=system.location.longitude,
            altitude=system.location.altitude,
            tz=system.location.timezone,
            name=system.location.name,
        )

        # Position du soleil
        solar_position = location.get_solarposition(
            weather.index
        )

        # Irradiance reçue par les panneaux
        poa = pvlib.irradiance.get_total_irradiance(
            surface_tilt=system.config.tilt,
            surface_azimuth=system.config.azimuth,
            solar_zenith=solar_position["apparent_zenith"],
            solar_azimuth=solar_position["azimuth"],
            dni=weather["dni"],
            ghi=weather["ghi"],
            dhi=weather["dhi"],
        )

        # Température cellule
        if "temp_air" in weather.columns:
            temp_air = weather["temp_air"]
        else:
            temp_air = pd.Series(
                20.0,
                index=weather.index,
            )

        if "wind_speed" in weather.columns:
            wind_speed = weather["wind_speed"]
        else:
            wind_speed = pd.Series(
                1.0,
                index=weather.index,
            )

        cell_temperature = pvlib.temperature.faiman(
            poa_global=poa["poa_global"],
            temp_air=temp_air,
            wind_speed=wind_speed,
        )

        # Puissance nominale
        nominal_power_w = (
            system.config.surface_m2
            * 1000
            * system.config.module_efficiency
        )

        # Modèle PV simplifié
        dc_power = (
            nominal_power_w
            * (poa["poa_global"] / 1000)
            * (
                1
                + system.config.temperature_coefficient
                * (
                    cell_temperature
                    - system.config.reference_temperature
                )
            )
        )

        # Pas de production négative
        dc_power = dc_power.clip(lower=0)

        # Conversion DC -> AC
        ac_power = (
            dc_power
            * system.config.inverter_efficiency
        )

        # Énergie produite
        timestep_hours = self._get_timestep_hours(
            weather.index
        )

        energy_kwh = (
            ac_power.sum()
            * timestep_hours
            / 1000
        )

        return PVSimulationResult(
            weather=weather,
            solar_position=solar_position,
            poa_irradiance=poa,
            dc_power_w=dc_power,
            ac_power_w=ac_power,
            energy_kwh=energy_kwh,
        )

    @staticmethod
    def _get_timestep_hours(
        index: pd.DatetimeIndex,
    ) -> float:

        if len(index) < 2:
            return 1.0

        delta = index[1] - index[0]

        return delta.total_seconds() / 3600