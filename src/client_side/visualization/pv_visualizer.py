from pathlib import Path

import matplotlib

# ==========================================================
# BACKEND MATPLOTLIB
# ==========================================================
#
# "Agg" permet de générer des images sans interface graphique.
# On évite ainsi la dépendance à Tkinter / Tcl.
#
# IMPORTANT :
# matplotlib.use() doit être appelé AVANT l'import de pyplot.
# ==========================================================

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from src.core.models.simulation_models import PVSimulationResult


class PVVisualizer:
    """
    Génère les graphiques associés à une simulation
    photovoltaïque.

    Les graphiques sont enregistrés dans :

        data/results/plots/
    """

    OUTPUT_DIR = Path("data/results/plots")

    MONTH_NAMES = [
        "Jan",
        "Fév",
        "Mar",
        "Avr",
        "Mai",
        "Juin",
        "Juil",
        "Août",
        "Sep",
        "Oct",
        "Nov",
        "Déc",
    ]

    # ==========================================================
    # OUTILS
    # ==========================================================

    @classmethod
    def _save_figure(
        cls,
        fig,
        filename: str,
    ) -> None:
        """
        Enregistre une figure dans le dossier de résultats.
        """

        cls.OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            cls.OUTPUT_DIR / filename
        )

        fig.savefig(
            output_path,
            dpi=150,
            bbox_inches="tight",
        )

        plt.close(fig)

        print(
            f"Graphique sauvegardé : {output_path}"
        )

    @staticmethod
    def _get_timestep_hours(
        index: pd.DatetimeIndex,
    ) -> float:
        """
        Détermine le pas de temps de la série en heures.
        """

        if len(index) < 2:
            raise ValueError(
                "Au moins deux points temporels "
                "sont nécessaires."
            )

        delta = (
            index[1] - index[0]
        )

        timestep_hours = (
            delta.total_seconds()
            / 3600
        )

        if timestep_hours <= 0:
            raise ValueError(
                "Le pas de temps doit être positif."
            )

        return timestep_hours

    @staticmethod
    def _power_to_energy(
        power_w: pd.Series,
    ) -> pd.Series:
        """
        Convertit une série de puissance en W
        en énergie par pas de temps en kWh.
        """

        timestep_hours = (
            PVVisualizer._get_timestep_hours(
                power_w.index
            )
        )

        energy_kwh = (
            power_w
            * timestep_hours
            / 1000
        )

        return energy_kwh

    # ==========================================================
    # PRODUCTION MENSUELLE
    # ==========================================================

    @classmethod
    def plot_monthly_energy(
        cls,
        result: PVSimulationResult,
    ) -> None:
        """
        Génère la production photovoltaïque
        mensuelle en kWh.
        """

        energy = cls._power_to_energy(
            result.ac_power_w
        )

        monthly = energy.groupby(
            energy.index.month
        ).sum()

        monthly = monthly.reindex(
            range(1, 13),
            fill_value=0.0,
        )

        fig, ax = plt.subplots(
            figsize=(12, 6)
        )

        bars = ax.bar(
            cls.MONTH_NAMES,
            monthly.values,
        )

        ax.set_title(
            "Production photovoltaïque mensuelle"
        )

        ax.set_xlabel(
            "Mois"
        )

        ax.set_ylabel(
            "Production (kWh)"
        )

        ax.grid(
            axis="y",
            alpha=0.3,
        )

        # Valeur au-dessus de chaque barre
        for bar, value in zip(
            bars,
            monthly.values,
        ):
            ax.text(
                bar.get_x()
                + bar.get_width() / 2,
                bar.get_height(),
                f"{value:.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        fig.tight_layout()

        cls._save_figure(
            fig,
            "production_mensuelle.png",
        )

    # ==========================================================
    # PROFIL JOURNALIER MOYEN
    # ==========================================================

    @classmethod
    def plot_average_daily_profile(
        cls,
        result: PVSimulationResult,
    ) -> None:
        """
        Génère le profil journalier moyen
        de production AC.
        """

        power_kw = (
            result.ac_power_w
            / 1000
        )

        hourly = power_kw.groupby(
            power_kw.index.hour
        ).mean()

        hourly = hourly.reindex(
            range(24),
            fill_value=0.0,
        )

        fig, ax = plt.subplots(
            figsize=(12, 6)
        )

        ax.plot(
            hourly.index,
            hourly.values,
            marker="o",
            label="Puissance AC moyenne",
        )

        ax.set_title(
            "Profil journalier moyen de production PV"
        )

        ax.set_xlabel(
            "Heure de la journée"
        )

        ax.set_ylabel(
            "Puissance moyenne (kW)"
        )

        ax.set_xticks(
            range(0, 24, 2)
        )

        ax.grid(
            alpha=0.3
        )

        ax.legend()

        fig.tight_layout()

        cls._save_figure(
            fig,
            "profil_journalier.png",
        )

    # ==========================================================
    # PUISSANCE DC VS AC
    # ==========================================================

    @classmethod
    def plot_dc_vs_ac(
        cls,
        result: PVSimulationResult,
    ) -> None:
        """
        Compare les puissances DC et AC
        sur une journée moyenne.
        """

        dc_kw = (
            result.dc_power_w
            / 1000
        )

        ac_kw = (
            result.ac_power_w
            / 1000
        )

        dc_hourly = dc_kw.groupby(
            dc_kw.index.hour
        ).mean()

        ac_hourly = ac_kw.groupby(
            ac_kw.index.hour
        ).mean()

        dc_hourly = dc_hourly.reindex(
            range(24),
            fill_value=0.0,
        )

        ac_hourly = ac_hourly.reindex(
            range(24),
            fill_value=0.0,
        )

        fig, ax = plt.subplots(
            figsize=(12, 6)
        )

        ax.plot(
            dc_hourly.index,
            dc_hourly.values,
            marker="o",
            label="Puissance DC",
        )

        ax.plot(
            ac_hourly.index,
            ac_hourly.values,
            marker="o",
            label="Puissance AC",
        )

        ax.set_title(
            "Comparaison puissance DC / AC"
        )

        ax.set_xlabel(
            "Heure de la journée"
        )

        ax.set_ylabel(
            "Puissance moyenne (kW)"
        )

        ax.set_xticks(
            range(0, 24, 2)
        )

        ax.grid(
            alpha=0.3
        )

        ax.legend()

        fig.tight_layout()

        cls._save_figure(
            fig,
            "dc_vs_ac.png",
        )

    # ==========================================================
    # IRRADIANCE MENSUELLE
    # ==========================================================

    @classmethod
    def plot_irradiance(
        cls,
        result: PVSimulationResult,
    ) -> None:
        """
        Génère l'irradiance moyenne reçue
        par les panneaux selon le mois.
        """

        poa_global = (
            result.poa_irradiance[
                "poa_global"
            ]
        )

        monthly = poa_global.groupby(
            poa_global.index.month
        ).mean()

        monthly = monthly.reindex(
            range(1, 13),
            fill_value=0.0,
        )

        fig, ax = plt.subplots(
            figsize=(12, 6)
        )

        bars = ax.bar(
            cls.MONTH_NAMES,
            monthly.values,
        )

        ax.set_title(
            "Irradiance moyenne reçue par les panneaux"
        )

        ax.set_xlabel(
            "Mois"
        )

        ax.set_ylabel(
            "Irradiance moyenne (W/m²)"
        )

        ax.grid(
            axis="y",
            alpha=0.3,
        )

        for bar, value in zip(
            bars,
            monthly.values,
        ):
            ax.text(
                bar.get_x()
                + bar.get_width() / 2,
                bar.get_height(),
                f"{value:.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        fig.tight_layout()

        cls._save_figure(
            fig,
            "irradiance_mensuelle.png",
        )

    # ==========================================================
    # HEATMAP MOIS / HEURE
    # ==========================================================

    @classmethod
    def plot_month_hour_heatmap(
        cls,
        result: PVSimulationResult,
    ) -> None:
        """
        Génère une heatmap représentant la puissance
        photovoltaïque AC moyenne selon le mois
        et l'heure.
        """

        data = pd.DataFrame(
            {
                "power_kw":
                    result.ac_power_w
                    / 1000
            }
        )

        data["month"] = (
            data.index.month
        )

        data["hour"] = (
            data.index.hour
        )

        matrix = data.pivot_table(
            values="power_kw",
            index="hour",
            columns="month",
            aggfunc="mean",
        )

        matrix = matrix.reindex(
            index=range(24),
            columns=range(1, 13),
            fill_value=0.0,
        )

        fig, ax = plt.subplots(
            figsize=(12, 7)
        )

        image = ax.imshow(
            matrix.values,
            aspect="auto",
            origin="lower",
        )

        ax.set_title(
            "Production PV moyenne selon le mois et l'heure"
        )

        ax.set_xlabel(
            "Mois"
        )

        ax.set_ylabel(
            "Heure"
        )

        ax.set_xticks(
            range(12)
        )

        ax.set_xticklabels(
            cls.MONTH_NAMES
        )

        ax.set_yticks(
            range(0, 24, 2)
        )

        ax.set_yticklabels(
            range(0, 24, 2)
        )

        colorbar = fig.colorbar(
            image,
            ax=ax,
        )

        colorbar.set_label(
            "Puissance AC moyenne (kW)"
        )

        fig.tight_layout()

        cls._save_figure(
            fig,
            "heatmap_production.png",
        )

    # ==========================================================
    # GENERATION DE TOUS LES GRAPHIQUES
    # ==========================================================

    @classmethod
    def save_all(
        cls,
        result: PVSimulationResult,
    ) -> None:
        """
        Génère et sauvegarde tous les graphiques
        principaux de la simulation.
        """

        print()
        print(
            "Génération de la production mensuelle..."
        )

        cls.plot_monthly_energy(
            result
        )

        print(
            "Génération du profil journalier..."
        )

        cls.plot_average_daily_profile(
            result
        )

        print(
            "Génération de la comparaison DC / AC..."
        )

        cls.plot_dc_vs_ac(
            result
        )

        print(
            "Génération de l'irradiance mensuelle..."
        )

        cls.plot_irradiance(
            result
        )

        print(
            "Génération de la heatmap..."
        )

        cls.plot_month_hour_heatmap(
            result
        )