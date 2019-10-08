""" The main Flask view for the print-my-brain frontend. AWS integration is
    handled through a separate helpers file.
"""

from flask import (
    render_template,
    request,
    redirect,
    url_for
)

from app import app
import helpers

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    """Landing page - get username"""
    return render_template('master.html')

@app.route('/print-my-brain')
def print_my_brain():
    """Redirect */print-my-brain to landing page"""
    return redirect(url_for('index'))

@app.route('/get_file', methods=['GET', 'POST'])
def get_file():
    """Ask user for file to upload, and submit batch job """
    username = request.args.get('username', '')

    if request.method == 'POST':
        file = request.files['user_file']
        if file and helpers.is_allowed_file(file.filename):
            print(f'username: {username}')
            file.filename = f'user-{username}.nii.gz'
            output = helpers.upload_file_to_s3(file)
            print(f's3 upload: {output}')
            job_id = helpers.submit_batch_job(username)
            print(f'job id: {job_id}')

        return redirect(url_for('submit_job', username=username, job_id=job_id))

    return render_template(
        'get_file.html',
        username=username
    )

@app.route('/submit_job', methods=['GET', 'POST'])
def submit_job():
    """Show user a confirmation page after job as been submitted """
    username = request.args.get('username', '')
    job_id = request.args.get('job_id', '')

    return render_template(
        'submit_job.html',
        username=username,
        job_id=job_id
    )


@app.route('/get_email', methods=['GET', 'POST'])
def get_email():
    """Get user's email """
    return render_template(
        'get_email.html'
    )

@app.route('/check_if_done', methods=['GET', 'POST'])
def check_if_done():
    """Check if job has completed. if so, redirect them to results """
    username = request.args.get('username', '')

    if helpers.is_processing_complete(username):
        return redirect(url_for('get_results', username=username))

    return render_template(
        'check_if_done.html',
        username=username
    )

@app.route('/get_results', methods=['GET', 'POST'])
def get_results():
    """Get user's email """
    username = request.args.get('username', '')

    lh_stl_url = helpers.get_url_to_s3(f'output/user-{username}-lh.stl')
    rh_stl_url = helpers.get_url_to_s3(f'output/user-{username}-rh.stl')
    lh_gif_url = helpers.get_url_to_s3(f'output/user-{username}-lh.gif')
    rh_gif_url = helpers.get_url_to_s3(f'output/user-{username}-rh.gif')

    return render_template(
        'get_results.html',
        username=username,
        lh_stl_url=lh_stl_url,
        rh_stl_url=rh_stl_url,
        lh_gif_url=lh_gif_url,
        rh_gif_url=rh_gif_url
    )
