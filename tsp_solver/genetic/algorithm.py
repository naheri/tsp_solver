# tsp_solver/genetic/algorithm.py
import random
import numpy as np
from ..genetic.operators.selection import tournament_selection, elitism_selection
from ..genetic.operators.crossover import ordered_crossover, cycle_crossover
from ..genetic.operators.mutation import swap_mutation, insertion_mutation, inversion_mutation

class GeneticAlgorithm:
    """Implementation of a genetic algorithm to solve the Traveling Salesman Problem"""
    
    def __init__(self, cities, population_size=100, elite_size=20, 
                 mutation_rate=0.01, tournament_size=5,
                 crossover_type="ordered", mutation_type="swap"):
        """
        Initialize the genetic algorithm.
        
        Args:
            cities (list): List of cities to visit
            population_size (int): Population size
            elite_size (int): Number of elites to retain
            mutation_rate (float): Mutation rate
            tournament_size (int): Tournament size for selection
            crossover_type (str): Type of crossover to use ('ordered' or 'cycle')
            mutation_type (str): Type of mutation to use ('swap', 'insertion', or 'inversion')
        """
        self.cities = cities
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.crossover_type = crossover_type
        self.mutation_type = mutation_type
        
        self.population = []
        self.best_route = None
        self.best_distance = float('inf')
        self.generation = 0
        self.history = []  # To store the evolution of the best distance
    
    def create_initial_population(self):
        """Create an initial population of random routes"""
        self.population = []
        
        for _ in range(self.population_size):
            route = random.sample(self.cities, len(self.cities))
            self.population.append(route)
            
        self.best_route = None
        self.best_distance = float('inf')
        self.generation = 0
        self.history = []
        
        return self.population
    
    def calculate_distance(self, route):
        """
        Calculate the total distance of a route.
        
        Args:
            route (list): List of cities in the order of visit
            
        Returns:
            float: Total distance of the route
        """
        total_distance = 0
        for i in range(len(route)):
            from_city = route[i]
            to_city = route[(i + 1) % len(route)]
            total_distance += from_city.distance(to_city)
        
        return total_distance
    
    def calculate_fitness(self, route):
        """Calculate the fitness of a route (inverse of total distance)"""
        distance = self.calculate_distance(route)
        return 1 / distance if distance > 0 else float('inf')
    
    def evaluate_population(self):
        """Evaluate the fitness of the entire population"""
        fitness_results = {}
        
        for i, route in enumerate(self.population):
            fitness_results[i] = self.calculate_fitness(route)
            
            distance = self.calculate_distance(route)
            
            if distance < self.best_distance:
                self.best_distance = distance
                self.best_route = route.copy()
        
        self.history.append(self.best_distance)
        
        return fitness_results
    
    def select_parents(self, fitness_results):
        """Select parents for reproduction using tournament selection"""
        selection_results = []
        
        elite_indices = elitism_selection(fitness_results, self.elite_size)
        selection_results.extend(elite_indices)
        
        while len(selection_results) < self.population_size:
            selected_idx = tournament_selection(
                self.population, fitness_results, self.tournament_size)
            selection_results.append(selected_idx)
        
        selected_routes = [self.population[i] for i in selection_results]
        return selected_routes
    
    def crossover(self, parent1, parent2):
        """Cross parents to create a child (ordered crossover)"""
        if self.crossover_type == "cycle":
            return cycle_crossover(parent1, parent2)
        else:
            return ordered_crossover(parent1, parent2)
    
    def mutate(self, route):
        """Apply mutation to the route (swap mutation)"""
        if self.mutation_type == "insertion":
            return insertion_mutation(route, self.mutation_rate)
        elif self.mutation_type == "inversion":
            return inversion_mutation(route, self.mutation_rate)
        else:
            return swap_mutation(route, self.mutation_rate)
    
    def create_next_generation(self, selected_routes):
        """Create new generation from selected routes"""
        next_generation = []
        
        elites = selected_routes[:self.elite_size]
        next_generation.extend(elites)
        
        while len(next_generation) < self.population_size:
            parent1, parent2 = random.sample(selected_routes, 2)
            
            child = self.crossover(parent1, parent2)
            
            child = self.mutate(child)
            
            next_generation.append(child)
        
        self.population = next_generation
        self.generation += 1
        
        return self.population
    
    def run_generation(self):
        """Execute a complete generation of the genetic algorithm"""
        fitness_results = self.evaluate_population()
        selected_routes = self.select_parents(fitness_results)
        self.create_next_generation(selected_routes)
        
        return self.best_route, self.best_distance, self.generation