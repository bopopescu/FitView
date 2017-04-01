import logging
from logbook import Logbook
from tools.profiling import timing

@timing
def open_logbook():
    return Logbook("test.gl")
    
if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(asctime)s %(name)s %(message)s',
                        filename='test.log',level=logging.DEBUG
                        )
    logging.debug("program started")
    
    files = ['data/722G5750.FIT',
             'data/722I0802.FIT',
             'data/722I2307.FIT',
             'data/723H3126.FIT',
             'data/723H4335.FIT',
             'data/723H4644.FIT',
             'data/723I0946.FIT',
             'data/724B3804.FIT',
             'data/726I4241.FIT',
             'data/727G2555.FIT',
             'data/728H2016.FIT',
             'data/729G5728.FIT',
             'data/72AH2225.FIT',
             'data/72AI3117.FIT',
             'data/72BC0814.FIT',
             'data/72DH5613.FIT',
             'data/72EH2943.FIT',
             'data/72EH3845.FIT',
             'data/72EJ0424.FIT',
             'data/72FH0019.FIT',]
    
    logbook = open_logbook()
    logbook.import_file(files)
    print(logbook.events)
    x = logbook[2]
    print(logbook[x])
    print(logbook[2])
    print(logbook["4aa55503bafde996d98fdb617d8a988d14d74350ac08349a9c5c88524c7b0452"])