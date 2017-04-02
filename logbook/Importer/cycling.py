from yapsy.IPlugin import IPlugin
from logbook.Importer import Plugin
from messages import TimeSeriesData,TimeSeriesMetaData,LogMetaData
from sqlalchemy import *
import logging
from tools.profiling import timing
from PyQt5.QtWidgets import QLabel, QFormLayout, QLineEdit
#from PyQt5 import QtCore, QtGui, QtWidgets


class Cycling(IPlugin,Plugin):
    
    def __init__(self,log_name=None,metadata=None):
        self._actions=['import']
        self._type=['cycling']
        self.logging = logging.getLogger(__name__)
        self._filename = log_name
        self._formdata = None
        self._data = None
        self._metadata = None
        self.labels=[]
        self.lineedits = []
        
        if metadata:
            self._metadata = LogMetaData(file_hash=metadata.file_hash,
                                 date=metadata.creation_date,
                                 name=metadata.event_name,
                                 maintype=metadata.event_type,
                                 subtype=metadata.event_subtype
                                 )

    def open_logbook(self,filename):
        self._filename = filename
        self._alchemy_logbook = create_engine('sqlite:///'+self._filename)   
        _metadata = MetaData(bind=self._alchemy_logbook)
        
        self.file_table = Table('file', _metadata, autoload=True)
        self.cycling_table = Table("event_cycling",_metadata,
                                Column('event_cycling_id',Integer,primary_key=True),
                                Column('f_id',Integer,ForeignKey("file.file_id"), nullable=False),
                                Column('timestamp',DateTime),
                                Column('distance',Integer),
                                Column('enhanced_altitude',Float),
                                Column('heart_rate',Integer)
                                )
        self.cycling_table.create(checkfirst=True)

    @timing
    def import_fit(self,fitfile=None):
        stmt = self.file_table.select(self.file_table.c.file_hash==fitfile.digest)
        row = stmt.execute().fetchone()
        
        file_id = row.file_id
                
        for record in fitfile.get_messages(["record"]):
            timestamp = None
            cadence = None
            distance = None
            enhanced_altitude = None
            heart_rate = None
            
            data = []
            
            for record_data in record:
                if record_data.name == "timestamp":
                    timestamp = record_data.value
                if record_data.name == "distance":
                    distance = record_data.value
                if record_data.name == "enhanced_altitude":
                    enhanced_altitude = record_data.value
                if record_data.name == "heart_rate":
                    heart_rate = record_data.value
                    
            data.append({'f_id':file_id,'timestamp':timestamp,
                         'distance':distance, 'enhanced_altitude':enhanced_altitude,
                         'heart_rate':heart_rate})
            

            self._alchemy_logbook.execute(self.cycling_table.insert(),data)

    @timing
    def get_data(self,filehash):
        
        s = self.cycling_table.join(self.file_table).\
        select().where(self.file_table.c.file_hash==filehash)

        distance          = TimeSeriesData(name="distance"         ,labels=[],data=[],unit='m')
        enhanced_altitude = TimeSeriesData(name="enhanced_altitude",labels=[],data=[],unit='m')
        heart_rate        = TimeSeriesData(name="heart_rate"       ,labels=[],data=[],unit="bpm")
#        speed             = TimeSeriesData(name="speed"            ,labels=[],data=[],unit="m/s")
        
        rows = 0
        abs_len = 0
        last_ts = 0

        row = None
               
        for row in self._alchemy_logbook.execute(s):
            rows = rows + 1
            
            if last_ts == 0:
                last_ts = row.timestamp

            ts =  ((row.timestamp-last_ts).seconds/60)

            
            enhanced_altitude.data.append(row.enhanced_altitude)
            enhanced_altitude.labels.append(ts)
            
            distance.data.append(row.distance-abs_len)
            abs_len = row.distance
            distance.labels.append(ts)
            
            heart_rate.data.append(row.heart_rate)
            heart_rate.labels.append(ts)
            
        if row:
            self._data = [enhanced_altitude,distance,heart_rate]
            self._formdata = []
    
            self._formdata.append(TimeSeriesMetaData("Total Length",row.distance,"m"))
            self._formdata.append(TimeSeriesMetaData("Time per 100m","%.1f" %1,"s"))
            self._formdata.append(TimeSeriesMetaData("average speed","%.1f" %(1/1),"m/s"))
            self._formdata.append(TimeSeriesMetaData("Total calories",1,"kcal"))
            self._formdata.append(TimeSeriesMetaData("Event duration","%.1f" %(1),"min"))
        
        return self._data
    
    @property
    def ui(self):
#        logging.debug("Building cycling UI")
        layout = QFormLayout()
        self.labels=[]
        self.lineedits=[]
        if self._formdata:
            for i in range(len(self._formdata)):
                layout.addRow(QLabel(self._formdata[i].name+" ("+self._formdata[i].unit+")"), QLineEdit(str(self._formdata[i].value)))
        return layout
