import rbfopt
import numpy as np

def obj_funct(x):
    print(">>>>: ", x)
    return x[0]*x[1] - x[2]

def main():
    bb = rbfopt.RbfoptUserBlackBox(3, np.array([0] * 3), np.array([10] * 3),
                                   np.array(['R', 'I', 'R']), obj_funct)
    settings = rbfopt.RbfoptSettings(max_evaluations=50)
    alg = rbfopt.RbfoptAlgorithm(settings, bb)
    val, x, itercount, evalcount, fast_evalcount = alg.optimize()
    print(val, x, itercount, evalcount, fast_evalcount)

if __name__ == "__main__":
    main()

