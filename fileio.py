"""File operations"""
import pathlib


def create_dirs():
    """Creates needed directories"""
    pathlib.Path('jobs').mkdir(parents=True, exist_ok=True)
    pathlib.Path('cache').mkdir(parents=True, exist_ok=True)


def create_job_dir(token):
    """Creates a jobs directory"""
    pathlib.Path('jobs/job-' + str(token)).mkdir(parents=True, exist_ok=True)


def get_directory(token):
    """returns the job dir of given token"""
    return "job-" + str(token)