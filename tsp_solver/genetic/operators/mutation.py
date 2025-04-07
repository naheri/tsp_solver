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
            j = random.randint(0, len(route) - 1)
            if i != j:
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
        city = random.randint(0, len(route) - 1)
        insertion_pos = random.randint(0, len(route) - 1)
        
        if city != insertion_pos:
            city = route.pop(city)
            route.insert(insertion_pos, city)
    
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
        i, j = sorted(random.sample(range(len(route)), 2))
        route[i:j+1] = reversed(route[i:j+1])
    
    return route