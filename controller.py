import os
import sys
import time

import docker


class job_controller:
    def __init__(self):
        self.current_token = 0
        self.job_dir = os.getcwd() + '/jobs'
        self.cache_dir = os.getcwd() + "/cache"
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
        self.current_token += 1
        container_tag = "job-" + str(token)

        work_dir_local = self.job_dir + "/" + container_tag
        work_dir_container  = '/usr/src/app'

        cache_dir_local = self.cache_dir
        cache_dir_container = '/usr/src/app/pip'

        directory_map = {work_dir_local : {'bind' : work_dir_container, 'mode' : 'rw'},
                         cache_dir_local : {'bind' : cache_dir_container, 'mode' : 'rw'}}
        container = self.client.containers.run("python:slim", command, 
                volumes=directory_map, working_dir=work_dir_container, 
                network_mode="host", user=1000, detach=True)

        self.jobs[token] = [name, token, time.strftime("%c"), command, container]


    def get_logs(self, token):
        """get logs from the docker container"""
        return self.jobs[token].container.logs()


    def get_jobs(self):
        return self.jobs
 