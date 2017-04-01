from yapsy.IPlugin import IPlugin
from messages import EventTableEntry
from messages import LogMetaData

class Plugin:
    
    def __init__(self):
        self._actions=None
        self._type=None
        self._filename = None
        self._formdata = None
        self._data = None

    def open_logbook(self,logbook=None):
        pass

    def test(self,fitfile=None,logbook=None):
        pass
        
    def import_fit(self,fitfile=None,logbook=None):
        pass
    
    def get_data(self,event):
        return (None)

    @property
    def metadata(self):
        return self._metadata
    
    @property
    def data(self):
        if not self._data:
            self.get_data()
        return self._data

    @property
    def formdata(self):
        return []
            
    @property
    def actions(self):
        return self._actions
    
    @property
    def event(self):
        return self._event

    @property
    def type(self):
        return self._type
    
    @property
    def id(self):
        ret = ""
        for a in self._actions:
            ret = ret + " " +a
        for t in self._type:
            ret = ret+" "+t
        return ret
    
    def __repr__(self):
        return(" "+self._actions+" "+self._type)
    
    def printme(self):
        print("Plugin ",self._actions,self._type,self._filename,self._event)