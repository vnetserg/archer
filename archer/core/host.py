
from ..util import is_ip


class Host:
    '''
        Class that represents remote host. Stores parameters of remote host,
        such as ip address, mac address, operating system, last activity
        and current state. Also stores ports information.
    '''

    # General case error
    class Error(Exception): pass

    # Exception that is raised when LocalHost method receives
    # as a parameter some obect that does not belong to this LocalHost instance.
    class ObjectError(Error): pass

    # Exception that is raised by dropJob if job is still running
    class DuplicateError(Error): pass

    # Exception that is raised by constructor if given IP address is invalid.
    class IPError(Error): pass


    def __init__(self, ip):
        '''
            Initialize host instance with given IP address.
            Raise self.IPError if given ip address is invalid
            Note that all the other remote host properties are set to None
            because Host object does not try to perform any active scanning
            of remote host to know these properties.
            It is LocalHost who becomes aware of remote host properties
            (through parsing jobs output) and sets the values of Host object
            attributes.
        '''

        if not is_ip(ip):
            raise self.IPError

        self.ip = ip # ip address
        self.mac = None # mac address
        self.os = None # operating system
        self.last_activity = None # timestamp of the last activity
        self.state = "unknown" # current state

        # Ports keys are transport protocols, values are dicts.
        # Each dict key is port number, value - Port object
        self.ports = {"tcp": {}, "udp": {}}


    def allPorts(self):
        '''
            Return list of all the Port objects of this host.
        '''
        return [port for proto in self.ports for port in self.ports[proto]]


    def addPort(self, port):
        '''
            Add port to this host.
            Raise self.DuplicateError if port with this protocol/number
            pair already exists.
        '''


    def dropPort(self, port):
        '''
            Delete port from this host.
            Raise ObjectError if this port object does not belong to this Host.
        '''
