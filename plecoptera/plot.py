import pathlib

import matplotlib.pyplot as plt
import matplotlib.axes
import numpy as np
from scipy.interpolate import griddata
import pandas as pd


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

        fig, axes = plt.subplots(nrows=len(column_names)-1,
                                 ncols=len(column_names)-1,
                                 figsize=figsize)

        for i in range(len(column_names)):
            for j in range(i + 1, len(column_names)):
                col_name_1, col_name_2 = column_names[i], column_names[j]
                ax = axes[j-1, i]
                self.__render_single(ax, col_name_1, col_name_2)

        figure_path = self.__root_dir.joinpath("matrix.png")
        fig.savefig(figure_path)

    def __render_single(self, ax: matplotlib.axes.Axes, col_name_1: str, col_name_2: str):
        selected = self.__df[[col_name_1, col_name_2, "cost"]]
        averaged = selected.groupby([col_name_1, col_name_2])['cost']. \
            agg(lambda x: x.unique().sum() / x.nunique()). \
            reset_index()

        x_min, x_max = averaged[col_name_1].min(), averaged[col_name_1].max()
        y_min, y_max = averaged[col_name_2].min(), averaged[col_name_2].max()

        grid_x, grid_y = np.mgrid[x_min:x_max, y_min:y_max]
        grid = griddata(
            averaged[[col_name_1, col_name_2]],
            averaged["cost"],
            (grid_x, grid_y),
            method='linear',
        )

        # TODO: estimate these limits only once
        cost_min, cost_max = self.__df["cost"].min(), self.__df["cost"].max()

        c = ax.imshow(grid, cmap='jet', origin='lower', vmin=cost_min, vmax=cost_max)

        ax.set_xlabel(col_name_1)
        ax.set_ylabel(col_name_2)

        # TODO: https://stackoverflow.com/questions/33282368/plotting-a-2d-heatmap-with-matplotlib/54088910#54088910
