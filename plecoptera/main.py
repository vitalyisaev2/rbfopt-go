#!/usr/bin/env python
import pathlib
import sys
import time
from datetime import datetime

import rbfopt

from plecoptera.client import Client
from plecoptera.evaluator import Evaluator
from plecoptera.plot import Renderer
from plecoptera.settings import Settings


def main():
    # prepare infrastructure
    root_dir = pathlib.Path(sys.argv[1])
    settings = Settings.from_file(root_dir)

    client = Client(settings.endpoint)
    evaluator = Evaluator(client, settings.var_names, root_dir)

    bb = rbfopt.RbfoptUserBlackBox(
        settings.dimensions,
        settings.var_lower,
        settings.var_upper,
        settings.var_types,
        evaluator.estimate_cost,
    )

    # perform optimization
    settings = rbfopt.RbfoptSettings(
        max_evaluations=settings.max_evaluations,
        max_iterations=settings.max_iterations,
        rand_seed=int(time.mktime(datetime.now().timetuple())),
    )
    alg = rbfopt.RbfoptAlgorithm(settings, bb)

    # post report to server
    evaluator.register_report(*alg.optimize())
    evaluations, report = evaluator.dump()

    # render plots
    renderer = Renderer(evaluations, report, root_dir)
    renderer.pairwise_heatmap_matrix()
    renderer.correlations()


if __name__ == "__main__":
    main()
