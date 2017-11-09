"""Remote Python flask application"""
# ======================== #
# Standard library modules #
# ======================== #
import os
import sys
import time
import threading

from collections import deque

# ================= #
# In-Project module #
# ================= #
import fileio
import controller

# ================= #
# 3rd Party modules #
# ================= #
import psutil
from flask import Flask, render_template, request, jsonify, Response
from werkzeug.utils import secure_filename

# ============================================== #
# Global variables for flask and other functions #
# ============================================== #
PROCS = psutil.cpu_count() # Processor Count
ALLOWED_EXTENSIONS = set(['py', 'sh']) # Allowed files
JOB_CONTROL = controller.job_controller() # docker controller
Activity = deque([]) # System activity monitor
LOCK = threading.Lock() # Threading lock
app = Flask(__name__) # Flask app


# ==================== #
# Flask configurations #
# ==================== #
app.config['UPLOAD_FOLDER'] = os.getcwd() + '/jobs/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# =============================================== #
# Create directories for pip cache and user files #
# =============================================== #
fileio.create_dirs()


# ================================================ #
# Define flask routes and where they get html from #
# ================================================ #
@app.route('/')
def index():
    """Index page"""
    return render_template('index.html')


@app.route('/jobs')
def jobs():
    """Jobs page"""
    return render_template('jobs.html')


@app.route('/jobs-table', methods=['GET', 'POST'])
def jobs_update():
    all_jobs = JOB_CONTROL.get_jobs()
    output = []
    for token in all_jobs:
        # part = [i for i in all_jobs[key]]
        part = all_jobs[token]
        log = JOB_CONTROL.get_logs(token)
        status = JOB_CONTROL.get_status(token)
        if log == '':
            part['log'] = ""
            part['log_len'] = 1
            part['status'] = status
        else:
            log_len = len(log.split('\n'))
            part['log'] = log
            part['log_len'] = log_len
            part['status'] = status
        output.append(part)
    return render_template('job-table.html', jobs=output)


@app.route('/jobs/<dID>')
def job_page(dID):
    job = ''
    try:
        job = JOB_CONTROL.get_job_by_id(dID)
        if job == -1:
            return "Job not found!"
    except Exception:
        return "Job not found!"
    log = JOB_CONTROL.get_logs(job['token'])
    log_len = len(log.split('\n'))
    status = JOB_CONTROL.get_status(job['token'])
    job['log'] = log
    job['log_len'] = log_len
    job['status'] = status
    return render_template('job-page.html', job=job)



@app.route('/sys-info')
def sys_info():
    """System information page"""
    return render_template('sys-info.html', proc_count=PROCS)


@app.route('/sys-info/update', methods=['GET'])
def sys_info_update():
    """Return some system info"""
    with LOCK:
        cpu = [ele[0] for ele in Activity]
        mem = [ele[1] for ele in Activity]
        return jsonify(cpu=cpu, mem=mem)


def allowed_file(filename):
    """Check if filename has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/submit-job', methods=['POST'])
def submit_job():
    """Submit a job to run"""
    job_name = request.form['jobTitle']
    command = request.form['command']
    token = JOB_CONTROL.get_current_token()
    fileio.create_job_dir(token)
    if 'file' not in request.files:
        print("No file part", file=sys.stderr)
        return "No file passed"
    file = request.files['file']
    if file.filename == '':
        print('No selected file', file=sys.stderr)
        return "No file choosen"
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'] +
                               fileio.get_directory(token), filename))

    JOB_CONTROL.add_job(job_name, command)
    return jobs()


@app.route('/get-job-id', methods=['GET'])
def get_job_id():
    """Get next job id"""
    return jsonify(id=JOB_CONTROL.get_current_token())


@app.route('/_add_numbers', methods=['GET'])
def add_numbers():
    """JQuery and Flask add two numbers"""
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)


# =============================== #
# Setting up the activity monitor #
# =============================== #
def activity_monitor(act, lock):
    """Monitors the system polling in he background"""
    next_call = time.time()
    while True:
        with lock:
            act.append((psutil.cpu_percent(),
                        psutil.virtual_memory().percent,
                        time.time()))
            if len(act) >= 120:
                act.popleft()
        next_call += 1
        time.sleep(next_call - time.time())


Activity_Thread = threading.Thread(target=activity_monitor, args=(Activity, LOCK))
Activity_Thread.daemon = True
Activity_Thread.start()