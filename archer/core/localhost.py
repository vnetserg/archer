
class LocalHost:
    '''
        The top-level class of the core components. Does discovery of
        local network interfaces upon instantiation, stores jobs
        and collects messages from them.
    '''

    def __init__(self):
        '''
            Initialize LocalHost instance by getting user name and host name
            and discovering network interfaces.
        '''

        self.username = "" # name of local user that runs thos proccess
        self.hostname = "" # name of the host machine
        self.interfaces = {} # keys are interfaces names, values - Interface objects
        self.jobs = {} # keys are job ids, values - Job or MuxJob objects


    def addJob(self, job):
        '''
            Set job id, add it to dict and run it.
            Raise self.ObjectError of job is run in context of uknown object.
        '''

        job.id = 0 # set job id
        self.jobs[job.id] = job # add job to dict

        # Job being added already "knows" it's context, so we need to extract
        # it in order to track what jobs are run in what contexts.
        # ...

        job.run()


    def update(self):
        '''
            Communicate with all the jobs, gathering messages from them,
            updating network objects accroding to these messages
            and generating list of events that occured.
        '''

        return [] # list of events


    def jobsInContext(self, obj=None):
        '''
            Return all the jobs that are run in context of given object.
            If None, return jobs that run in global context.
            Raise self.ObjectError if given object does not belong to this LocalHost.
        '''

        return [] # list of jobs


    def findParents(self, obj):
        '''
            Return list of all the ancestors of this object. List elements are:
                0: Interface object
                1: Host object
                2: Port object
        '''

        return [] # list of parent objects
