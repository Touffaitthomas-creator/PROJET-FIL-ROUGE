from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    """
    Configuration globale de l'application.

    Les valeurs sont chargées depuis les variables
    d'environnement et le fichier .env.
    """

    # --------------------------------------------------
    # Application
    # --------------------------------------------------

    app_name: str = Field(
        default="projet-pv",
        alias="APP_NAME",
    )

    app_env: str = Field(
        default="development",
        alias="APP_ENV",
    )

    debug: bool = Field(
        default=False,
        alias="DEBUG",
    )

    # --------------------------------------------------
    # Localisation
    # --------------------------------------------------

    pv_site_name: str = Field(
        alias="PV_SITE_NAME",
    )

    pv_latitude: float = Field(
        alias="PV_LATITUDE",
    )

    pv_longitude: float = Field(
        alias="PV_LONGITUDE",
    )

    pv_altitude: float = Field(
        default=0.0,
        alias="PV_ALTITUDE",
    )

    pv_timezone: str = Field(
        alias="PV_TIMEZONE",
    )

    # --------------------------------------------------
    # Photovoltaïque
    # --------------------------------------------------

    pv_surface_m2: float = Field(
        gt=0,
        alias="PV_SURFACE_M2",
    )

    pv_tilt: float = Field(
        ge=0,
        le=90,
        alias="PV_TILT",
    )

    pv_azimuth: float = Field(
        ge=0,
        le=360,
        alias="PV_AZIMUTH",
    )

    pv_module_efficiency: float = Field(
        gt=0,
        le=1,
        alias="PV_MODULE_EFFICIENCY",
    )

    pv_inverter_efficiency: float = Field(
        gt=0,
        le=1,
        alias="PV_INVERTER_EFFICIENCY",
    )

    pv_temperature_coefficient: float = Field(
        default=-0.004,
        alias="PV_TEMPERATURE_COEFFICIENT",
    )

    pv_reference_temperature: float = Field(
        default=25.0,
        alias="PV_REFERENCE_TEMPERATURE",
    )

    # --------------------------------------------------
    # Pydantic configuration
    # --------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> _Settings:
    """
    Retourne l'instance unique de configuration.
    """
    return _Settings()


settings = get_settings()