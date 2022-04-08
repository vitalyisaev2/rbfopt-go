#!/usr/bin/env python
import pathlib
import sys
import time
from datetime import datetime

import rbfopt

from wrapper.client import Client
from wrapper.evaluator import Evaluator
from wrapper.plot import Renderer
from wrapper.settings import Settings


def main():
    # prepare infrastructure
    root_dir = pathlib.Path(sys.argv[1])
    wrapper_settings = Settings.from_file(root_dir)
    print(f"wrapper_settings: {wrapper_settings}")

    client = Client(wrapper_settings.endpoint)
    evaluator = Evaluator(client, wrapper_settings.var_names, root_dir)

    bb = rbfopt.RbfoptUserBlackBox(
        wrapper_settings.dimensions,
        wrapper_settings.var_lower,
        wrapper_settings.var_upper,
        wrapper_settings.var_types,
        evaluator.estimate_cost,
    )

    # perform optimization
    rbfopt_settings = rbfopt.RbfoptSettings(
        max_evaluations=wrapper_settings.max_evaluations,
        max_iterations=wrapper_settings.max_iterations,
        rand_seed=int(time.mktime(datetime.now().timetuple())),
        init_strategy=wrapper_settings.init_strategy,
    )
    alg = rbfopt.RbfoptAlgorithm(rbfopt_settings, bb)

    # post report to server
    evaluator.register_report(*alg.optimize())
    evaluations, report = evaluator.dump()

    # render plots
    renderer = Renderer(wrapper_settings, evaluations, report, root_dir)
    renderer.scatterplots()
    renderer.pairwise_heatmap_matrix()


if __name__ == "__main__":
    main()
