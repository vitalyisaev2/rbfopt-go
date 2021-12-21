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
we only control inputs and outpus of a system.

Here is where optimization methods usually take place:
* We define a **cost function**. It usually looks like a combination of performance metrics like latency, RPS,
CPU utilization and so on. 
* We describe the domain of the function and set reasonable constrains
for the variable parameters.
* We provide external **optimizer** with the cost function 
function and run him to find its optimum.

The problem is in the *cost* of a cost function evaluation. 
In a real-world examples, it's highly likely that every call 
of a cost function would be *very* expensive,
because it may involve resource-intensive performance tests, 
IO or CPU-intensive computations.
Therefore, the number of cost function invocations must be as 
little as possible.

All the classic optimization techniques are based on [gradient descent](https://en.wikipedia.org/wiki/Gradient_descent).
On each iteration, optimizer computes partial derivatives of explored function.
Basing on the computed derivative values, optimizer decides, where to go 
on the next step. That's how optimizer moves towards the function optimum.

There are three major downsides of this technique:

* Some of gradient-descent-based algorithms require the cost function (as 
well as its derivative function) to be expressed explicitly. 
Of course, it's not the case for us, because we treat the software as
a black box system and don't know the exact form of the cost function.
* As a long as the cost function derivative is unknown, the function gradient 
must be computed numerically. This requires huge number of extra evaluations
of the cost function. Gradient-descent methods are [ineffective](https://datascience.stackexchange.com/a/105080/97074) in the terms
of cost functions evaluations.
* For a certain type of functions, gradient-descent may end up with
*local* optimum instead of *global* optimum. 

Modern optimization algorithms try to avoid the computation of the
cost function derivative. 
Plecoptera is based on one of these tools - [RBFOpt](https://github.com/coin-or/rbfopt).
If you're interested, please read either RBFOpt [brief annotation](https://developer.ibm.com/open/projects/rbfopt/), 
or [full whitepaper](http://www.optimization-online.org/DB_FILE/2014/09/4538.pdf).

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
