
def motorFactory(descp):
    pass

def gyroFactory(descp):
    pass

def breaksensorFactory(descp):
    pass

def compressorFactory(descp):
    pass

def solenoidFactory(descp):
    pass

group_mappings = {
    'motors':       motorFactory,
    'gyros':        gyroFactory,
    'digitalInput': breaksensorFactory,
    'compressors':  compressorFactory,
    'solenoids':    solenoidFactory
}

