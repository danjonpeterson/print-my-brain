from flask import (
	render_template,
	request,
	redirect,
	url_for
)

from app import app

from helpers import *

@app.route('/')
@app.route('/index',methods=["GET","POST"])
def index():
    return render_template('master.html')

@app.route('/print-my-brain')
def print_my_brain():
	return redirect(url_for('index'))

@app.route('/get_file',methods=["GET","POST"])
def get_file():
    username = request.args.get('username', '')

    if request.method == 'POST':
	
	    file = request.files["user_file"]
	
	    if file and allowed_file(file.filename):

	        print("username:"+username)
	        file.filename="user-{}.nii.gz".format(username)
	        output = upload_file_to_s3(file, app.config["S3_BUCKET"])
	        print("s3 upload:"+output)
	        job_id=submit_batch_job(username)
	        print("job id:"+job_id)

	    return redirect(url_for('submit_job', username=username, job_id=job_id))

    example_brain_url=get_url_to_s3('input/example_brain.nii.gz')

    return render_template(
        'get_file.html',
        username=username,
        example_brain_url=example_brain_url
    )

@app.route('/submit_job',methods=["GET","POST"])
def submit_job():

    username = request.args.get('username', '')
    job_id = request.args.get('job_id', '')


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

@app.route('/check_if_done',methods=["GET","POST"])
def check_if_done():
	username=request.args.get('username', '')

	if is_processing_complete(username):
		return redirect(url_for('get_results', username=username))
	else:
		return render_template(
			'check_if_done.html',
			username=username
			)







