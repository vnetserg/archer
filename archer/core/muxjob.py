
class MuxJob:
    '''
        Continer class that multiplexes I/O from several jobs
        into one place. Intended use case is when the same job
        needs to be run in different contexts.
    '''

    def __init__(self, name, contexts):
        '''
            Initialize instance by creating the jobs.
            Raise Job.NameError if manifest for given job name is not found.
            Raise Job.ContextError if some contexts are inappropriate
            for this job.
        '''

        self.name = name # job name
        self.jobs = [Job(name, cont) for cont in context] # muxed jobs
        self.context = {} # the biggest common context
        self.jid = None # assigned by LocalHost before running


    def run(self):
        '''
            Run all the jobs.
        '''


    def update(self):
        '''
            Update all the jobs and return list of events from them.
            The order of returned events is undefined.
        '''


    def read(self):
        '''
            Read stdout of all the jobs.
            It is guaranteed that every line of returned text belongs to
            a single job; however, the order of those lines is undefined.
        '''


    def write(self, data):
        '''
            Write to stdin of all the jobs.
        '''


    def signal(self, sig="term"):
        '''
            Send signal to all the jobs.
            Raise Job.SignalError if signal name is invalid.
        '''


    def isRunning(self):
        '''
            Return True if any job is running.
        '''
