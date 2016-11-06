
class Interface:
    '''
        The class that represents network interface on the LocalHost.
        Determines current interface configuration and stores list of host
        that have been descovered behind this interface.
        Interface attributes are immutable - "update" method returns
        new Interface object if anything changed.
    '''


    # General case error
    class Error(Exception): pass

    # Exception that is raised when Interface method receives
    # as a parameter some obect that does not belong to this Interface instance.
    class ObjectError(Error): pass

    # Exception that is raised when addHost is called with host
    # that is already present on this interface.
    class DuplicateError(Error): pass


    def __init__(self, name):
        '''
            Initialize instance by gathering interface parameters:
            ip address, network mask, mac address, gateway address, state.
            Raise ValueError if interface with such name is not found.
        '''

        self.name = name # interface name
        self.mac = "" # mac address
        self.ip = "" # ip address
        self.mask = "" # network mask in full format, e.g. 255.255.255.0
        self.gateway = "" # address of gateway
        self.state = "" # interface state (either 'up' or 'down')

        self.hosts = {} # keys are host ip addresses, values are Host objects


    def update(self):
        '''
            Check if network interface parameters have changed.
            If so, return new Interface object that has new values.
            Otherwise return self.
            Note: new Interface object inherits all the Host objects.
            If it is not desired, client should delete them manually.
        '''


    def addHost(self, host):
        '''
            Add host object to this interface. Raise self.DuplicateError
            if host with given ip address already exists.
        '''


    def drop(self, host):
        '''
            Delete host from the list of known hosts.
            Raise ObjectError if host does not belong to this interface.
        '''
