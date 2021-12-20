import pathlib
import itertools

import matplotlib.pyplot as plt
import matplotlib.axes
import matplotlib.image
import numpy as np
import scipy.interpolate
import scipy.stats
import pandas as pd

from typing import Any


class Renderer():
    __df: pd.DataFrame
    __root_dir: pathlib.Path

    def __init__(self, df: pd.DataFrame, root_dir: pathlib.Path):
        self.__df = df
        self.__root_dir = root_dir

    def correlations(self):
        column_names = [column for column in self.__df.columns if column != 'cost']

        if len(column_names) <= 2:
            n_rows, n_columns = 1, len(column_names)
        else:
            n_columns = 2
            if len(column_names) % 2 == 0:
                n_rows = int(len(column_names) / n_columns)
            else:
                n_rows = int(len(column_names) / n_columns) + 1

        # this multiplier is purely empirical...
        figsize = (6 * n_rows, 6 * n_columns)

        fig, axes = plt.subplots(nrows=n_rows, ncols=n_columns, figsize=figsize,
                                 squeeze=False, constrained_layout=True)
        axes = axes.flat

        for i in range(len(axes)):
            if i < len(column_names):
                self.__render_correlation(axes[i], column_names[i])
            else:
                axes[i].axis('off')

        figure_path = self.__root_dir.joinpath("correlation.png")
        fig.savefig(figure_path)

    def __render_correlation(self, ax: matplotlib.axes.Axes, col_name: str):
        x = self.__df[col_name]
        y = self.__df['cost']
        slope, intercept, r, p, stderr = scipy.stats.linregress(x, y)

        line = f'Regression: cost={intercept:.2f}+{slope:.2f}{col_name}, r={r:.2f}'

        ax.plot(x, y, linewidth=0, marker='o', label='Data points', color='blue')
        ax.plot(x, intercept + slope * x, label=line)
        ax.set_xlabel(col_name)
        ax.set_ylabel('Cost')
        ax.legend(facecolor='white', loc='upper center')

    def pairwise_heatmap_matrix(self):
        column_names = [column for column in self.__df.columns if column != 'cost']

        # approximate size that make image look well
        figsize = (4 * len(column_names), 4 * len(column_names))

        fig, axes = plt.subplots(nrows=len(column_names) - 1,
                                 ncols=len(column_names) - 1,
                                 figsize=figsize,
                                 constrained_layout=True,
                                 )
        im = None
        for i in range(len(column_names) - 1):
            for j in range(0, i):
                axes[j, i].axis('off')
                pass
            for j in range(i + 1, len(column_names)):
                col_name_1, col_name_2 = column_names[i], column_names[j]
                ax = axes[j - 1, i]
                im = self.__render_pairwise_heatmap(ax, col_name_1, col_name_2)

        fig.colorbar(im, ax=axes, shrink=0.6)

        figure_path = self.__root_dir.joinpath("pairwise_heatmap_matrix.png")
        fig.savefig(figure_path)

    def __render_pairwise_heatmap(self,
                                  ax: matplotlib.axes.Axes,
                                  col_name_1: str,
                                  col_name_2: str) -> matplotlib.image.AxesImage:
        data = self.__df[[col_name_1, col_name_2, "cost"]]

        # compute grid bounds
        x_min, x_max = data[col_name_1].min(), data[col_name_1].max()
        y_min, y_max = data[col_name_2].min(), data[col_name_2].max()
        cost_min, cost_max = self.__df["cost"].min(), self.__df["cost"].max()
        samples = 100
        x_step = (x_max - x_min) / samples
        y_step = (y_max - y_min) / samples
        grid_x, grid_y = np.mgrid[x_min:x_max:x_step, y_min:y_max:y_step]

        # interpolate data
        grid = scipy.interpolate.griddata(
            data[[col_name_1, col_name_2]],
            data["cost"],
            (grid_x, grid_y),
            method='linear',
        )

        # render interpolated grid
        # TODO: https://stackoverflow.com/questions/33282368/plotting-a-2d-heatmap-with-matplotlib/54088910#54088910
        im = ax.imshow(grid, cmap='jet', origin='lower', interpolation='lanczos', vmin=cost_min, vmax=cost_max)

        # assign real values to ticks
        x_scale, y_scale = (x_max - x_min) / samples, (y_max - y_min) / samples
        ax.set_xticklabels(map(lambda t: self.__absolutize_tick_labels(x_scale, t), ax.get_xticks().tolist()))
        ax.set_yticklabels(map(lambda t: self.__absolutize_tick_labels(y_scale, t), ax.get_yticks().tolist()))

        # assign axes labels
        ax.set_xlabel(col_name_1)
        ax.set_ylabel(col_name_2)

        return im

    @staticmethod
    def __absolutize_tick_labels(scale: float, tick: Any):
        if isinstance(tick, int):
            return int(tick * scale)
        elif isinstance(tick, float):
            return tick * scale
        else:
            raise TypeError(f"unexpected type {tick}")
