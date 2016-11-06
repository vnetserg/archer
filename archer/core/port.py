
class Port:
    '''
        Class that represents TCP/UDP port on remote host. It stores
        information such as transport layer protocol, port number,
        last activity timestamp and state.
    '''


    # General case error
    class Error(Exception): pass

    # Exception for a case if constructor receives invalid port number
    class NumberError(Error): pass

    # Exception for a case if constructor receives invalid protocol name
    class ProtocolError(Error): pass


    def __init__(self, num, proto):
        '''
            Initialize Port instance by setting port number and protocol type.
            Raise self.NumberError if port number is out of range.
            Raise self.ProtocolError if protocol type is unknown.
            Note: last_activity and state attributes are assigned by LocalHost,
            since Port object itself does not perform any active scanning.
        '''

        if not (0 < num < 65536):
            raise self.NumberError
        if proto not in ("tcp", "udp"):
            raise self.ProtocolError

        self.num = num # port number
        self.proto = proto # transport-layer protocol
        self.last_activity = None # last activity timestamp
        self.state = "unknown" # current state
