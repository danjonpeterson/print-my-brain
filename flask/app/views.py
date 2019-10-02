from flask import render_template
from flask import request
from app import app

from helpers import *

@app.route('/')
@app.route('/index',methods=["GET","POST"])
def index():
    return render_template('master.html')


@app.route('/get_file',methods=["GET","POST"])
def get_file():
    username = request.args.get('username', '')

    message=''

    if request.method == 'POST':
	    if "user_file" not in request.files:
	        message="No user_file key in request.files"
	
	    file = request.files["user_file"]

	    if file.filename == "":
	        message="Please select a file"
	
	    if file and allowed_file(file.filename):
	       	output = upload_file_to_s3(file, app.config["S3_BUCKET"])
	        message=str(output)

    return render_template(
        'get_file.html',
        username=username,
        message=message
    )

@app.route('/submit_job',methods=["GET","POST"])
def submit_job():

    username = request.args.get('username', '')

    job_id=submit_batch_job(username)

    return render_template(
        'submit_job.html',
        username=username,
        job_id=job_id
    )


@app.route('/get_email',methods=["GET","POST"])
def get_email():

	return render_template(
		'get_email.html'
	)

@app.route('/get_results',methods=["GET","POST"])
def get_results():

	username=request.args.get('username', '')

	lh_stl_url=get_url_to_s3('output/user-'+username+'-lh.stl')
	rh_stl_url=get_url_to_s3('output/user-'+username+'-rh.stl')
	lh_gif_url=get_url_to_s3('output/user-'+username+'-lh.gif')
	rh_gif_url=get_url_to_s3('output/user-'+username+'-rh.gif')

	return render_template(
		'get_results.html',
		username=username,
		lh_stl_url=lh_stl_url,
		rh_stl_url=rh_stl_url,
		lh_gif_url=lh_gif_url,
		rh_gif_url=rh_gif_url
	)




