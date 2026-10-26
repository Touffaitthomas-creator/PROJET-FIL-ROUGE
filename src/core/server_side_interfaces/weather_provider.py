from abc import ABC, abstractmethod

import pandas as pd

from src.core.models.pv_models import LocationConfig


class WeatherProvider(ABC):
    """
    Interface pour les fournisseurs de données météorologiques.
    """

    @abstractmethod
    def get_weather(
        self,
        location: LocationConfig,
    ) -> pd.DataFrame:
        """
        Retourne les données météorologiques nécessaires
        à la simulation photovoltaïque.
        """
        raise NotImplementedError