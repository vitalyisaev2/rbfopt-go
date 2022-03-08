# RBFOpt-go

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
in the terms of the number of the cost functions evaluations.
* For a certain type of functions, gradient-descent may end up with
*local* optimum instead of *global* optimum. 

Modern optimization algorithms try to avoid the computation of the
derivative and gradient of a cost function. 
Rbfopt-go is based on one of these tools - [RBFOpt](https://github.com/coin-or/rbfopt).
If you're interested, please read either RBFOpt [brief annotation](https://developer.ibm.com/open/projects/rbfopt/), 
or [full whitepaper](http://www.optimization-online.org/DB_FILE/2014/09/4538.pdf).

## Architecture

RBFOpt-go consists of two parts:

* Python script wrapping RBFOpt.
* Go library hiding the details of external optimizer work from clients.

Go library executes Python script as a subprocess and runs 
internal HTTP server to handle requests emitted by the optimizer.

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

### rbfopt-go

```bash
virtualenv venv
source venv/bin/activate
pip install rbfopt-go
go get github.com/vitalyisaev2/rbfopt-go
```

## Example 

### Code

```go
package main

import (
	"context"
	"fmt"

	"github.com/vitalyisaev2/rbfopt-go/optimization"
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
	// It's not possible to draw this function (because it's 4D),
	// but it's quite easy to reason about it. 
	//
	// Please remember that in practice, you will have to evaluate cost empirically,
	// and this is the place where you will launch performance tests
	// and measure performance metrics.
	x, y, z := cfg.paramX, cfg.paramY, cfg.paramZ
	return optimization.Cost(-1 * (x*y + z)), nil
}

func main() {
	cfg := &serviceConfig{}

	// Describe the variables and set the bounds.
	settings := &optimization.Settings{
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
		CostFunction: cfg.costFunction,
		// This variable controls trade-off between the accuracy of
		// determination of the optimum and the time spent on it.
		MaxEvaluations: 10,
	}

	// Here you may set timeout or provide this context
	// with an instance of a logger (see library source code for details)
	ctx := context.Background()

	// Run optimization
	report, err := optimization.Optimize(ctx, settings)
	if err != nil {
		panic(err)
	}

	fmt.Printf("Minimal cost: %v\n", report.Cost)
	fmt.Printf("Optimum:\n")
	for _, p := range report.Optimum {
		fmt.Printf("%s: %v\n", p.Name, p.Value)
	}
}

```

Finally you'll see the parameter values corresponding to the 
optimum of the cost function.
```bash
Minimal cost: -110
Optimum:
x: 10
y: 10
z: 10
```

### Analysis

Aside from the discovered optimum value, RBFOpt-go provides you 
with several plots that may give you some inspiration 
when exploring the cost function.
You can find them in `/tmp/rbfopt_$timestamp` directory.

Please note that on each of these plots not all data points are depicted,
but only the minimum reached in this point.
For a particular value of a certain parameter, optimizer may do several cost function evaluations
(with different values of other parameters), but only the minimal  
value of cost function is shown on the plot.

#### Linear regression plot

A simple correlation between parameters and 
the cost function helps to estimate the contribution of each
parameter to the final value of a cost function.

All discovered points:

![correlation](/docs/scatterplot_all_values.png)

Only optimal points:

![correlation](/docs/scatterplot_only_optimal_values.png)

#### Pairwise heatmaps

On each of these plots cost function values are "mapped" to the axes
formed by all possible pairs of parameters. 
This matrix of plots helps to find out the nature of interaction
of parameters between each other (and their influence on the cost function).

![pairwise heatmap matrix](/docs/pairwise_heatmap_matrix.png)

## Limitations

* Floating-point and categorical parameters are not supported yet.
