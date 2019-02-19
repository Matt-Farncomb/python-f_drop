import requests
import os
import subprocess
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, exc
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import scoped_session, sessionmaker

import helpers

app = Flask(__name__)

# Connects to DB if exists, creates one if it doesn't and connects to that
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:////{os.getcwd()}/data.db"

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], 
	connect_args={'check_same_thread':False},
	poolclass=StaticPool, echo=False)

db = scoped_session(sessionmaker(bind=engine))

uploads_dir = "uploads"
rejected_uploads = "uploads/rejected"
allowed_extensions = set(['txt'])

#create 'uploads_content' table on start up if none exist
helpers.create_table(db)

# Scan uploads folder on start up to ensure the DB...
# reflects correctly what is in the folder...
# for example, in case user has deleted content from the uploads folder
helpers.rescan_db(db, uploads_dir, allowed_extensions)

'''
Upload 'file' to the uploads_dir folder and returns data to the user
'''
@app.route('/', methods=['POST'])
def upload():
	rows = db.execute("SELECT * FROM uploads_content")
	file = request.files['file']
	filename = secure_filename(file.filename)

	for e in rows:
		if e.name == filename:
			return "File already exists on the server with this name.\n"
	f_ext = filename.rsplit('.',1)[1].lower()
	if f_ext in allowed_extensions:	
		# send uploaded file to uploads_dir	
		file.save(os.path.join(uploads_dir, filename))
		f_size = os.path.getsize(f'{uploads_dir}/{filename}')
	else:
		return "This file type is not allowed.\n"
	helpers.insert(db, filename, f_ext, f_size)

	return jsonify ({ "Sucessfully uploaded": {
	 			"filename":filename,
	 			"filetype":f_ext,
	 			"filesize":f_size
	 			}})

'''
Returns a json object of all files uploaded and their data
'''
@app.route("/", methods=["GET"])
def index():
	rows = db.execute("SELECT * FROM uploads_content")
	temp = {}
	for e in rows:
		temp[e.name] = {
			"filetype":e.type,
			"filesize":e.size
			}
	return jsonify(temp)

'''
Returns the output of the contents of the user requested file via the 'cat' command
'''
@app.route("/<string:input>", methods=["GET"])
def get_metadata(input):
	rows = db.execute("SELECT * FROM uploads_content")
	temp = []
	for e in rows:
		if e.name == input:
			# runs CAT terminal command on the file requested
			file_contents = subprocess.run(['cat', f'{uploads_dir}/{e.name}'], 
				stdout=subprocess.PIPE)
			return file_contents.stdout
	return "File not found.\n"