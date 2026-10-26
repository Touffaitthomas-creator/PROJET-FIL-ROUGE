import pandas as pd
import pvlib

from src.core.models.pv_models import LocationConfig
from src.core.server_side_interfaces.weather_provider import WeatherProvider


class PVLibWeatherProvider(WeatherProvider):
    """
    Fournisseur de données météorologiques basé sur PVGIS.

    Les données récupérées correspondent à une année
    météorologique typique (TMY - Typical Meteorological Year).
    """

    def get_weather(
        self,
        location: LocationConfig,
    ) -> pd.DataFrame:
        """
        Récupère les données météorologiques TMY depuis PVGIS.
        """

        # --------------------------------------------------
        # Récupération des données PVGIS
        # --------------------------------------------------

        result = pvlib.iotools.get_pvgis_tmy(
            latitude=location.latitude,
            longitude=location.longitude,
            outputformat="json",
            usehorizon=True,
            map_variables=True,
        )

        # Les versions récentes de pvlib renvoient :
        # (data, metadata)
        weather = result[0]

        if not isinstance(weather, pd.DataFrame):
            raise TypeError(
                "PVGIS n'a pas retourné un DataFrame météo."
            )

        weather = weather.copy()

        # --------------------------------------------------
        # Vérification des colonnes indispensables
        # --------------------------------------------------

        required_columns = {
            "ghi",
            "dni",
            "dhi",
        }

        missing_columns = required_columns.difference(
            weather.columns
        )

        if missing_columns:
            raise ValueError(
                "Les données PVGIS ne contiennent pas toutes "
                "les colonnes nécessaires. "
                f"Colonnes manquantes : {sorted(missing_columns)}. "
                f"Colonnes disponibles : {list(weather.columns)}"
            )

        # --------------------------------------------------
        # Vérification / conversion de l'index temporel
        # --------------------------------------------------

        if not isinstance(weather.index, pd.DatetimeIndex):
            weather.index = pd.to_datetime(
                weather.index,
                utc=True,
            )

        # --------------------------------------------------
        # Fuseau horaire
        # --------------------------------------------------

        if weather.index.tz is None:
            weather.index = weather.index.tz_localize("UTC")

        weather.index = weather.index.tz_convert(
            location.timezone
        )

        # --------------------------------------------------
        # Nettoyage
        # --------------------------------------------------

        weather = weather.sort_index()

        # Une irradiance physique ne peut pas être négative.
        for column in ("ghi", "dni", "dhi"):
            weather[column] = (
                weather[column]
                .fillna(0.0)
                .clip(lower=0.0)
            )

        # --------------------------------------------------
        # Température
        # --------------------------------------------------

        if "temp_air" not in weather.columns:
            weather["temp_air"] = 20.0

        weather["temp_air"] = (
            weather["temp_air"]
            .interpolate()
            .ffill()
            .bfill()
        )

        # --------------------------------------------------
        # Vent
        # --------------------------------------------------

        if "wind_speed" not in weather.columns:
            weather["wind_speed"] = 1.0

        weather["wind_speed"] = (
            weather["wind_speed"]
            .fillna(1.0)
            .clip(lower=0.0)
        )

        return weather