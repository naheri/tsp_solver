import random
import numpy as np

class City:
    def __init__(self, x, y, name=None):
        self.x = x
        self.y = y
        self.name = name if name else f"Ville-{random.randint(1, 100)}"
    
    def distance(self, city):
        return np.sqrt((self.x - city.x) ** 2 + (self.y - city.y) ** 2)
    
    def __repr__(self):
        return f"{self.name}({self.x},{self.y})"