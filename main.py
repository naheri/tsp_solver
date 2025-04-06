#!/usr/bin/env python3
# main.py
"""
Traveling Salesman Problem (TSP) with Genetic Algorithm
-------------------------------------------------------------------
This program solves the traveling salesman problem using
a genetic algorithm with a PyQt5 graphical interface.
"""

import sys
from PyQt5.QtWidgets import QApplication
from tsp_solver.ui import TSPWindow

def main():
    """Main entry point of the application"""
    app = QApplication(sys.argv)
    
    # Apply a modern style
    app.setStyle("Breeze")
    
    window = TSPWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()