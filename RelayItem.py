# RelayItem fields.
class RelayItem:
    id=""
    created=""
    modified=""
    flags=""
    uaSetpoint=""
    uaCurrent=""

    def __init__(self, row):
        self.id         = row[0]
        self.created    = row[1]
        self.modified   = row[2]
        self.flags      = row[3]
        self.setpoint   = row[4]
        self.enable     = row[5]
        self.disable    = row[6]
        self.current    = row[7]
        self.name       = row[8]
    def update():
        return None
