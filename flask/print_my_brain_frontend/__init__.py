from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.config.from_object("config")

from helpers import *

@app.route("/", methods=["GET","POST"])

def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()

def upload_file():

	# A
    if "user_file" not in request.files:
        return "No user_file key in request.files"

	# B
    file    = request.files["user_file"]

    """
        These attributes are also available

        file.filename               # The actual name of the file
        file.content_type
        file.content_length
        file.mimetype

    """

	# C.
    if file.filename == "":
        return "Please select a file"

	# D.
    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        output   	  = upload_file_to_s3(file, app.config["S3_BUCKET"])
        return str(output)

    else:
        return redirect("/")
