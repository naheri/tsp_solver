# tsp_solver/ui/main_window.py
import sys
import random
import time
import threading
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QSpinBox, 
                            QDoubleSpinBox, QGroupBox, QGridLayout, QStatusBar,
                            QComboBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject

from ..core.city import City
from ..genetic.algorithm import GeneticAlgorithm
from .canvas import MatplotlibCanvas

class SignalEmitter(QObject):
    """Class for emitting signals between threads"""
    update_signal = pyqtSignal()
    generation_signal = pyqtSignal(int, float)

class TSPWindow(QMainWindow):
    """Main window of the application"""
    
    def __init__(self):
        """Initialize the main window"""
        super().__init__()
        
        # Window configuration
        self.setWindowTitle("Genetic Algorithm - Traveling Salesman Problem")
        self.setGeometry(100, 100, 1200, 800)
        
        # Variables for the algorithm
        self.cities = []
        self.genetic_algo = None
        self.is_running = False
        self.thread = None
        
        # Create signals for thread communication
        self.signal_emitter = SignalEmitter()
        self.signal_emitter.update_signal.connect(self.update_plots)
        self.signal_emitter.generation_signal.connect(self.update_generation_info)
        
        # Create the user interface
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Group for algorithm parameters
        param_group = QGroupBox("Algorithm Parameters")
        param_layout = QGridLayout()
        param_group.setLayout(param_layout)
        
        # Number of cities
        param_layout.addWidget(QLabel("Number of cities:"), 0, 0)
        self.city_count = QSpinBox()
        self.city_count.setRange(5, 200)
        self.city_count.setValue(30)
        param_layout.addWidget(self.city_count, 0, 1)
        
        # Population size
        param_layout.addWidget(QLabel("Population size:"), 0, 2)
        self.population_size = QSpinBox()
        self.population_size.setRange(10, 1000)
        self.population_size.setValue(100)
        param_layout.addWidget(self.population_size, 0, 3)
        
        # Mutation rate
        param_layout.addWidget(QLabel("Mutation rate:"), 0, 4)
        self.mutation_rate = QDoubleSpinBox()
        self.mutation_rate.setRange(0.001, 0.5)
        self.mutation_rate.setSingleStep(0.001)
        self.mutation_rate.setValue(0.01)
        self.mutation_rate.setDecimals(3)
        param_layout.addWidget(self.mutation_rate, 0, 5)
        
        # Elite size
        param_layout.addWidget(QLabel("Elite size:"), 1, 0)
        self.elite_size = QSpinBox()
        self.elite_size.setRange(1, 100)
        self.elite_size.setValue(20)
        param_layout.addWidget(self.elite_size, 1, 1)
        
        # Tournament size
        param_layout.addWidget(QLabel("Tournament size:"), 1, 2)
        self.tournament_size = QSpinBox()
        self.tournament_size.setRange(2, 20)
        self.tournament_size.setValue(5)
        param_layout.addWidget(self.tournament_size, 1, 3)
        
        # Crossover type
        param_layout.addWidget(QLabel("Crossover type:"), 1, 4)
        self.crossover_type = QComboBox()
        self.crossover_type.addItems(["ordered", "cycle"])
        param_layout.addWidget(self.crossover_type, 1, 5)
        
        # Mutation type
        param_layout.addWidget(QLabel("Mutation type:"), 2, 0)
        self.mutation_type = QComboBox()
        self.mutation_type.addItems(["swap", "insertion", "inversion"])
        param_layout.addWidget(self.mutation_type, 2, 1)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("Generate Cities")
        self.generate_button.clicked.connect(self.generate_cities)
        button_layout.addWidget(self.generate_button)
        
        self.start_button = QPushButton("Start Algorithm")
        self.start_button.clicked.connect(self.toggle_algorithm)
        self.start_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        
        self.step_button = QPushButton("Step by Step")
        self.step_button.clicked.connect(self.run_step)
        self.step_button.setEnabled(False)
        button_layout.addWidget(self.step_button)
        
        # Group for information
        info_group = QGroupBox("Information")
        info_layout = QHBoxLayout()
        info_group.setLayout(info_layout)
        
        # Current generation
        info_layout.addWidget(QLabel("Generation:"))
        self.generation_label = QLabel("0")
        info_layout.addWidget(self.generation_label)
        
        # Best distance
        info_layout.addWidget(QLabel("Best distance:"))
        self.distance_label = QLabel("N/A")
        info_layout.addWidget(self.distance_label)
        
        info_layout.addStretch()
        
        # Matplotlib canvas
        self.canvas = MatplotlibCanvas(self, width=10, height=6)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Assemble the main layout
        main_layout.addWidget(param_group)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(info_group)
        main_layout.addWidget(self.canvas)
    
    def generate_cities(self):
        """Generate N random cities"""
        try:
            n_cities = self.city_count.value()
            if n_cities < 3:
                n_cities = 3  # Minimum 3 cities for a valid problem
                self.city_count.setValue(3)
                
            # Stop the algorithm if running
            self.stop_algorithm()
            
            # Generate random cities in a 2D space
            self.cities = []
            for i in range(n_cities):
                x = random.uniform(0, 100)
                y = random.uniform(0, 100)
                self.cities.append(City(x, y, f"City-{i+1}"))
            
            # Initialize the genetic algorithm
            pop_size = self.population_size.value()
            elite = self.elite_size.value()
            mutation = self.mutation_rate.value()
            tournament = self.tournament_size.value()
            crossover = self.crossover_type.currentText()
            mutation_type = self.mutation_type.currentText()
            
            self.genetic_algo = GeneticAlgorithm(
                self.cities, 
                population_size=pop_size,
                elite_size=elite,
                mutation_rate=mutation,
                tournament_size=tournament,
                crossover_type=crossover,
                mutation_type=mutation_type
            )
            
            # Create the initial population
            self.genetic_algo.create_initial_population()
            
            # Update plots
            self.update_plots()
            
            # Enable buttons
            self.start_button.setEnabled(True)
            self.start_button.setText("Start Algorithm")
            self.step_button.setEnabled(True)
            
            # Reset labels
            self.generation_label.setText("0")
            self.distance_label.setText("N/A")
            
            self.statusBar.showMessage(f"{n_cities} random cities generated")
            
        except Exception as e:
            self.statusBar.showMessage(f"Error: {str(e)}")
    
    def toggle_algorithm(self):
        """Start or stop the genetic algorithm"""
        if self.is_running:
            self.stop_algorithm()
        else:
            self.start_algorithm()
    
    def start_algorithm(self):
        """Start the genetic algorithm in a separate thread"""
        if not self.is_running and self.genetic_algo:
            self.is_running = True
            self.start_button.setText("Stop Algorithm")
            self.generate_button.setEnabled(False)
            self.step_button.setEnabled(False)
            
            # Run the algorithm in a thread to avoid blocking the UI
            self.thread = threading.Thread(target=self.run_algorithm)
            self.thread.daemon = True
            self.thread.start()
            
            self.statusBar.showMessage("Algorithm running...")
    
    def stop_algorithm(self):
        """Stop the genetic algorithm"""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(0.1)  # Wait for the thread to finish
        
        self.start_button.setText("Start Algorithm")
        self.generate_button.setEnabled(True)
        self.step_button.setEnabled(True)
        
        if self.genetic_algo:
            self.statusBar.showMessage(f"Algorithm stopped at generation {self.genetic_algo.generation}")
    
    def run_algorithm(self):
        """Run the genetic algorithm until stopped"""
        while self.is_running:
            # Execute one generation
            best_route, best_distance, generation = self.genetic_algo.run_generation()
            
            # Emit a signal to update the UI
            self.signal_emitter.generation_signal.emit(generation, best_distance)
            # Update plots periodically
            if generation % 5 == 0 or generation < 10:
                self.signal_emitter.update_signal.emit()
            
            # Small delay to avoid overloading the UI
            time.sleep(0.05)
    
    def run_step(self):
        """Execute one step (generation) of the genetic algorithm"""
        if self.genetic_algo:
            # Execute one generation
            best_route, best_distance, generation = self.genetic_algo.run_generation()
            
            # Update labels
            self.generation_label.setText(str(generation))
            self.distance_label.setText(f"{best_distance:.2f}")
            
            # Update plots
            self.update_plots()
            
            self.statusBar.showMessage(f"Generation {generation} completed")
    
    def update_generation_info(self, generation, distance):
        """Update generation information (called from another thread)"""
        self.generation_label.setText(str(generation))
        self.distance_label.setText(f"{distance:.2f}")
    
    def update_plots(self):
        """Update plots with current data"""
        if not self.genetic_algo:
            return
        
        # Clear plots
        self.canvas.axes1.clear()
        self.canvas.axes2.clear()
        
        # Configure titles and legends
        self.canvas.axes1.set_title("Traveling Salesman Problem")
        self.canvas.axes1.set_xlabel("X")
        self.canvas.axes1.set_ylabel("Y")
        self.canvas.axes1.grid(True)
        
        self.canvas.axes2.set_title("Distance Evolution")
        self.canvas.axes2.set_xlabel("Generation")
        self.canvas.axes2.set_ylabel("Distance")
        self.canvas.axes2.grid(True)
        
        # Plot cities
        x = [city.x for city in self.cities]
        y = [city.y for city in self.cities]
        self.canvas.axes1.scatter(x, y, c='blue', marker='o')
        
        # Add city labels
        for city in self.cities:
            self.canvas.axes1.annotate(city.name, (city.x, city.y), fontsize=8)
        
        # Plot the best route if it exists
        if self.genetic_algo.best_route:
            best_route = self.genetic_algo.best_route
            
            # Plot connections between cities
            for i in range(len(best_route)):
                city1 = best_route[i]
                city2 = best_route[(i + 1) % len(best_route)]
                self.canvas.axes1.plot([city1.x, city2.x], [city1.y, city2.y], 'r-', alpha=0.7)
        
        # Plot distance evolution
        history = self.genetic_algo.history
        if history:
            generations = list(range(len(history)))
            self.canvas.axes2.plot(generations, history, 'g-')
            
            # Logarithmic scale if there is a lot of data
            if len(history) > 50 and max(history) / min(history) > 10:
                self.canvas.axes2.set_yscale('log')
        
        # Refresh the canvas
        self.canvas.draw()
    
    def closeEvent(self, event):
        """Handle window closing"""
        self.stop_algorithm()
        event.accept()