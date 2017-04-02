import collections

'''
Created on 15.03.2017

@author: kreitz
'''
#Represents o line in the event table
LogMetaData        = collections.namedtuple("EventTableEntry", "filehash date name maintype subtype")

# represents on eevent
TimeSeries         = collections.namedtuple("TimeSeries", "data metadata")
TimeSeriesData     = collections.namedtuple("TimeSeriesData","name labels data unit xlabel")
TimeSeriesMetaData = collections.namedtuple("TimeSeriesMetaData","name value unit")

UIData             = collections.namedtuple("UIData","ui labels fields")
UIList             = collections.namedtuple("UIList","index ui labels fields")