#!/usr/bin/env python
import sys
import rbfopt
from plecoptera.client import Client
from plecoptera.evaluator import Evaluator
from plecoptera.settings import Settings


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

    # perform optimization and post report to server
    settings = rbfopt.RbfoptSettings(max_evaluations=10)
    alg = rbfopt.RbfoptAlgorithm(settings, bb)
    evaluator.register_report(*alg.optimize())


if __name__ == "__main__":
    main()