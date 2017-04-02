from gui.graphwidget_ui import Ui_GraphLayout
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from gui.MplCanvas import MatPlotLibCanvas
from PyQt5 import QtWidgets

class GraphWidget(Ui_GraphLayout):
    
    def __init__(self,parent=None):
        
        Ui_GraphLayout.__init__(parent)
        self.setupUi(parent)
        
        self.canvas=MatPlotLibCanvas(self.graph,dpi=100)
        
        self.canvas_toolbar = NavigationToolbar(self.canvas,self.menu)
        
        self.canvas_vertical_layout = QtWidgets.QVBoxLayout(self.graph)
        self.canvas_vertical_layout.addWidget(self.canvas)
        
        
    def update_figure(self, data = None,title="Dummy"):
        self.canvas.update_figure(data,title)