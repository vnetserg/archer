
class Job:
    '''
        Class that represents a subprocess job.
        It implements the functionality of starting a job, reading it's
        stdout, writing to it's stdin and sending signals to it.
        Also this class loads job's manifest (description of what program
        expects as input and what it provides as output) and based on it
        does the parsing of stdout, generating events that are then
        analyzed by LocalHost.
    '''


    # General case error
    class Error(Exception): pass

    # Exception for constructor if job manifest with given name is not found
    class NameError(Error): pass

    # Exception for constructor if given context is inappropriatet for job
    class ContextError(Error): pass

    # Exception for signal() if there is no signal with given name
    class SignalError(Error): pass


    def __init__(self, name, context={}):
        '''
            Initialize the instance by loading manifest file for a job
            with given name and saving its context.
            Raise self.NameError if manifest for a job with given name
            is not found.
            Raise self.ContextError if given context is inappropriate for
            this job.
            Context is a dictionary with the following keys:
                interface - Interface object
                host - Host object
                port - Port object
            When ommitted, context values are considered None.
        '''

        # Make None context values explicit
        for key in ["interface", "host", "port"]:
            if key not in context:
                context[key] = None

        self.name = name # job manifest name
        self.context = context # job context
        self.jid = None # job id, assigned by LocalHost before running
        self.pid = None # os proccess id, assigned when run
        self.state = "init" # job state
        self.return_code = None # job return code


    def run(self):
        '''
            Run the job by creating a subproccess and launching it.
        '''

        # ...
        self.pid = 0 # assign id of created proccess
        self.state = "running"


    def update(self):
        '''
            Read subproccess stdout, save in internal buffer, parse it
            and return list of events. If neccesary, update self.state
            and self.return_code.
        '''


    def read(self):
        '''
            Read proccess stdout from Job's internal buffer.
            Note: should be called only after update() because this method
            does not actually communicate with subproccess.
        '''


    def write(self, data):
        '''
            Write to subproccess stdin.
        '''


    def signal(self, sig="term"):
        '''
            Send signal to subproccess.
            Raise self.SignalError if signal name is invalid.
        '''


    def isRunning(self):
        '''
            Return True if job is running now.
        '''
