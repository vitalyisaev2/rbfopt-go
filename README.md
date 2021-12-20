# plecoptera
Configuration may have crucial impact on how software performs in production. 
Often we have no clue what configuration can be considered "optimal", espicially in complicated services and libraries
including dozens and even hundreds of parameters.
Software performance metrics depend on these parameters, but we cannot determine the type of this dependency.
The whole system starts to act like a "black box": we do not understand what's under the hood,
we only control inputs and outpus of a system.

Here is where optimization methods usually come. We define a **cost function**,
which usually looks like a combination of performance metrics like latency, RPS,
CPU utilization and so on. 
Then we describe the domain of the function and set reasonable constrains
for the variable parameters.
Finally, we provide external **optimizer** with this 
function and ask him to find its local (or global) optimum.

The problem is in the *cost* of a cost function. 
In a real-world software, every call of a cost function may be *very* expensive,
because it may involve resource-intensive perfomance tests, IO or CPU-intensive computations.
Therefore, the number of cost function invocations must be as less as possible.

All the classic optimization techniques are based on [gradient descent](https://en.wikipedia.org/wiki/Gradient_descent).
On each iteration, optimizer computes partial derivatives of explored function,
moving towards the optimum.

// to be continued

Find better configuration for your Go service using modern derivative-free optimization algorithms.

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
pip install git+https://github.com/vitalyisaev2/plecoptera.git   
```
