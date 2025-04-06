# Traveling Salesman Problem Solver with Genetic Algorithms

![TSP Solver](https://raw.githubusercontent.com/yourusername/tsp-solver/main/docs/images/example.png)

A Python implementation of a genetic algorithm to solve the Traveling Salesman Problem (TSP) with multiple selection, crossover, and mutation operators. This implementation is based on established research in evolutionary computation and combinatorial optimization.

## Features

### Multiple Genetic Operators

#### Selection Operators
- **Tournament Selection**: Selects individuals through a tournament of size k
  - Complexity: O(k log k)
  - Based on [Miller & Goldberg, 1995](https://doi.org/10.1162/evco.1995.3.4.373)

- **Elitism**: Preserves the n best solutions
  - Ensures monotonic improvement in the best solution
  - [Rudolph, 1994](https://doi.org/10.1109/TEVC.1994.4766865)

#### Crossover Operators
- **Ordered Crossover (OX)**:
  - Preserves relative order of cities
  - Mathematical formulation:
    ```
    Let P₁, P₂ be parents of length n
    Child[i:j] = P₁[i:j]
    Remaining = [x ∈ P₂ | x ∉ P₁[i:j]]
    ```
  - [Davis, 1985](https://doi.org/10.1145/645776.645777)

- **Cycle Crossover (CX)**:
  - Preserves absolute positions
  - [Oliver et al., 1987](https://doi.org/10.1145/42369.42370)

#### Mutation Operators
1. **Swap Mutation**
   - Probability per position: p_m
   - Random exchange of two cities

2. **Insertion Mutation**
   - Single city relocation
   - [Michalewicz, 1992](https://doi.org/10.1007/978-3-662-03363-6)

3. **Inversion Mutation**
   - Reverses a subsequence of cities
   - Based on biological chromosome inversion

## Mathematical Foundation

### Fitness Function
For a route R = (c₁, c₂, ..., cₙ), the total distance is:

```math
D(R) = \sum_{i=1}^{n-1} d(c_i, c_{i+1}) + d(c_n, c_1)