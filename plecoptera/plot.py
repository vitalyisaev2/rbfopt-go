import matplotlib.pyplot as plt
import matplotlib.axes
import numpy as np
import pandas as pd


class Renderer():
    __df: pd.DataFrame

    def __init__(self, df: pd.DataFrame):
        self.__df = df

    def matrix(self, figsize=(12, 12)):
        column_names = [column for column in self.__df.columns if column != 'cost']

        fig, axes = plt.subplots(nrows=len(column_names),
                                 ncols=len(column_names),
                                 figsize=figsize)

        for i in range(len(column_names)):
            for j in range(i+1, len(column_names)):
                col_name_1, col_name_2 = column_names[i], column_names[j]
                ax = axes[i, j]
                self.__render_single(col_name_1, col_name_2, ax)

        fig.savefig('/tmp/foo.png')

    def __render_single(self, col_name_1: str, col_name_2: str, ax: matplotlib.axes.Axes):
        selected = self.__df[[col_name_1, col_name_2, "cost"]]
        averaged = selected.groupby([col_name_1, col_name_2])['cost'].\
            agg(lambda x: x.unique().sum() / x.nunique()).\
            reset_index()

        # TODO: estimate these limits only once
        cost_min, cost_max = self.__df["cost"].min(), self.__df["cost"].max()

        out = averaged[[col_name_1, col_name_2, "cost"]]
        print(out)

        c = ax.pcolormesh(out, cmap='cool', vmin=cost_min, vmax=cost_max)
        x = averaged[col_name_1]
        y = averaged[col_name_2]
        ax.axis([x.min(), x.max(), y.min(), y.max()])
        ax.set_xlabel(col_name_1)
        ax.set_ylabel(col_name_2)

        # TODO: https://stackoverflow.com/questions/33282368/plotting-a-2d-heatmap-with-matplotlib/54088910#54088910
