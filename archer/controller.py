import os

from .core import LocalHost, Interface, Host, Port, Job, MuxJob


class Controller:
    '''
        This class defines the border between UI and backend.
        It implements the interface for the UI to interact
        with network interfaces, remote hosts, remote TCP/UDP ports,
        launch jobs etc.
    '''

    # General case error. When raised, error string contains human-readable
    # error message that could be displayed to user.
    class Error(Exception): pass


    def __init__(self):
        '''
            Initialize controller by creating LocalHost instance.
        '''
        self._localhost = LocalHost()


    def list(self, path="/"):
        '''
            List all the subdevices of given device.
        '''

        # Parse path string
        pstat = self._parsePath(path)

        # If path contains port - nothing to list
        if pstat["port"]:
            return []

        # If path contains transport proto - list all port numbers
        # if this proto on specified host
        if pstat["proto"]:
            return [str(port.number)
                    for port in pstat["host"].ports[pstat["proto"]].values()]

        # If path contains host - list all available transport protocols
        if pstat["host"]:
            return list(pstat["host"].ports.keys())

        # If path contains interface - list all the ip addresses of hosts
        # associated with this interface
        if pstat["interface"]:
            return [host.ip for host in pstat["interface"].hosts.values()]

        # Otherwise return names of all available interfaces
        return [iface.name for iface in self._localhost.interfaces.values()]


    def stat(self, path="/"):
        '''
            Return properties of given device.
        '''

        # Parse path string
        pstat = self._parsePath(path)

        # If path contains any entity - stat it
        for key in ["port", "proto", "host", "interface"]:
            if pstat[key]:
                if key != "proto":
                    return self._toJson(pstat[key])
                else:
                    # In case of transport proto, there is nothing really to stat
                    return {"name": pstat[key]}

        # If path is empty - stat localhost:
        return self._toJson(self._localhost)


    def listat(self, path="/"):
        '''
            Stat all the devices contained in given path.
            Same as listing path and then calling stat on each subdevice,
            but slightly faster. The only functional difference is that
            listat of /<interface>/<host> returns stat of all ports
            of the host, not all the available transport protocols.
        '''

        # Parse path string
        pstat = self._parsePath(path)

        # If path string contains port - nothing to list
        if pstat["port"]:
            return []

        # If path string contains transport protocol -
        # stat all ports of this proto
        if pstat["proto"]:
            return [self._toJson(port)
                    for port in pstat["host"].ports[pstat["proto"]].values()]

        # If path string contains host - stat all ports of this host
        if pstat["host"]:
            return [self._toJson(port) for port in pstat["host"].allPorts()]

        # If path string contains interface - stat all hosts bound to it
        if pstat["interface"]:
            return [self._toJson(host)
                    for host in pstat["interface"].hosts.values()]

        # Otherwise stat all interfaces
        return [self._toJson(iface) for iface in self._localhost.interfaces.values()]


    def create(self, path, name):
        '''
            Create subdevice with given path.
        '''

        # Parse path string
        pstat = self._parsePath(path)

        # Nothing can be created under port
        if pstat["port"]:
            raise self.Error("can not create subdevice to port")

        # If we have protocol, create a port
        if pstat["proto"]:
            try:
                port = Port(int(name), pstat["proto"])
            except Port.InvalidNumber:
                raise self.Error("invalid port: {}/{}".format(pstat["proto"], name))
            try:
                pstat["host"].addPort(port)
            except Host.DuplicateError:
                raise self.Error("port exists: {}/{}".format(path, name))

        # Transport protocols are not creatable
        elif pstat["host"]:
            raise self.Error("can not create transport protocol")

        # If we only have interface, create host
        elif pstat["interface"]:
            try:
                host = Host(name)
            except Host.IPError:
                raise self.Error("invalid ip address: {}".format(name))
            try:
                pstat["interface"].addHost(host)
            except Interface.DuplicateError:
                raise self.Error("host exists: {}/{}".format(path, name))

        # Interfaces are not creatable
        else:
            raise self.Error("can not create interface")


    def delete(self, path):
        '''
            Delete device given by path.
        '''

        # Parse path
        pstat = self._parsePath(path)

        # If port in path - drop it:
        if pstat["port"]:
            pstat["host"].dropPort(pstat["port"])

        # If transport protocol in path, it is an Error
        elif pstat["proto"]:
            raise self.Error("can not drop protocol")

        # If host in path - drop it
        elif pstat["host"]:
            pstat["interface"].dropHost(pstat["host"])

        # Interfaces are not dropable
        elif pstat["interface"]:
            raise self.Error("can not drop interface")

        # Localhost is not dropable too
        else:
            raise self.Error("can not drop localhost")


    def update(self):
        '''
            Update localhost. Return events generated by it almost untouched,
            but replace object references with pathes to those objects.
        '''
        events = self._localhost.update()
        for ev in events:
            if "object" in ev:
                ev["device"] = self._pathToObject(ev.pop("object"))
        return events


    def jobs(self, path="/"):
        '''
            List job ids of all the jobs that are running
            in context of given device.
        '''

        # Parse path
        pstat = self._parsePath(path)

        # Retreive the last object in path.
        # Note: job can not be run in context of protocol at host
        for key in ["port", "host", "interface"]:
            obj = pstat[key]
            if obj:
                break

        # Return job ids. If obj is None, jobsInContext returns
        # jobs that are run in context of localhost
        return [job.id for job in self._localhost.jobsInContext(obj)]


    def info(self, jid):
        '''
            Return properties of job with given jid.
        '''
        return self._toJson(self._getJob(jid))


    def signal(self, jid, signal="term"):
        '''
            Send specified signal to the job with given job id.
        '''
        try:
            self._getJob(jid).signal(signal)
        except Job.SignalError:
            # No such signal
            raise self.Error("no such signal: {}".format(signal))


    def read(self, jid):
        '''
            Read stdout of job with given id.
        '''
        return self._getJob(jid).read()


    def write(self, jid, data):
        '''
            Write to stdin of job with given id.
        '''
        self._getJob(jid).write(data)


    def run(self, jobname, context="/"):
        '''
            Run job with given name and arguments in context of given device.
            Return job id.
        '''

        # Parse context
        pstat = self._parsePath(context)

        # Create a job
        try:
            job = Job(jobname, pstat)
        except Job.NameError:
            raise self.Error("job manifest not found: {}".format(jobname))
        except Job.ContextError as exc:
            raise self.Error("inappropriate context for job: {}".format(str(exc)))

        # Add a job to localhost
        self._localhost.addJob(job)

        return job.id


    def runMux(self, jobname, contexts):
        '''
            Run multiple instances of the same job in different contexts.
            Those instances are counted as one job (aka multiplexed job).
            Return id of this job.
        '''

        # Parse all contexts
        pstats = [self._parsePath(cont) for cont in contexts]

        # Create multiplexed job
        try:
            job = MuxJob(jobname, pstats)
        except Job.NameError:
            raise self.Error("job manifest not found: {}".format(jobname))
        except Job.ContextError as exc:
            raise self.Error("inappropriate context for job: {}".format(str(exc)))

        # Add job to localhost
        self._localhost.addJob(job)

        return job.id


    def drop(self, jid):
        '''
            Delete job with given id. Job needs to be not running.
        '''
        job = self._getJob(jid)
        try:
            self._localhost.dropJob(job)
        except LocalHost.JobRunningError:
            raise self.Error("the job is still running")


    def _parsePath(self, path):
        '''
            Parse path string and return a meaningful structure that
            specifies, what interface, host, protocol and port
            are addressed by the path.
            Raise self.Error if parsing fails.
        '''

        # Current search status
        pstat = {
            "interface": None,
            "host": None,
            "proto": None,
            "port": None
        }

        # Device path is given using forward slashes
        for dev in path.strip("/").split("/"):

            # If empty string encountered, we are done
            if not dev: break

            # If no interface specified - try to get interface
            if not pstat["interface"]:
                try:
                    pstat["interface"] = self._localhost.interfaces[dev]
                except KeyError:
                    raise self.Error("interface not found: {}".format(dev))

            # Else if no host specified - get the host
            elif not pstat["host"]:
                try:
                    pstat["host"] = pstat["interface"].hosts[dev]
                except KeyError:
                    raise self.Error("host not found: {}/{}"
                                     .format(pstat["interface"], dev))

            # Else if no transport protocol specified - get it
            elif not pstat["proto"]:
                pstat["proto"] = dev.lower()
                if pstat["proto"] not in pstat["host"].ports:
                    raise self.Error("unknown transport proto: {}".format(dev))

            # Else if no port specified - add it
            elif not pstat["port"]:
                try:
                    num = int(dev)
                except ValueError:
                    raise self.Error("invalid port number: {}".format(dev))
                try:
                    pstat["port"] = pstat["host"].ports[pstat["proto"]][num]
                except KeyError:
                    raise self.Error("port not found: {}/{}"
                                     .format(pstat["proto"], num))

            # If there is still something in path, it is junk
            else:
                raise self.Error("junk path component: {}".format(dev))

        return pstat


    def _toJson(self, obj):
        '''
            Convert object to JSON representation.
        '''

        if isinstance(obj, LocalHost):
            return {
                "username": obj.username,
                "hostname": obj.hostname
            }

        if isinstance(obj, Interface):
            return {
                "name": obj.name,
                "ip": obj.ip,
                "mask": obj.mask,
                "mac": obj.mac,
                "gateway": obj.gateway,
                "state": obj.state
            }

        if isinstance(obj, Host):
            return {
                "ip": obj.ip,
                "mac": obj.mac,
                "os": obj.os,
                "last_activity": obj.last_activity,
                "state": obj.state
            }

        if isinstance(obj, Port):
            return {
                "number": obj.number,
                "proto": obj.proto,
                "last_activity": obj.last_activity,
                "state": obj.state
            }

        raise ValueError("Unknown object: {}".format(obj.__class__.__name__))


    def _pathToObject(self, obj):
        '''
            Return string path to device object.
        '''

        # Find parents of this object
        parents = self._localhost.findParents(obj)
        devs = parents + [obj]

        names = [] # list of device names participating in path

        if len(devs) >= 1:
            names.append(devs[0].name)
        elif len(devs) >= 2:
            names.append(devs[1].ip)
        elif len(devs >= 3):
            names += [devs[2].proto, int(devs[2].number)]

        return "/" + "/".join(names)


    def _getJob(self, jid):
        '''
            Get job by job id. Raise self.Error if no job with such jid found.
        '''
        try:
            job = self._localhost.jobs[jid]
        except KeyError:
            raise self.Error("no job found with id {}".format(jid))
