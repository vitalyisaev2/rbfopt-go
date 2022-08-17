import functools
import pathlib
import typing
from typing import Any, Callable

import matplotlib.axes
import matplotlib.image
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
import scipy.interpolate
import scipy.stats
from colorhash import ColorHash

import wrapper.names as names
from wrapper.report import Report
from wrapper.settings import Settings


class Renderer:
    __df: pd.DataFrame
    __root_dir: pathlib.Path
    __report: Report

    def __init__(self, ss: Settings, df: pd.DataFrame, report: Report, root_dir: pathlib.Path):
        # filter values corresponding to ErrInvalidParameterCombination params (if necessary)
        if ss.skip_invalid_parameter_combination_on_plots:
            self.__df = df[df[names.InvalidParameterCombination] == False]
        else:
            self.__df = df

        self.__root_dir = root_dir
        self.__report = report

    @property
    @functools.cache
    def __parameter_column_names(self) -> typing.List[str]:
        utility_columns = (names.Cost, names.InvalidParameterCombination)
        return list(filter(lambda x: x not in utility_columns, self.__df.columns))

    @property
    @functools.cache
    def __cost_bounds(self) -> typing.List[str]:
        cost = self.__df[names.Cost]
        return [cost.min(), cost.max()]

    def scatterplots(self):
        self.__render_scatterplot_group(only_optimal_values=False)
        self.__render_scatterplot_group(only_optimal_values=True)

    def __render_scatterplot_group(self, only_optimal_values: bool):
        column_names = self.__parameter_column_names

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
                self.__render_scatterplot(axes[i], column_names[i], only_optimal_values=only_optimal_values)
            else:
                axes[i].axis('off')

        fig.tight_layout()

        suffix = "only_optimal_values" if only_optimal_values else "all_values"
        figure_path = self.__root_dir.joinpath(f"scatterplot_{suffix}.png")
        fig.savefig(figure_path)

    def __render_scatterplot(self, ax: matplotlib.axes.Axes, col_name: str, only_optimal_values: bool):
        data = pd.DataFrame({col_name: self.__df[col_name], names.Cost: self.__df[names.Cost]})

        if only_optimal_values:
            # for every argument value, pick the best cost function value
            data = data.groupby(col_name)[names.Cost].agg(lambda x: x.min()).reset_index()

        color = ColorHash(col_name).hex
        ax.plot(data[col_name], data[names.Cost], linewidth=0, marker='o', color=color)

        ax.set_xlabel(col_name, fontsize=14)
        ax.set_ylabel('Cost function', fontsize=14)

        # draw point with optimum
        opt_arg = self.__report.optimum_argument(col_name)
        opt_val = self.__report.cost
        ax.scatter(opt_arg, opt_val, color='red', marker='o', s=100)
        ax.annotate("{:.2f}".format(opt_val), (opt_arg, opt_val))

        # set equal limits
        (cost_min, cost_max) = self.__cost_bounds
        # ax.set_ybound(lower=cost_min, upper=cost_max)
        ax.set_ylim(bottom=cost_min, top=cost_max)
        print(col_name, cost_min, cost_max)

    def pairwise_heatmap_matrix(self):
        column_names = self.__parameter_column_names

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
        data = self.__df[[col_name_1, col_name_2, names.Cost]]

        # select the minimums
        data = data.groupby([col_name_1, col_name_2])[names.Cost].agg(lambda x: x.min()).reset_index()

        # compute grid bounds
        x_min, x_max = data[col_name_1].min(), data[col_name_1].max()
        y_min, y_max = data[col_name_2].min(), data[col_name_2].max()
        (cost_min, cost_max) = self.__cost_bounds
        samples = 100
        x_step = (x_max - x_min) / samples
        y_step = (y_max - y_min) / samples
        grid_x, grid_y = np.mgrid[x_min:x_max:x_step, y_min:y_max:y_step]

        # interpolate data
        grid = scipy.interpolate.griddata(
            data[[col_name_1, col_name_2]],
            data[names.Cost],
            (grid_x, grid_y),
            method='cubic',
        )

        # render interpolated grid
        im = ax.imshow(grid.T, cmap='jet', origin='lower', interpolation='quadric', vmin=cost_min, vmax=cost_max)

        # scale ticks
        x_scale, y_scale = (x_max - x_min) / samples, (y_max - y_min) / samples
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(self.__tick_scaler(x_scale)))
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(self.__tick_scaler(y_scale)))

        # draw point with optimum
        opt_x, opt_y, opt_val = self.__derive_optimum_coordinates(col_name_1, col_name_2, x_scale, y_scale)
        ax.scatter(opt_x, opt_y, color='red', marker='o', s=100)
        ax.annotate("{:.2f}".format(opt_val), (opt_x, opt_y))

        # assign axes labels
        ax.set_xlabel(col_name_1, fontsize=14)
        ax.set_ylabel(col_name_2, fontsize=14)

        return im

    @staticmethod
    def __tick_scaler(scale) -> Callable[[Any, Any], str]:
        def tick_formater(val, pos) -> str:
            tick = val * scale
            if tick.is_integer():
                return str(int(tick))
            else:
                # FIXME: it's a hodgie (индусский) code now - write smart algorithm instead of that
                if tick >= 100:
                    return str(int(tick))
                elif tick >= 10:
                    return "{:.1f}".format(tick)
                elif tick >= 1:
                    return "{:.2f}".format(tick)
                else:
                    return "{:.3f}".format(tick)

        return tick_formater

    def __derive_optimum_coordinates(self,
                                     col_name_1: str, col_name_2: str,
                                     col_scale_1: float, col_scale_2: float,
                                     ) -> (float, float, float):
        col_val_1 = self.__report.optimum_argument(col_name_1) / col_scale_1
        col_val_2 = self.__report.optimum_argument(col_name_2) / col_scale_2
        cost_val = self.__report.cost

        return col_val_1, col_val_2, cost_val
