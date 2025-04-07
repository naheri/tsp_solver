# tsp_solver/ui/main_window.py
import sys
import random
import time
import threading
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QSpinBox, 
                            QDoubleSpinBox, QGroupBox, QGridLayout, QStatusBar,
                            QComboBox, QFileDialog, QCheckBox)
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
        

        self.setWindowTitle("Genetic Algorithm - Traveling Salesman Problem")
        self.setGeometry(100, 100, 1200, 800)
        
        self.cities = []
        self.genetic_algo = None
        self.is_running = False
        self.thread = None
        
        # signals for thread communication
        self.signal_emitter = SignalEmitter()
        self.signal_emitter.update_signal.connect(self.update_plots)
        self.signal_emitter.generation_signal.connect(self.update_generation_info)
        
        # Create the user interface
        self.init_ui()
    
    def init_ui(self):
        """
        Initialize the user interface
        """
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
    
        main_layout = QVBoxLayout(central_widget)
        
        param_group = QGroupBox("Algorithm Parameters")
        param_layout = QGridLayout()
        param_group.setLayout(param_layout)
        
        param_layout.addWidget(QLabel("Number of cities:"), 0, 0)
        self.city_count = QSpinBox()
        self.city_count.setRange(5, 200)
        self.city_count.setValue(30)
        param_layout.addWidget(self.city_count, 0, 1)
        
        param_layout.addWidget(QLabel("Population size:"), 0, 2)
        self.population_size = QSpinBox()
        self.population_size.setRange(10, 1000)
        self.population_size.setValue(100)
        param_layout.addWidget(self.population_size, 0, 3)
        
        param_layout.addWidget(QLabel("Mutation rate:"), 0, 4)
        self.mutation_rate = QDoubleSpinBox()
        self.mutation_rate.setRange(0.001, 0.5)
        self.mutation_rate.setSingleStep(0.001)
        self.mutation_rate.setValue(0.01)
        self.mutation_rate.setDecimals(3)
        param_layout.addWidget(self.mutation_rate, 0, 5)
        
        param_layout.addWidget(QLabel("Elite size:"), 1, 0)
        self.elite_size = QSpinBox()
        self.elite_size.setRange(1, 100)
        self.elite_size.setValue(20)
        param_layout.addWidget(self.elite_size, 1, 1)
      
        param_layout.addWidget(QLabel("Tournament size:"), 1, 2)
        self.tournament_size = QSpinBox()
        self.tournament_size.setRange(2, 20)
        self.tournament_size.setValue(5)
        param_layout.addWidget(self.tournament_size, 1, 3)
        

        param_layout.addWidget(QLabel("Crossover type:"), 1, 4)
        self.crossover_type = QComboBox()
        self.crossover_type.addItems(["ordered", "cycle"])
        param_layout.addWidget(self.crossover_type, 1, 5)
        
        param_layout.addWidget(QLabel("Mutation type:"), 2, 0)
        self.mutation_type = QComboBox()
        self.mutation_type.addItems(["swap", "insertion", "inversion"])
        param_layout.addWidget(self.mutation_type, 2, 1)
        
        # Ajout des contrôles pour le critère d'arrêt
        self.use_stopping = QCheckBox("Use stopping criterion")
        param_layout.addWidget(self.use_stopping, 2, 2)
        
        param_layout.addWidget(QLabel("Min. improvement:"), 2, 3)
        self.improvement_threshold = QDoubleSpinBox()
        self.improvement_threshold.setRange(0.0001, 0.01)
        self.improvement_threshold.setSingleStep(0.0001)
        self.improvement_threshold.setValue(0.001)
        self.improvement_threshold.setDecimals(4)
        param_layout.addWidget(self.improvement_threshold, 2, 4)
        
        param_layout.addWidget(QLabel("Generations to check:"), 2, 5)
        self.generations_check = QSpinBox()
        self.generations_check.setRange(10, 100)
        self.generations_check.setValue(20)
        param_layout.addWidget(self.generations_check, 2, 6)
        
        button_layout = QHBoxLayout()
        
        self.import_button = QPushButton("Import TSPLIB")
        self.import_button.clicked.connect(self.import_tsplib)
        button_layout.addWidget(self.import_button)
        
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
    
        info_group = QGroupBox("Information")
        info_layout = QHBoxLayout()
        info_group.setLayout(info_layout)
        
        info_layout.addWidget(QLabel("Generation:"))
        self.generation_label = QLabel("0")
        info_layout.addWidget(self.generation_label)
        
        info_layout.addWidget(QLabel("Best distance:"))
        self.distance_label = QLabel("N/A")
        info_layout.addWidget(self.distance_label)
        
        info_layout.addStretch()
        
        self.canvas = MatplotlibCanvas(self, width=10, height=6)
        

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
                
            self.stop_algorithm()
            
            self.cities = []
            for i in range(n_cities):
                x = random.uniform(0, 100)
                y = random.uniform(0, 100)
                self.cities.append(City(x, y, f"City-{i+1}"))
            
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
                mutation_type=mutation_type,
                use_stopping_criterion=self.use_stopping.isChecked(),
                improvement_threshold=self.improvement_threshold.value(),
                generations_without_improvement=self.generations_check.value()
            )
            
            self.genetic_algo.create_initial_population()
            
            self.update_plots()
            
            self.start_button.setEnabled(True)
            self.start_button.setText("Start Algorithm")
            self.step_button.setEnabled(True)
            
            self.generation_label.setText("0")
            self.distance_label.setText("N/A")
            
            self.statusBar.showMessage(f"{n_cities} random cities generated")
            
        except Exception as e:
            self.statusBar.showMessage(f"Error: {str(e)}")
    
    def import_tsplib(self):
        """Import a TSPLIB instance"""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Open TSPLIB File",
                "",
                "TSPLIB Files (*.tsp);;All Files (*)"
            )
            
            if filename:
                # Stop the algorithm if running
                self.stop_algorithm()
                
                # Read the TSPLIB file
                self.cities = []
                with open(filename, 'r') as file:
                    dimension = 0
                    coords_started = False
                    
                    for line in file:
                        line = line.strip()
                        if line.startswith("DIMENSION"):
                            dimension = int(line.split(":")[-1])
                        elif line == "NODE_COORD_SECTION":
                            coords_started = True
                        elif coords_started and line != "EOF":
                            # Parse coordinates
                            parts = line.split()
                            if len(parts) >= 3:
                                idx = int(parts[0])
                                x = float(parts[1])
                                y = float(parts[2])
                                self.cities.append(City(x, y, f"City-{idx}"))
                
                self.city_count.setValue(len(self.cities))
                
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
                    mutation_type=mutation_type,
                    use_stopping_criterion=self.use_stopping.isChecked(),
                    improvement_threshold=self.improvement_threshold.value(),
                    generations_without_improvement=self.generations_check.value()
                )
                
                self.genetic_algo.create_initial_population()
                self.update_plots()
                
                self.start_button.setEnabled(True)
                self.start_button.setText("Start Algorithm")
                self.step_button.setEnabled(True)
                
                # Reset labels
                self.generation_label.setText("0")
                self.distance_label.setText("N/A")
                
                self.statusBar.showMessage(f"Imported {len(self.cities)} cities from TSPLIB file")
            
        except Exception as e:
            self.statusBar.showMessage(f"Error importing TSPLIB file: {str(e)}")
    
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
            best_route, best_distance, generation, should_stop = self.genetic_algo.run_generation()
            self.signal_emitter.generation_signal.emit(generation, best_distance)
            
            if generation % 5 == 0 or generation < 10:
                self.signal_emitter.update_signal.emit()
            
            if should_stop:
                self.stop_algorithm()
                self.statusBar.showMessage(f"Algorithm stopped: no significant improvement after {self.generations_check.value()} generations")
                break
            
            time.sleep(0.05)
    
    def run_step(self):
        """Execute one step (generation) of the genetic algorithm"""
        if self.genetic_algo:
            best_route, best_distance, generation, should_stop = self.genetic_algo.run_generation()
            self.generation_label.setText(str(generation))
            self.distance_label.setText(f"{best_distance:.2f}")
            
            self.update_plots()
            
            if should_stop:
                self.statusBar.showMessage(f"Suggested to stop: no significant improvement after {self.generations_check.value()} generations")
            
            self.statusBar.showMessage(f"Generation {generation} completed")
    
    def update_generation_info(self, generation, distance):
        """Update generation information (called from another thread)"""
        self.generation_label.setText(str(generation))
        self.distance_label.setText(f"{distance:.2f}")
    
    def update_plots(self):
        """Update plots with current data"""
        if not self.genetic_algo:
            return
        
        self.canvas.axes1.clear()
        self.canvas.axes2.clear()
        
        self.canvas.axes1.set_title("Traveling Salesman Problem")
        self.canvas.axes1.set_xlabel("X")
        self.canvas.axes1.set_ylabel("Y")
        self.canvas.axes1.grid(True)
        
        self.canvas.axes2.set_title("Distance Evolution")
        self.canvas.axes2.set_xlabel("Generation")
        self.canvas.axes2.set_ylabel("Distance")
        self.canvas.axes2.grid(True)
        
        x = [city.x for city in self.cities]
        y = [city.y for city in self.cities]
        self.canvas.axes1.scatter(x, y, c='blue', marker='o')
        
        for city in self.cities:
            self.canvas.axes1.annotate(city.name, (city.x, city.y), fontsize=8)
        
        # plot best route if available
        if self.genetic_algo.best_route:  
            best_route = self.genetic_algo.best_route
            for i in range(len(best_route)):
                city1 = best_route[i]
                city2 = best_route[(i + 1) % len(best_route)]
                self.canvas.axes1.plot([city1.x, city2.x], [city1.y, city2.y], 'r-', alpha=0.7)
        
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