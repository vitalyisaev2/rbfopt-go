#!/usr/bin/env python
import sys

import pandas as pd
import rbfopt
from plecoptera.client import Client
from plecoptera.evaluator import Evaluator
from plecoptera.settings import Settings
from plecoptera.plot import Renderer


def main():
    # prepare infrastructure
    settings = Settings.from_config(sys.argv[1])

    client = Client(settings.endpoint)
    evaluator = Evaluator(client, settings.var_names)

    bb = rbfopt.RbfoptUserBlackBox(
        settings.dimensions,
        settings.var_lower,
        settings.var_upper,
        settings.var_types,
        evaluator.estimate_cost,
    )

    # perform optimization
    settings = rbfopt.RbfoptSettings(max_evaluations=settings.max_evaluations)
    alg = rbfopt.RbfoptAlgorithm(settings, bb)

    # post report to server
    evaluator.register_report(*alg.optimize())

    # render plots
    renderer = Renderer(evaluator.evaluations)
    renderer.matrix()

    # df = evaluator.evaluations
    # print(df)
    # selected = df[["x", "y", "cost"]]
    # print(selected)
    # print(">>>>", selected.groupby(['x', 'y'])['cost'])
    # unique = selected.groupby(['x', 'y'])['cost'].agg(lambda x: x.unique().sum() / x.nunique()).reset_index()
    # print(unique)
    # unique_df = pd.DataFrame(unique)
    # print(unique_df)
    # print(unique_df.pivot("x", "y", "cost"))


if __name__ == "__main__":
    main()
