"""Docker controller"""
# ======================== #
# Standard library modules #
# ======================== #
import os
import sys
import time

# 3rd party modules #
import docker


class job_controller:
    """Job controller class"""
    def __init__(self):
        self.current_token = 0
        self.job_dir = os.getcwd() + '/jobs'
        self.cache_dir = os.getcwd() + "/cache"
        self.tokens = []
        self.jobs = {}

        print("Docker dir:", self.job_dir, file=sys.stderr)
        self.client = docker.from_env()
        print("Pulling docker images (may take some time)...", file=sys.stderr)
        self.client.images.pull("python:slim")


    def get_current_token(self):
        """Get the current token"""
        return self.current_token


    def add_job(self, name, command):
        """Starts a container with the given parameters"""
        token = self.current_token
        self.tokens.append(token)
        self.current_token += 1
        container_tag = "job-" + str(token)

        # Working directory
        work_dir_local = self.job_dir + "/" + container_tag
        work_dir_container  = '/usr/src/app'

        # Pip cache directory
        cache_dir_local = self.cache_dir
        cache_dir_container = '/usr/src/pip'

        # Map directorys and start container
        directory_map = {work_dir_local : {'bind' : work_dir_container, 'mode' : 'rw'},
                        cache_dir_local : {'bind' : cache_dir_container, 'mode' : 'rw'}}

        container = self.client.containers.run("python:slim", command, 
                        volumes=directory_map, working_dir=work_dir_container, 
                        network_mode="host", user=1000, detach=True)

        self.jobs[token] = {'name': name, 'token': token, 'id': container.short_id,
                            'stime': time.strftime("%c"), 'command': command, 'container': container}


    def get_logs(self, token):
        """get logs from the docker container"""
        log = self.client.containers.get(self.jobs[token]['id']).logs()
        return log.decode('utf8')


    # def rerun_job(self, token):
        # job = self.jobs[token][-1]
        # job.start()


    def get_status(self, token):
        status = ''
        try:
            status = self.client.containers.get(self.jobs[token]['id']).status
            if status == "exited":
                status = 'finished'
            return status
        except KeyError:
            return "creating"


    def get_jobs(self):
        return self.jobs


    def get_job_by_id(self, dID):
        for key in self.jobs:
            if self.jobs[key]['id'] == dID:
                return self.jobs[key]
        return -1
 