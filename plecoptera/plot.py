import pathlib

import matplotlib.pyplot as plt
import matplotlib.axes
import numpy as np
import scipy.interpolate
import pandas as pd

from typing import Any


class Renderer():
    __df: pd.DataFrame
    __root_dir: pathlib.Path

    def __init__(self, df: pd.DataFrame, root_dir: pathlib.Path):
        self.__df = df
        self.__root_dir = root_dir

    def matrix(self):
        column_names = [column for column in self.__df.columns if column != 'cost']

        # approximate size that make image look well
        figsize = (4 * len(column_names), 4 * len(column_names))

        fig, axes = plt.subplots(nrows=len(column_names) - 1,
                                 ncols=len(column_names) - 1,
                                 figsize=figsize)

        for i in range(len(column_names) - 1):
            for j in range(0, i):
                axes[j, i].axis('off')
                pass
            for j in range(i + 1, len(column_names)):
                col_name_1, col_name_2 = column_names[i], column_names[j]
                ax = axes[j - 1, i]
                self.__render_single(ax, col_name_1, col_name_2)

        figure_path = self.__root_dir.joinpath("matrix.png")
        fig.savefig(figure_path)

    def __render_single(self, ax: matplotlib.axes.Axes, col_name_1: str, col_name_2: str):
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
        ax.imshow(grid, cmap='jet', origin='lower', interpolation='lanczos', vmin=cost_min, vmax=cost_max)

        # assign real values to ticks
        x_scale, y_scale = (x_max - x_min) / samples, (y_max - y_min) / samples
        ax.set_xticklabels(map(lambda t: self.__absolutize_tick_labels(x_scale, t), ax.get_xticks().tolist()))
        ax.set_yticklabels(map(lambda t: self.__absolutize_tick_labels(y_scale, t), ax.get_yticks().tolist()))

        # assign axes labels
        ax.set_xlabel(col_name_1)
        ax.set_ylabel(col_name_2)


    @staticmethod
    def __absolutize_tick_labels(scale: float, tick: Any):
        if isinstance(tick, int):
            return int(tick * scale)
        elif isinstance(tick, float):
            return tick * scale
        else:
            raise TypeError(f"unexpected type {tick}")
