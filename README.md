# plecoptera

Find better configuration of your Go service using modern derivative-free optimization algorithms.

## Motivation

Configuration has crucial impact on how software performs in production. 
Often we have no clue what configuration can be considered "optimal", 
especially when working with complicated services and libraries
including dozens and even hundreds of parameters.
Software performance metrics depend on these parameters, 
but we cannot determine the type of this dependency.
The whole system starts to act like a "black box": 
we do not understand what's under the hood,
we only control inputs and outputs of a system.

This is exactly where optimization methods usually takes the stage:
* We define a **cost function**.
Basically it may look like a combination of performance metrics such as
latency, RPS, CPU utilization and so on. 
* We describe the domain of the function and set reasonable constrains
for the variable parameters.
* We provide external **optimizer** with the cost function 
and run him to find its optimum.

The problem is in the *cost* of a cost function evaluation. 
In a real-world examples, it's highly likely that every call 
of a cost function would be *very* expensive,
because of resource-intensive performance tests and  
IO- or CPU-bound computations.
Therefore, the number of cost function invocations must be as 
little as possible.

All the classic optimization techniques are based on [gradient descent](https://en.wikipedia.org/wiki/Gradient_descent).
On each iteration, optimizer computes partial derivatives of explored function.
Basing on the computed derivative values, optimizer decides, where to go 
on the next step. This is how optimizer moves towards the optimum of a function.

There are three major downsides of this technique:

* Some of gradient-descent-based algorithms require the cost function (as 
well as its derivative function) to be expressed explicitly. 
Of course, it doesn't work for us, because we treat the software as
a black box system and don't know the exact form of the cost function.
* Since the cost function derivative is unknown,
the function gradient must be computed numerically. 
This requires huge number of extra evaluations of the cost function. 
Thus the gradient-descent methods are [ineffective](https://datascience.stackexchange.com/a/105080/97074)
in the terms of cost functions evaluations.
* For a certain type of functions, gradient-descent may end up with
*local* optimum instead of *global* optimum. 

Modern optimization algorithms try to avoid the computation of the
derivative and gradient of a cost function. 
Plecoptera is based on one of these tools - [RBFOpt](https://github.com/coin-or/rbfopt).
If you're interested, please read either RBFOpt [brief annotation](https://developer.ibm.com/open/projects/rbfopt/), 
or [full whitepaper](http://www.optimization-online.org/DB_FILE/2014/09/4538.pdf).

## Architecture

Plecoptera consists of two parts:

* Python script wrapping RBFopt.
* Go library - an abstraction layer that hides the details of external optimizers
from the clients.

Go library executes Python script as a subprocess and runs the HTTP server 
to handle requests emitted by the optimizer working on Python side.

## Installation

### External dependencies

#### RHEL-based

```bash
sudo dnf install -y coin-or-Bonmin python3-virtualenv
```

#### Debian-based

```bash
# TODO: check
```

### Plecoptera

```bash
virtualenv venv
source venv/bin/activate
# TODO: release on pypi
pip install git+https://github.com/vitalyisaev2/plecoptera.git   
go get github.com/vitalyisaev2/plecoptera.git   
```

## Example 

```go
package main

import (
    "context"
    
    "github.com/vitalyisaev2/plecoptera/optimization"
)

// Define a configuration structure in any way you want.
// For the sake of simplicity, we take only three parameters.
// In a real world, configuration structures are much more sophisticated.
type serviceConfig struct {
	paramX int
	paramY int
	paramZ int
}

// Define parameter setters. External optimizer will use them to mutate
// configuration on each iteration of the algorithm.
// If it's more convinient for you, instead of making explicit methods, 
// you may use anonymous functions later.
func (cfg *serviceConfig) setParamX(value int) { cfg.paramX = value }
func (cfg *serviceConfig) setParamY(value int) { cfg.paramY = value }
func (cfg *serviceConfig) setParamZ(value int) { cfg.paramZ = value }

// Define a cost function. It must perform some computation on the basis
// of configuration provided by external optimizer.
// If it's more convinient for you, instead of making explicit method, 
// you may use closure later.
func (cfg *serviceConfig) costFunction(_ context.Context) (optimization.Cost, error) {
    // For clarity, we will use quite a simple polinomial function 
    // with optimum that can be easily discovered: 
	// it corresponds to the upper bound of every variable.
	// In real-world example, one will have to evaluate cost empirically.
	x, y, z := cfg.paramX, cfg.paramY, cfg.paramZ
	return optimization.Cost(-1 * (x * y  + z)), nil
}

func main()cfg := &serviceConfig{}
    // The most important part is optimizer settings.
	settings := &optimization.Settings{
	    // Here you describe the variables and set the bounds.
		Parameters: []*optimization.ParameterDescription{
			{
				Name:           "x",
				Bound:          &optimization.Bound{From: 0, To: 10},
				ConfigModifier: cfg.setParamX,
			},
			{
				Name:           "y",
				Bound:          &optimization.Bound{From: 0, To: 10},
				ConfigModifier: cfg.setParamY,
			},
			{
				Name:           "z",
				Bound:          &optimization.Bound{From: 0, To: 10},
				ConfigModifier: cfg.setParamZ,
			},
		},
		CostFunction:   cfg.costFunction,
		// This variable controls trade-off between 
		// the accuracy of determination of the optimum 
		// and the time spent on it.
		MaxEvaluations: 100,
	}

    // Here you may set timeout or provide this context
    // with an instance of a logger (see library source code for details)
	ctx := context.Background()

    // Run optimization
	report, err := optimization.Optimize(ctx, settings)
	if err != nil {
	    panic(err)
	}
	fmt.Println(report)
}

```

## Limiataions