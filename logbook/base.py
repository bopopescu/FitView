from sqlalchemy import *
import logging
from fitparse import FitFile
import os.path
from yapsy.PluginManager import PluginManager 
from messages import EventTableEntry,LogRow
from tools.profiling import timing

class Logbook(object):

    def __init__(self, filename):
        self.logging = logging.getLogger(__name__)

        self.name = filename
        self.event_table = None

        self._alchemy_logbook = create_engine('sqlite:///'+filename)

        self._metadata = MetaData(bind=self._alchemy_logbook)
        self._file_table = Table("file",self._metadata,
                                 Column('file_id',Integer,primary_key=True),
                                 Column('file_name',String(20)),
                                 Column('file_hash',String(64),unique=True),
                                 Column('creation_date',DateTime),
                                 Column('event_name',String(30)),
                                 Column('event_type',String(30)),
                                 Column('event_subtype',String(30)),
                                 Column('duration',Integer),
                                 Column('calories',Integer)
                                 )
                
        self._check_database_integrity()
        
        self._plugins = {}
        
        try:
            manager = PluginManager()
            manager.setPluginPlaces(["logbook/Importer"])
            manager.collectPlugins()
        except Exception as e:
            print(e)
            
        '''
        load plugins and register them
        '''

        for p in manager.getAllPlugins():
            self.logging.info("loading plugin "+p.name)
            for t in p.plugin_object.type:
                self._plugins[t]=p.plugin_object
                self._plugins[t].open_logbook(filename)

        self.logging.info("%s plugins loaded"%len(manager.getAllPlugins()))
        self.read_events()
        self.logging.debug("Logbook initialized")
     
    @timing   
    def read_events(self):
        stmt = self._file_table.select().order_by(desc(self._file_table.c.creation_date))
        rows = stmt.execute()

        self.event_table = []

        for row in rows:
            self.event_table.append(EventTableEntry(filehash=row.file_hash,
                                                    date=row.creation_date,
                                                    name=row.event_name,
                                                    maintype=row.event_type,
                                                    subtype=row.event_subtype,
                                                    duration=row.duration,
                                                    calories=row.calories))

    def close_logbook(self):
        self.event_table = None
#        self._file_table.close()
#        self._alchemy_logbook.close()

    def _check_database_integrity(self):
        self._metadata.create_all(checkfirst=True)
 
    def import_files(self,files):
        for file in files:
            self.import_file(file)
 
    def import_file(self,file):
        try:
            fitfile = FitFile(file)
            filename = os.path.basename(file)
            filehash = fitfile.digest
            
            creation_date = ""
            event_name = ""
            event_sport = ""
            event_subsport = ""

#            if not result:
            self.logging.info("Importing file %s",filename)
                
            for record in fitfile.get_messages():
                for record_data in record:
                    if record.name == "file_id" and record_data.name == "time_created":
                        creation_date = record_data.value
                    if record.name == "sport":
                        if record_data.name == "sport":
                            event_sport = str(record_data.value)
                        if record_data.name == "sub_sport":
                            event_subsport = str(record_data.value)
                        if record_data.name == "name":
                            event_name = record_data.value.decode('utf-8')
                            
            try:
                file_insert = self._file_table.insert()
                f_id = file_insert.values(file_name=filename,file_hash=filehash,
                                          creation_date=creation_date,event_name=event_name,
                                          event_type=event_sport, event_subtype=event_subsport)
                conn = self._alchemy_logbook.connect()
                conn.execute(f_id)
                
                if event_sport not in self._plugins:
                    self.logging.info("delegating the import to plugin \"default\"")
                    self._plugins["default"].import_fit(fitfile)
                else:
                    self.logging.info("delegating the import to plugin \"%s\""%event_sport)
                    self._plugins[event_sport].import_fit(fitfile)
                    
            except Exception as e:
                self.logging.debug(e)
                
            self.logging.info("Import finished")

        except Exception as e:
#            self.logging.error("Error importing file")
            print(e)

        self.read_events()
                    
    @property
    def events(self):
        return self.event_table

    @timing
    def __getitem__(self,key):
        if isinstance(key, str):
            for x in self.event_table:
                if x.filehash == key:
                    return self.get_event(x)
            return None
        elif isinstance(key,EventTableEntry):
            for x in self.event_table:
                if x.filehash == key.filehash:
                    return self.get_event(x)
            return None
        else:
            return self.get_event(self.event_table[key])
        return None
        
    @timing
    def get_event(self,event):
        if event.maintype in self._plugins:
            return self._plugins[event.maintype].get_data(event.filehash)
        else:
            return self._plugins["default"].get_data(event.filehash)