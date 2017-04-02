import collections

'''
Created on 15.03.2017

@author: kreitz
'''
       
EventTableEntry    = collections.namedtuple("EventTableEntry", 
                                            "filehash date name maintype subtype duration calories")
'''
meta_data:    data for the mainwindow event table
form_data:    data for the event form
time_series:  array of TimeSeries for the chart
ui:           the event ui
'''
LogRow             = collections.namedtuple("LogRow", "meta_data form_data time_series ui")
LogMetaData        = collections.namedtuple("EventTableEntry", "file_hash date name maintype subtype")
FormData           = collections.namedtuple("FormData", "field_name field_value field_unit")
TimeSeriesData     = collections.namedtuple("TimeSeriesData","name labels data unit")
TimeSeriesMetaData = collections.namedtuple("TimeSeriesMetaData","name value unit")