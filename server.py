"""Remote Python flask application"""
# import sys
import psutil

from flask import Flask, render_template, request, jsonify

# ============================================== #
# Global variables for flask and other functions #
# ============================================== #
APP = Flask(__name__)

PROCS = psutil.cpu_count()


@APP.route('/')
def index():
    """Index page"""
    return render_template('index.html')


@APP.route('/jobs')
def jobs():
    """Jobs page"""
    return render_template('jobs.html')


@APP.route('/sys-info')
def sys_info():
    """System information page"""
    return render_template('sys-info.html', proc_count=PROCS)


@APP.route('/sys-info/update', methods=['GET'])
def sys_info_update():
    """Return some system info"""
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    # print(cpu, mem, file=sys.stderr)
    return jsonify(cpu=cpu, mem=mem)


@APP.route('/hello')
def hello():
    """Hello world! page"""
    return "Hello world!"


@APP.route('/post/<int:post_id>')
def show_post(post_id):
    """Show the post with the given id"""
    return render_template('base.html', testVar=post_id)


@APP.route('/_add_numbers', methods=['GET'])
def add_numbers():
    """JQuery and Flask add two numbers"""
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)
