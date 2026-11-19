import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

from scr.utils.csv_handler import CSVHandler


class OutputUtils:
    def __init__(
            self
    ) -> None:
        pass

    def output(
            self,
            graph_type: str,
    ) -> None:
        if graph_type == "surface":
            self._output_vol_surface_graph()
        elif graph_type == "smile":
            self._output_vol_smile_graph()
        else:
            raise NotImplementedError

    def _output_vol_smile_graph(self) -> None:
        df = pd.DataFrame()
        csv = CSVHandler()
        data_df = csv.read_model_output_data()

        df["estimated_iv"] = data_df["estimated_iv"]
        df["moneyness"] = data_df["moneyness"]

        sns.set_theme(
            style="whitegrid",
            context="paper",
            font="Arial"
        )

        fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)

        sns.lineplot(
            data=df,
            x="moneyness",
            y="estimated_iv",
            color="#1F4E79",
            linewidth=2.5,
            ax=ax
        )

        ax.set_title(
            "Implied Volatility Smile",
            fontsize=16,
            fontweight="bold",
            pad=18
        )

        ax.set_xlabel("Moneyness", fontsize=12, labelpad=10)
        ax.set_ylabel("Implied Volatility (%)", fontsize=12, labelpad=10)

        ax.legend(
            frameon=False,
            fontsize=10,
            loc="upper center"
        )

        ax.grid(
            axis="y",
            linestyle="--",
            linewidth=0.6,
            alpha=0.5
        )

        ax.grid(axis="x", visible=False)

        plt.tight_layout()

        plt.savefig("C:/repos/personal/python_projects/option_vol_surface/data/outputs/smile")

    def _output_vol_surface_graph(self) -> None:
        csv = CSVHandler()
        data_df = csv.read_model_output_data()

        surface_data = data_df.pivot(
            index='dte',
            columns='moneyness',
            values='estimated_iv'
        )

        # Extract X, Y and Z coordinates
        X, Y = np.meshgrid(
            surface_data.columns.values,
            surface_data.index.values
        )

        Z = surface_data.values

        sns.set_theme(
            style="whitegrid",
            context="notebook",
            palette="viridis",
            font_scale=1.1
        )

        fig = plt.figure(figsize=(12, 9), dpi=150)
        ax = fig.add_subplot(111, projection='3d')

        surface = ax.plot_surface(
            X,
            Y,
            Z,
            cmap='viridis',
            edgecolor='none',
            linewidth=0,
            antialiased=True,
            alpha=0.95,
            rstride=1,
            cstride=1
        )

        ax.set_title(
            'Implied Volatility Surface',
            fontsize=18,
            fontweight='bold',
            pad=25
        )

        ax.set_xlabel(
            'Moneyness (K/F)',
            fontsize=13,
            labelpad=12
        )

        ax.set_ylabel(
            'Time to Maturity (Years)',
            fontsize=13,
            labelpad=12
        )

        ax.set_zlabel(
            'Implied Volatility',
            fontsize=13,
            labelpad=12
        )

        cbar = fig.colorbar(
            surface,
            ax=ax,
            shrink=0.65,
            aspect=15,
            pad=0.12
        )

        cbar.set_label(
            'Implied Volatility',
            fontsize=12,
            labelpad=10
        )

        ax.view_init(
            elev=30,
            azim=-135
        )

        ax.set_box_aspect((1.5, 1, 0.8))

        ax.tick_params(
            axis='both',
            which='major',
            labelsize=10
        )

        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("C:/repos/personal/python_projects/option_vol_surface/data/outputs/surface")
