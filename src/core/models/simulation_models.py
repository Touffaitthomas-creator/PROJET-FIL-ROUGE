from dataclasses import dataclass

import pandas as pd


@dataclass
class PVSimulationResult:
    """
    Résultat complet d'une simulation photovoltaïque.
    """

    weather: pd.DataFrame

    solar_position: pd.DataFrame

    poa_irradiance: pd.DataFrame

    dc_power_w: pd.Series

    ac_power_w: pd.Series

    energy_kwh: float