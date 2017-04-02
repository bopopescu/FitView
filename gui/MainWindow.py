'''
Created on 9 Mar 2017

@author: Christopher Kreitz
'''


from PyQt5.QtWidgets import QApplication, QMainWindow, QAction
from PyQt5.QtWidgets import qApp, QFileDialog,QWidget
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem,QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings
from gui.GraphWidget import GraphWidget
#import seaborn as sns
import logging

from logbook import Logbook
from gui.mainwindow_ui import Ui_MainWindow
            
class Application(QMainWindow, Ui_MainWindow):
    def __init__(self):

        # Variables
        self._logbook = None
        self._event_table = []
        self.logging = logging.getLogger(__name__)

        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        
        #UI Settings
        self.setupUi(self)
        
        self.actionExit.triggered.connect(qApp.quit)
        self.actionNew_Logbook.triggered.connect(self.new_logbook)
        self.actionOpen_Logbook.triggered.connect(self.open_logbook)
        self.actionImport_File.triggered.connect(self.import_files)
        self.actionSync_with_Garmin.triggered.connect(self.import_files)  

        self.selectAction = QComboBox()
        self.selectAction.insertItems(1,["One","Two","Three"])
        self.toolBar.addWidget(self.selectAction)

#        self.action_Import_Files.triggered.connect(self.import_files)
#        self.action_Import_Files.setEnabled(False)
#        self.setWindowTitle("GView")
#        self.action_Open_Logbook.triggered.connect(self.open_logbook)
#        self.action_New_Logbook.triggered.connect(self.new_logbook)
#        self.action_Close_Logbook.triggered.connect(self.close_logbook)
        self.all_events_table.itemSelectionChanged.connect(self._selection_changed)
        self.all_events_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.all_events_table.hideColumn(4)
        self.graphwidget=GraphWidget(self.graph)

        self.all_events_table.setSortingEnabled(True)

        self.actionSync_with_Garmin.setDisabled(True)
        self.actionImport_File.setDisabled(True)
        
        self.settings = QSettings("MyCompany", "FitView")
        if not self.settings.value("geometry") == None:
            self.restoreGeometry(self.settings.value("geometry"))
        if not self.settings.value("windowState") == None:
            self.restoreState(self.settings.value("windowState"))
            
#        self.graphwidget.update_figure(data=None)
        
    def _selection_changed(self):
        indexes = []
        for selectionRange in self.all_events_table.selectedRanges():
            row = int(self.all_events_table.item(selectionRange.topRow(),4).text())
            indexes.append(row)
        
        logging.info("Line %s selected"%indexes[0])
        self.metadataStackedWidget.setCurrentIndex(indexes[0])
        
        self.graphwidget.update_figure(data=self._logbook[self._event_table[indexes[0]]],title="Bar")

    def import_files(self):
        options = QFileDialog.Options()
        file_names, _ = QFileDialog.getOpenFileNames(self,"Open File", "","FIT file (*.FIT)", options=options)
        
        if file_names:
            if self._logbook.import_files(file_names):
                logging.info("Import successful")
            else:
                logging.info("Import unsuccessful")
                self.logging.info("Invalid File")
        self.load_tablewidget_data()
                      
    def open_logbook(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"Open Logbook", "","Garmin Logbook file (*.gl)", options=options)
        if fileName:
            self._logbook = Logbook(fileName)
            self.setWindowTitle("GView - " + fileName)
        self.load_tablewidget_data()

    def new_logbook(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"Open Logbook", "","Garmin Logbook file (*.gl)", options=options)
        if fileName:
            self._logbook = Logbook(fileName)
            self.setWindowTitle("GView - " + fileName)
            self.load_tablewidget_data()
    
    def close_logbook(self):
        if self._logbook:
            self._logbook.close_logbook()
        self.setWindowTitle("GView ")
        self.load_tablewidget_data(unload_data=True)
                
    def load_tablewidget_data(self,unload_data = False):
        if unload_data:
            self.action_Import_Files.setEnabled(False)
            self.all_events_table.setRowCount(0)
            self._event_table = []            
        else:
            if self._logbook:
#                self.action_Import_Files.setEnabled(True)
                self.actionSync_with_Garmin.setEnabled(True)
                self.actionImport_File.setEnabled(True)
                self._event_table = self._logbook.events

                self.all_events_table.setRowCount(len(self._event_table))
        
                i=0
                for ev in self._event_table:
                    self.all_events_table.setItem(i,0, QTableWidgetItem(str(ev.date)))
                    self.all_events_table.setItem(i,1, QTableWidgetItem(ev.name))
                    self.all_events_table.setItem(i,2, QTableWidgetItem(ev.maintype))
                    self.all_events_table.setItem(i,3, QTableWidgetItem(ev.subtype))
                    self.all_events_table.setItem(i,4, QTableWidgetItem(str(i)))
#                    tmp = QWidget()
#                    tmp.setLayout(ev.ui)
#                    self.metadataStackedWidget.insertWidget(i,tmp)
                    i+=1
            
            self.graphwidget.update_figure()
        
    def edit_event(self):
        pass
        
    def delete_event(self,test):
        print(self.all_events_table.currentColumn())        
    
    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        QMainWindow.closeEvent(self, event)
                
