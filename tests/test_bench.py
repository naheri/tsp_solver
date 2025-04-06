import time
import pandas as pd
import numpy as np
from datetime import datetime
from tsp_solver.core.city import City
from tsp_solver.genetic.algorithm import GeneticAlgorithm

class TSPTestBench:
    def __init__(self):
        self.results = []
        self.city_sizes = [10, 20, 30, 50]
        self.population_ratios = [5, 7, 10, 12, 15]
        self.crossover_types = ["ordered", "cycle"]
        self.mutation_types = ["swap", "insertion", "inversion"]
        self.num_runs = 5  # number of runs for each configuration, we will do an average
        
    def generate_cities(self, size):
        """Génère un ensemble de villes aléatoires"""
        return [City(np.random.uniform(0, 100), 
                    np.random.uniform(0, 100), 
                    f"City-{i+1}") for i in range(size)]
    
    def calculate_mutation_rate(self, num_cities):
        """Calcule le taux de mutation optimal"""
        return 1.0 / num_cities
    
    def check_stagnation(self, history, window=20, threshold=0.005):
        """Vérifie la stagnation de l'algorithme"""
        if len(history) < window:
            return False
        
        recent_history = history[-window:]
        initial_value = recent_history[0]
        improvement = (initial_value - min(recent_history)) / initial_value
        
        return improvement < threshold
    
    def run_test_configuration(self, cities, population_size, crossover_type, 
                             mutation_type, max_generations=1000):
        """Exécute une configuration de test"""
        start_time = time.time()
        
        ga = GeneticAlgorithm(
            cities=cities,
            population_size=population_size,
            mutation_rate=self.calculate_mutation_rate(len(cities)),
            crossover_type=crossover_type,
            mutation_type=mutation_type
        )
        
        ga.create_initial_population()
        stagnation_gen = 0
        best_distance = float('inf')
        
        for gen in range(max_generations):
            best_route, current_distance, _ = ga.run_generation()
            
            if current_distance < best_distance:
                best_distance = current_distance
            
            if self.check_stagnation(ga.history):
                stagnation_gen = gen
                break
        
        execution_time = time.time() - start_time
        
        return {
            'best_distance': best_distance,
            'execution_time': execution_time,
            'stagnation_generation': stagnation_gen,
            'final_generation': gen,
            'convergence_history': ga.history
        }

    def run_benchmark(self):
        """Exécute le benchmark complet"""
        for city_size in self.city_sizes:
            print(f"\nTesting with {city_size} cities...")
            
            for pop_ratio in self.population_ratios:
                population_size = pop_ratio * city_size
                
                for crossover in self.crossover_types:
                    for mutation in self.mutation_types:
                        print(f"Testing: pop={population_size}, "
                              f"crossover={crossover}, mutation={mutation}")
                        
                        # Exécute plusieurs tests pour cette configuration
                        config_results = []
                        for run in range(self.num_runs):
                            cities = self.generate_cities(city_size)
                            result = self.run_test_configuration(
                                cities, population_size, crossover, mutation)
                            config_results.append(result)
                        
                        # Calcule les statistiques moyennes
                        avg_results = {
                            'city_size': city_size,
                            'population_ratio': pop_ratio,
                            'population_size': population_size,
                            'crossover_type': crossover,
                            'mutation_type': mutation,
                            'avg_best_distance': np.mean([r['best_distance'] 
                                                        for r in config_results]),
                            'std_best_distance': np.std([r['best_distance'] 
                                                       for r in config_results]),
                            'avg_execution_time': np.mean([r['execution_time'] 
                                                         for r in config_results]),
                            'avg_stagnation_gen': np.mean([r['stagnation_generation'] 
                                                         for r in config_results])
                        }
                        
                        self.results.append(avg_results)
    
    def save_results(self, output_dir='test_results'):
        """Sauvegarde les résultats dans des fichiers"""
        # Crée un DataFrame avec les résultats
        df = pd.DataFrame(self.results)
        
        # Génère un timestamp pour le nom de fichier
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Sauvegarde les résultats détaillés
        df.to_csv(f'{output_dir}/detailed_results_{timestamp}.csv', index=False)
        
        # Génère et sauvegarde le tableau récapitulatif
        summary = df.groupby('city_size').apply(
            lambda x: x.loc[x['avg_best_distance'].idxmin()]
        ).reset_index(drop=True)
        
        summary.to_csv(f'{output_dir}/summary_{timestamp}.csv', index=False)
        
        return df, summary