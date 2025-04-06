# tsp_solver/genetic/operators/selection.py
import random

def tournament_selection(population, fitness_results, tournament_size):
    """
    Tournament selection: selects the best individuals from random subgroups.
    
    Args:
        population (list): List of routes (individuals) in the population
        fitness_results (dict): Dictionary mapping each route's index to its fitness
        tournament_size (int): Number of individuals participating in each tournament
        
    Returns:
        int: Index of the selected individual
    """
    # Randomly select tournament participants
    tournament_candidates = random.sample(range(len(population)), tournament_size)
    
    # Find the best participant in the tournament
    tournament_fitness = [(i, fitness_results[i]) for i in tournament_candidates]
    tournament_fitness.sort(key=lambda x: x[1], reverse=True)
    
    # Return the tournament winner
    return tournament_fitness[0][0]

def elitism_selection(fitness_results, elite_size):
    """
    Elitism selection: selects the n best individuals.
    
    Args:
        fitness_results (dict): Dictionary mapping each route's index to its fitness
        elite_size (int): Number of elites to select
        
    Returns:
        list: Indices of selected elites
    """
    # Sort individuals by descending fitness
    sorted_fitness = [(i, fitness_results[i]) for i in range(len(fitness_results))]
    sorted_fitness.sort(key=lambda x: x[1], reverse=True)
    
    # Return indices of the n best individuals
    return [sorted_fitness[i][0] for i in range(min(elite_size, len(sorted_fitness)))]