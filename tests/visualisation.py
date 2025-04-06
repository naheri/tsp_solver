import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class TestResultsVisualizer:
    def __init__(self, results_df):
        self.df = results_df
        
    def plot_convergence_comparison(self, save_path=None):
        plt.figure(figsize=(12, 8))
        
        for city_size in self.df['city_size'].unique():
            best_config = self.df[self.df['city_size'] == city_size].iloc[0]
            plt.plot(best_config['convergence_history'], 
                    label=f'{city_size} cities')
        
        plt.xlabel('Generation')
        plt.ylabel('Best Distance')
        plt.title('Convergence Comparison by Problem Size')
        plt.legend()
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path)
        plt.show()
    
    def plot_population_ratio_impact(self, save_path=None):
        plt.figure(figsize=(12, 8))
        
        sns.boxplot(data=self.df, x='population_ratio', 
                   y='avg_stagnation_gen', hue='city_size')
        
        plt.xlabel('Population Ratio (n)')
        plt.ylabel('Generation of Stagnation')
        plt.title('Impact of Population Ratio on Convergence Speed')
        
        if save_path:
            plt.savefig(save_path)
        plt.show()
    
    def create_summary_tables(self):
        """Crée des tableaux récapitulatifs"""
        
        best_configs = self.df.loc[self.df.groupby('city_size')['avg_best_distance'].idxmin()]
        operator_performance = self.df.groupby(['crossover_type', 'mutation_type'])\
            .agg({
                'avg_best_distance': 'mean',
                'avg_execution_time': 'mean',
                'avg_stagnation_gen': 'mean'
            }).round(2)
        
        return best_configs, operator_performance
    def create_comparison_table(self):
        """Crée un tableau comparatif formaté avec Pandas"""
        comparison = pd.pivot_table(
            self.df,
            values=['avg_best_distance', 'avg_execution_time', 'avg_stagnation_gen'],
            index=['city_size', 'population_ratio'],
            columns=['crossover_type', 'mutation_type'],
            aggfunc='mean'
        )
        
        # tableau format
        styled_comparison = comparison.style\
            .background_gradient(cmap='RdYlGn_r', subset=['avg_best_distance'])\
            .background_gradient(cmap='RdYlGn', subset=['avg_execution_time'])\
            .format({
                'avg_best_distance': '{:.2f}',
                'avg_execution_time': '{:.2f}s',
                'avg_stagnation_gen': '{:.0f}'
            })
        
        return styled_comparison