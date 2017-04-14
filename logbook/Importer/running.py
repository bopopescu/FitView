from yapsy.IPlugin import IPlugin
from logbook.Importer import Plugin
from messages import TimeSeriesData,TimeSeriesMetaData,LogMetaData,UIData,TimeSeries
from sqlalchemy import *
import logging
from tools.profiling import timing
from PyQt5.QtWidgets import QLabel, QFormLayout, QLineEdit
#from PyQt5 import QtCore, QtGui, QtWidgets


class Running(IPlugin,Plugin):
    
    def __init__(self,log_name=None,metadata=None):
        self._actions=['import']
        self._type=['running']
        self.logging = logging.getLogger(__name__)
        self._filename = log_name
        
        if metadata:
            self._metadata = LogMetaData(file_hash=metadata.file_hash,
                                 date=metadata.creation_date,
                                 name=metadata.event_name,
                                 maintype=metadata.event_type,
                                 subtype=metadata.event_subtype
                                 )
        self._formdata = []
        self._formdata.append(TimeSeriesMetaData("Total Length",0,"m"))
        self._formdata.append(TimeSeriesMetaData("Time per 100m","%.1f" %0,"s"))
        self._formdata.append(TimeSeriesMetaData("average speed","%.1f" %0,"m/s"))
        self._formdata.append(TimeSeriesMetaData("Total calories",0,"kcal"))
        self._formdata.append(TimeSeriesMetaData("Event duration","%.1f" %0,"min"))
            
    @timing
    def open_logbook(self,filename):
        self._filename = filename
        self._alchemy_logbook = create_engine('sqlite:///'+self._filename)   
        _metadata = MetaData(bind=self._alchemy_logbook)
        
        self.file_table = Table('file', _metadata, autoload=True)
        self.running_table = Table("event_running",_metadata,
                                Column('event_running_id',Integer,primary_key=True),
                                Column('f_id',Integer,ForeignKey("file.file_id"), nullable=False),
                                Column('timestamp',DateTime),
                                Column('cadence',Integer),
                                Column('distance',Integer),
                                Column('enhanced_speed',Float),
                                Column('heart_rate',Integer),
                                Column('position_lat',Float),
                                Column('position_long',Float)
                                )
        self.running_table.create(checkfirst=True)

    @timing
    def import_fit(self,fitfile=None):
        stmt = self.file_table.select(self.file_table.c.file_hash==fitfile.digest)
        row = stmt.execute().fetchone()
        
        file_id = row.file_id
                
        for record in fitfile.get_messages(["record"]):
            timestamp = None
            cadence = None
            distance = None
            enhanced_speed = None
            heart_rate = None
            lat = None
            lon = None
            
            data = []
            
            for record_data in record:
                if record_data.name == "timestamp":
                    timestamp = record_data.value
                if record_data.name =="cadence":
                    cadence = record_data.value
                if record_data.name == "distance":
                    distance = record_data.value
                if record_data.name == "enhanced_speed":
                    enhanced_speed = record_data.value
                if record_data.name == "heart_rate":
                    heart_rate = record_data.value
                if record_data.name == "position_lat":
                    lat = record_data.value*(180.0/2**31)
                if record_data.name == "position_long":
                    lon = record_data.value*(180.0/2**31)
                    
            data.append({'f_id':file_id,'timestamp':timestamp,
                         'cadence':cadence,'distance':distance,
                         'enhanced_speed':enhanced_speed,'heart_rate':heart_rate,
                         'position_lat':lat,'position_long':lon})
            

            self._alchemy_logbook.execute(self.running_table.insert(),data)

    @timing
    def get_data(self,filehash):
        
        s = self.running_table.join(self.file_table).\
        select().where(self.file_table.c.file_hash==filehash)

        cadence    = TimeSeriesData(name="cadence"   ,labels=[],data=[],unit='rpm',xlabel="duration(min)")
        distance   = TimeSeriesData(name="distance"  ,labels=[],data=[],unit='m',xlabel="duration(min)")
        heart_rate = TimeSeriesData(name="heart_rate",labels=[],data=[],unit="bpm",xlabel="duration(min)")
        speed      = TimeSeriesData(name="speed"     ,labels=[],data=[],unit="m/s",xlabel="duration(min)")
        
        rows = 0
        abs_len = 0
        last_ts = 0

        row = None
               
        for row in self._alchemy_logbook.execute(s):
            if row.cadence and row.distance and row.enhanced_speed and row.heart_rate:
                rows = rows + 1
                
                if last_ts == 0:
                    last_ts = row.timestamp

                ts =  ((row.timestamp-last_ts).seconds/60)

                
                cadence.data.append(row.cadence)
                cadence.labels.append(ts)
                
                distance.data.append(row.distance-abs_len)
                abs_len = row.distance
                distance.labels.append(ts)
                
                heart_rate.data.append(row.heart_rate)
                heart_rate.labels.append(ts)
                
                speed.data.append(row.enhanced_speed)
                speed.labels.append(ts)
            
        if row:
            data = [cadence,distance,heart_rate,speed]
    
            formdata = []
    
            formdata.append(TimeSeriesMetaData("Total Length",row.distance,"m"))
            formdata.append(TimeSeriesMetaData("Time per 100m","%.1f" %1,"s"))
            formdata.append(TimeSeriesMetaData("average speed","%.1f" %(1/1),"m/s"))
            formdata.append(TimeSeriesMetaData("Total calories",1,"kcal"))
            formdata.append(TimeSeriesMetaData("Event duration","%.1f" %(1),"min"))
            
        return TimeSeries(data=data,metadata=formdata)

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
