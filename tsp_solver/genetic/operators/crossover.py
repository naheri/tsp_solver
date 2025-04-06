# tsp_solver/genetic/operators/crossover.py
import random

def ordered_crossover(parent1, parent2):
    """
    Ordered crossover (OX): preserves the relative order of cities from parent1
    while inheriting cities from parent2 that are not yet present.
    
    Args:
        parent1 (list): First parent (list of cities)
        parent2 (list): Second parent (list of cities)
        
    Returns:
        list: New individual (list of cities)
    """
    child = [None] * len(parent1)
    
    # Randomly choose two cut points
    start_idx, end_idx = sorted(random.sample(range(len(parent1)), 2))
    
    # Copy the section between the cut points from parent1
    for i in range(start_idx, end_idx + 1):
        child[i] = parent1[i]
    
    # Add the remaining cities in the order they appear in parent2
    ptr = (end_idx + 1) % len(parent1)
    p2_idx = (end_idx + 1) % len(parent2)
    
    while None in child:
        if parent2[p2_idx] not in child:
            child[ptr] = parent2[p2_idx]
            ptr = (ptr + 1) % len(child)
        p2_idx = (p2_idx + 1) % len(parent2)
    
    return child

def cycle_crossover(parent1, parent2):
    """
    Cycle crossover (CX): preserves the absolute position of cities.
    
    Args:
        parent1 (list): First parent (list of cities)
        parent2 (list): Second parent (list of cities)
        
    Returns:
        list: New individual (list of cities)
    """
    size = len(parent1)
    child = [None] * size
    
    # Dictionaries for quick position lookup
    p1_dict = {parent1[i]: i for i in range(size)}
    p2_dict = {parent2[i]: i for i in range(size)}
    
    # Start with the first element of parent1
    start_pos = 0
    current_pos = 0
    current_value = parent1[current_pos]
    
    # Mark the cycle
    while True:
        child[current_pos] = parent1[current_pos]
        current_pos = p1_dict[parent2[current_pos]]
        
        if current_pos == start_pos:
            break
    
    # Fill the remaining positions with parent2
    for i in range(size):
        if child[i] is None:
            child[i] = parent2[i]
    
    return child