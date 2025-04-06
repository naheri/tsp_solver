from tests.test_bench import TSPTestBench
from tests.visualisation import TestResultsVisualizer
import pandas as pd
import numpy as np
import os

def main():
    os.makedirs('test_results', exist_ok=True)
    
    test_bench = TSPTestBench()
    test_bench.run_benchmark()
    
    results_df, summary_df = test_bench.save_results()
    
    visualizer = TestResultsVisualizer(results_df)
    
    visualizer.plot_convergence_comparison('test_results/convergence_comparison.png')
    visualizer.plot_population_ratio_impact('test_results/population_ratio_impact.png')
    
    best_configs, operator_performance = visualizer.create_summary_tables()

    best_configs.to_csv('test_results/best_configurations.csv')
    operator_performance.to_csv('test_results/operator_performance.csv')
   
    comparison_table = visualizer.create_comparison_table()
    
    
    comparison_table.to_html('test_results/comparison_table.html')
    
    with pd.ExcelWriter('test_results/tsp_results.xlsx') as writer:
        results_df.to_excel(writer, sheet_name='Detailed Results')
        best_configs.to_excel(writer, sheet_name='Best Configurations')
        operator_performance.to_excel(writer, sheet_name='Operator Performance')

if __name__ == "__main__":
    main()