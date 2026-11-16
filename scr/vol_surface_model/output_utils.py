import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

from scr.utils.csv_handler import CSVHandler


class OutputUtils:
    def __init__(self) -> None:
        pass

    def output_vol_surface_graph(self):
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
        plt.savefig("C:/repos/personal/python_projects/option_vol_surface/data/outputs/vol_surface.pdf")


