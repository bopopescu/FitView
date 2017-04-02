from yapsy.IPlugin import IPlugin
from logbook.Importer import Plugin
from messages import TimeSeriesData,TimeSeriesMetaData,LogMetaData,UIData
import logging
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QFormLayout, QLineEdit

class Default(IPlugin,Plugin):
    def __init__(self,log_name=None,metadata=None):
        self._actions=['import']
        self._type=['default']
        self.logging = logging.getLogger(__name__)
        self._filename = log_name 
        self._formdata = None
        self._metadata = None
        self._data = None
        
        if metadata:
            self._metadata = LogMetaData(file_hash=metadata.file_hash,
                                 date=metadata.creation_date,
                                 name=metadata.event_name,
                                 maintype=metadata.event_type,
                                 subtype=metadata.event_subtype
                                 )
        self.open_logbook(self._filename)

    def open_logbook(self,filename):
        self._filename = filename
        
    def import_fit(self,fitfile=None):
        pass
    
    def get_data(self,event):
        self._data = [TimeSeriesData(name="dummy" ,labels=[],data=[],unit=None)]
        
    @property
    def ui(self):
        layout = QFormLayout()
        labels=[]
        fields=[]
        if self._formdata:
            for i in range(len(self._formdata)):
                labels.append(QLabel(self._formdata[i].name+" ("+self._formdata[i].unit+")"))
                fields.append(QLineEdit(str(self._formdata[i].value)))
                layout.addRow(labels[-1], 
                              fields[-1]
                              )
                
        return UIData(ui=layout,labels=labels,fields=fields)
    
    @property
    def metadata(self):
        return self._metadata
    
    @property
    def data(self):
        return self._data 
