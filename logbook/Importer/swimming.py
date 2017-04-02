from yapsy.IPlugin import IPlugin
from logbook.Importer import Plugin
from messages import TimeSeriesData,TimeSeriesMetaData,LogMetaData
from sqlalchemy import *
import logging
from tools.profiling import timing
from PyQt5.QtWidgets import QLabel, QFormLayout, QLineEdit
#from PyQt5 import QtCore, QtGui, QtWidgets


class Swimming(IPlugin,Plugin):
    
    def __init__(self,log_name=None,metadata=None):
        self._actions=['import']
        self._type=['swimming']
        self.logging = logging.getLogger(__name__)
        self._filename = log_name
        self._formdata = None
        self._data = None
        self._metadata = None
        self.labels=[]
        self.lineedits = []
        self.file_table = None
        
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
        self.swim_table = Table("event_swimming",_metadata,
                                Column('event_swimming_id',Integer,primary_key=True),
                                Column('f_id',Integer,ForeignKey("file.file_id"), nullable=False),
                                Column('event_timestamp',DateTime),
                                Column('start_time',DateTime),
                                Column('swim_stroke',String(30)),
                                Column('total_calories',Integer),
                                Column('total_elapsed_time',Float),
                                Column('total_strokes',Integer),
                                Column('distance',Integer)
                                )
        self.swim_table.create(checkfirst=True)

    @timing
    def import_fit(self,fitfile=None):
        print("Swimming is importing")
        stmt = self.file_table.select(self.file_table.c.file_hash==fitfile.digest)
        row = stmt.execute().fetchone()
        
        file_id = row.file_id
                
        for record in fitfile.get_messages(["length"]):
            event_timestamp = None
            start_time = None
            swim_stroke = None
            total_calories = None
            total_elapsed_time = None
            total_strokes = None
            distance=None
            
            data = []
            fields=0
            
            for record_data in record:
                if record_data.name == "timestamp":
                    event_timestamp = record_data.value
                    fields +=1
                if record_data.name =="start_time":
                    start_time = record_data.value
                    fields +=1
                if record_data.name == "swim_stroke":
                    swim_stroke = record_data.value
                    fields +=1
                if record_data.name == "total_calories":
                    total_calories = record_data.value
                    fields +=1
                if record_data.name == "total_strokes":
                    total_strokes = record_data.value
                    fields +=1
                if record_data.name == "total_elapsed_time":
                    total_elapsed_time = record_data.value
                    fields +=1
                    
            if fields == 6:
                data.append({'f_id':file_id,'event_timestamp':event_timestamp,
                             'start_time':start_time,'swim_stroke':swim_stroke,
                             'total_calories':total_calories,'total_elapsed_time':total_elapsed_time,
                             'total_strokes':total_strokes})
                
    
                self._alchemy_logbook.execute(self.swim_table.insert(),data)

        data=[]
        for record in fitfile.get_messages(["record"]):
            event_timestamp = None
            distance = None
            
            for record_data in record:
                if record_data.name == "timestamp":
                    event_timestamp = record_data.value
                if record_data.name == "distance":
                    distance = record_data.value
                    
            if event_timestamp and distance:
                data.append({'timestamp':event_timestamp,'distance':distance})

                stmt = self.swim_table.update().\
                where(self.swim_table.c.event_timestamp==bindparam('timestamp')).\
                values(distance=bindparam('distance'))
                self._alchemy_logbook.execute(stmt,data)

    @timing
    def get_data(self,filehash):
        
        s = self.swim_table.join(self.file_table).\
        select().where(self.file_table.c.file_hash==filehash)

        strokes_data  = TimeSeriesData(name="strokes" ,labels=[],data=[],unit=None)
        avg_strokes   = TimeSeriesData(name="avg strokes",labels=[],data=[],unit="Strokes/lap")
        calories_data = TimeSeriesData(name="calories",labels=[],data=[],unit=None)
        speed_data    = TimeSeriesData(name="speed"   ,labels=[],data=[],unit="min/100m")
        
        rows = 0
        total_calories = 0
        event_duration = 0

        strokes_data.data.append(0)
        strokes_data.labels.append(0)

        avg_strokes.data.append(0)
        avg_strokes.labels.append(0)
        
        calories_data.data.append(0)
        calories_data.labels.append(0)
        
        speed_data.data.append(0)
        speed_data.labels.append(0)

        stro = 0

        row = None
               
        for row in self._alchemy_logbook.execute(s):
            if row.total_strokes and row.distance and row.total_calories and row.total_elapsed_time:
                rows = rows + 1
                strokes_data.data.append(row.total_strokes)
                strokes_data.labels.append(row.distance)
                
                stro = stro + row.total_strokes
                
                avg_strokes.data.append((stro/row.distance)*50)
                avg_strokes.labels.append(row.distance)
                
                calories_data.data.append(row.total_calories)
                calories_data.labels.append(row.distance)
                
                speed_data.data.append(((row.total_elapsed_time/50)*100)/60) #FIXME
                speed_data.labels.append(row.distance)
                
                total_calories = total_calories + row.total_calories
                event_duration = event_duration + row.total_elapsed_time
            
        if row:
            lap_distance = int(row.distance / rows)
            total_length = row.distance
            total_time = row.start_time
            
            self._data = [strokes_data,calories_data,speed_data,avg_strokes]
            
            time_per_hundred = (100/lap_distance)*(event_duration/lap_distance)
    
            self._formdata = []
    
            self._formdata.append(TimeSeriesMetaData("Lap length",lap_distance,"m"))
            self._formdata.append(TimeSeriesMetaData("Total Length",total_length,"m"))
            self._formdata.append(TimeSeriesMetaData("Time per 100m","%.1f" %time_per_hundred,"s"))
            self._formdata.append(TimeSeriesMetaData("average speed","%.1f" %(total_length/event_duration),"m/s"))
#            self._formdata.append(TimeSeriesMetaData("Total time",total_time,"s"))
            self._formdata.append(TimeSeriesMetaData("Total calories",total_calories,"kcal"))
            self._formdata.append(TimeSeriesMetaData("Event duration","%.1f" %(event_duration/60),"min"))
            
        return self._data

    @property
    def ui(self):
        layout = QFormLayout()
        self.labels=[]
        self.lineedits=[]
        if self._formdata or True:
            for i in range(len(self._formdata)):
                layout.addRow(QLabel(self._formdata[i].name+" ("+self._formdata[i].unit+")"), QLineEdit(str(self._formdata[i].value)))
                
        return layout
