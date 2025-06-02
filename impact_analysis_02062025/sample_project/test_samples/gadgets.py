class Battery:
    pass

class Phone:
    def __init__(self):
        self._battery = Battery()  # Composition (not strong/private)

class Tablet(Phone):
    pass