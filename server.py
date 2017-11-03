"""Remote Python flask application"""
# Standard library modules
import os
import sys

# In-Project module
import fileio
import controller

# 3rd Party modules
import psutil
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

# ============================================== #
# Global variables for flask and other functions #
# ============================================== #
PROCS = psutil.cpu_count()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py'])
JOB_CONTROL = controller.job_controller()
app = Flask(__name__)


# ==================== #
# Flask configurations #
# ==================== #
app.config['UPLOAD_FOLDER'] = os.getcwd() + '/jobs/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024



# =============================================== #
# Create directories for pip cache and user files #
# =============================================== #
fileio.create_dirs()


@app.route('/')
def index():
    """Index page"""
    return render_template('index.html')


@app.route('/jobs')
def jobs():
    """Jobs page"""
    jobs = JOB_CONTROL.get_jobs()
    output = []
    for key in jobs:
        part = [i for i in jobs[key]]
        # part.append(part[-1].logs())
        print(part[-1].logs(), file=sys.stderr)
        output.append(part)
    print(output, file=sys.stderr)

        
    return render_template('jobs.html', jobs=output)


@app.route('/sys-info')
def sys_info():
    """System information page"""
    return render_template('sys-info.html', proc_count=PROCS)


@app.route('/sys-info/update', methods=['GET'])
def sys_info_update():
    """Return some system info"""
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    # print(cpu, mem, file=sys.stderr)
    return jsonify(cpu=cpu, mem=mem)


def allowed_file(filename):
    """Check if filename has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    """Used to upload a file to the server host"""
    # check if the post request has the file part
    if 'file' not in request.files:
        print("No file part", file=sys.stderr)
        return "No file pass"
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        print('No selected file', file=sys.stderr)
        return "No file choosen"
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('index', filename=filename))
    return "File Extension not supported"


@app.route('/submit-job', methods=['POST'])
def submit_job():
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
    return jsonify(id=JOB_CONTROL.get_current_token())


@app.route('/_add_numbers', methods=['GET'])
def add_numbers():
    """JQuery and Flask add two numbers"""
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)
