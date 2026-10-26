from src.client_side.visualization.pv_visualizer import (
    PVVisualizer,
)
from src.config.settings import settings
from src.core.domain.pv_system import PVSystem
from src.core.models.pv_models import (
    LocationConfig,
    PVSystemConfig,
)
from src.core.services.pv_simulation_service import (
    PVSimulationService,
)
from src.server_side.weather.pvlib_weather import (
    PVLibWeatherProvider,
)


def main() -> None:
    # ==========================================================
    # CONFIGURATION
    # ==========================================================

    location = LocationConfig(
        latitude=settings.pv_latitude,
        longitude=settings.pv_longitude,
        altitude=settings.pv_altitude,
        timezone=settings.pv_timezone,
        name=settings.pv_site_name,
    )

    pv_config = PVSystemConfig(
        surface_m2=settings.pv_surface_m2,
        tilt=settings.pv_tilt,
        azimuth=settings.pv_azimuth,
        module_efficiency=(
            settings.pv_module_efficiency
        ),
        inverter_efficiency=(
            settings.pv_inverter_efficiency
        ),
        temperature_coefficient=(
            settings.pv_temperature_coefficient
        ),
        reference_temperature=(
            settings.pv_reference_temperature
        ),
    )

    system = PVSystem(
        location=location,
        config=pv_config,
    )

    # ==========================================================
    # INFORMATIONS INSTALLATION
    # ==========================================================

    print()
    print("=" * 60)
    print("SIMULATION PHOTOVOLTAÏQUE")
    print("=" * 60)

    print(
        f"Site                   : "
        f"{location.name}"
    )

    print(
        f"Latitude               : "
        f"{location.latitude}"
    )

    print(
        f"Longitude              : "
        f"{location.longitude}"
    )

    print(
        f"Altitude               : "
        f"{location.altitude:.0f} m"
    )

    print(
        f"Fuseau horaire         : "
        f"{location.timezone}"
    )

    print(
        f"Surface PV             : "
        f"{pv_config.surface_m2:.1f} m²"
    )

    print(
        f"Inclinaison            : "
        f"{pv_config.tilt:.1f}°"
    )

    print(
        f"Azimut                 : "
        f"{pv_config.azimuth:.1f}°"
    )

    print(
        f"Rendement module       : "
        f"{pv_config.module_efficiency * 100:.1f} %"
    )

    print(
        f"Rendement onduleur     : "
        f"{pv_config.inverter_efficiency * 100:.1f} %"
    )

    print(
        f"Puissance crête        : "
        f"{system.peak_power_kw:.2f} kWc"
    )

    # ==========================================================
    # METEO PVGIS
    # ==========================================================

    print()
    print("-" * 60)
    print("RÉCUPÉRATION MÉTÉO PVGIS")
    print("-" * 60)

    weather_provider = (
        PVLibWeatherProvider()
    )

    weather = (
        weather_provider.get_weather(
            location=location,
        )
    )

    print(
        f"Nombre de points météo : "
        f"{len(weather)}"
    )

    available_columns = [
        column
        for column in [
            "ghi",
            "dni",
            "dhi",
            "temp_air",
            "wind_speed",
        ]
        if column in weather.columns
    ]

    print()
    print("Aperçu des données météo :")

    print(
        weather[
            available_columns
        ].head()
    )

    # ==========================================================
    # SIMULATION
    # ==========================================================

    print()
    print("-" * 60)
    print("SIMULATION DE LA PRODUCTION")
    print("-" * 60)

    simulator = (
        PVSimulationService()
    )

    result = simulator.simulate(
        system=system,
        weather=weather,
    )

    # ==========================================================
    # INDICATEURS
    # ==========================================================

    specific_yield = (
        result.energy_kwh
        / system.peak_power_kw
    )

    average_daily_energy = (
        result.energy_kwh
        / 365
    )

    theoretical_max_energy = (
        system.peak_power_kw
        * 8760
    )

    capacity_factor = (
        result.energy_kwh
        / theoretical_max_energy
        * 100
    )

    max_dc_kw = (
        result.dc_power_w.max()
        / 1000
    )

    max_ac_kw = (
        result.ac_power_w.max()
        / 1000
    )

    # ==========================================================
    # RESULTATS
    # ==========================================================

    print()
    print("=" * 60)
    print("RÉSULTATS")
    print("=" * 60)

    print(
        f"Production annuelle     : "
        f"{result.energy_kwh:,.0f} kWh"
    )

    print(
        f"Production spécifique   : "
        f"{specific_yield:,.0f} kWh/kWc"
    )

    print(
        f"Production moyenne/jour : "
        f"{average_daily_energy:.1f} kWh/j"
    )

    print(
        f"Facteur de capacité     : "
        f"{capacity_factor:.1f} %"
    )

    print(
        f"Puissance DC maximale   : "
        f"{max_dc_kw:.2f} kW"
    )

    print(
        f"Puissance AC maximale   : "
        f"{max_ac_kw:.2f} kW"
    )

    # ==========================================================
    # DATAVIZ
    # ==========================================================

    print()
    print("-" * 60)
    print("GÉNÉRATION DES GRAPHIQUES")
    print("-" * 60)

    PVVisualizer.save_all(
        result
    )

    # ==========================================================
    # FIN
    # ==========================================================

    print()
    print("=" * 60)
    print("SIMULATION TERMINÉE")
    print("=" * 60)

    print(
        "Les graphiques sont disponibles dans :"
    )

    print(
        "data/results/plots/"
    )


if __name__ == "__main__":
    main()