# tsp_solver/genetic/operators/mutation.py
import random

def swap_mutation(route, mutation_rate):
    """
    Swap mutation: randomly exchanges pairs of cities.
    
    Args:
        route (list): Route to mutate (list of cities)
        mutation_rate (float): Probability of applying mutation to each city
        
    Returns:
        list: Mutated route
    """
    for i in range(len(route)):
        if random.random() < mutation_rate:
            # Randomly choose another city for the swap
            j = random.randint(0, len(route) - 1)
            # Avoid swapping a city with itself
            if i != j:
                # Swap the cities
                route[i], route[j] = route[j], route[i]
    return route

def insertion_mutation(route, mutation_rate):
    """
    Insertion mutation: inserts a city at a new position.
    
    Args:
        route (list): Route to mutate (list of cities)
        mutation_rate (float): Probability of applying mutation
        
    Returns:
        list: Mutated route
    """
    if random.random() < mutation_rate:
        # Choose a random city and a random insertion position
        idx1 = random.randint(0, len(route) - 1)
        idx2 = random.randint(0, len(route) - 1)
        
        # Avoid inserting at the same location
        if idx1 != idx2:
            city = route.pop(idx1)
            route.insert(idx2, city)
    
    return route

def inversion_mutation(route, mutation_rate):
    """
    Inversion mutation: reverses the order of cities between two points.
    
    Args:
        route (list): Route to mutate (list of cities)
        mutation_rate (float): Probability of applying mutation
        
    Returns:
        list: Mutated route
    """
    if random.random() < mutation_rate:
        # Choose two random positions
        i, j = sorted(random.sample(range(len(route)), 2))
        
        # Reverse the order of cities between these positions
        route[i:j+1] = reversed(route[i:j+1])
    
    return route