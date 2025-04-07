from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MatplotlibCanvas(FigureCanvas):
    """Class for creating a Matplotlib canvas integrated with PyQt"""
    
    def __init__(self, parent=None, width=10, height=6, dpi=100):
        """
        Initialize the Matplotlib canvas.
        
        Args:
            parent: Parent widget
            width (float): Canvas width
            height (float): Canvas height
            dpi (int): Canvas resolution
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes1 = self.fig.add_subplot(121)  # cities and the path
        self.axes2 = self.fig.add_subplot(122)  # the evolution of the distance
        
        super(MatplotlibCanvas, self).__init__(self.fig)
        
        # Initial configuration
        self.axes1.set_title("Traveling Salesman Problem")
        self.axes1.set_xlabel("X")
        self.axes1.set_ylabel("Y")
        self.axes1.grid(True)
        
        self.axes2.set_title("Evolution of the distance")
        self.axes2.set_xlabel("Generation")
        self.axes2.set_ylabel("Distance")
        self.axes2.grid(True)