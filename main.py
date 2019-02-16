import requests
import os
import subprocess
from subprocess import call
from flask import Flask, session, jsonify, request, render_template, redirect, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:////{os.getcwd()}/example.db"
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/matt/new_docker/example.db"

Session(app)
# Most databses seem to need the scoped session as it is needed for
# the multiple threads. SQLite doesn't allow multiple threads. Seeming as...
# there is only one thread, no nned for it and therefore, commit is unecessary because...
# with only one thread, there is no chance of a clash.
db = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], 
	connect_args={'check_same_thread':False},
	poolclass=StaticPool, echo=False)
#db = scoped_session(sessionmaker(bind=engine))

#engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
#db = scoped_session(sessionmaker(bind=engine))

#TABLE SCHEMA
db.execute('''CREATE TABLE if not exists file_data_table 
	(id INTEGER PRIMARY KEY AUTOINCREMENT, 
	name TEXT NOT NULL,
	type TEXT NOT NULL,
	size TEXT NOT NULL
	)''')

uploads_dir = "uploads"
allowed_extensions = set(['txt'])
#app.config['UPLOAD_FOLDER'] = uploads_dir

# def create_cursor():
# 	engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
# 	db = scoped_session(sessionmaker(bind=engine))
# 	return db


'''
Upload 'file' to the uploads_dir folder and returns data to the user
'''
@app.route('/', methods=['POST'])
def upload():
	
	rows = db.execute("SELECT * FROM file_data_table")
	file = request.files['file']
	filename = secure_filename(file.filename)
	for e in rows:
		if e.name == filename:
			return "File already exists on the server with this name.\n"
	f_ext = filename.rsplit('.',1)[1].lower()
	if f_ext in allowed_extensions:
		file.save(os.path.join(uploads_dir, filename))
		f_size = os.path.getsize(filename)
	else:
		return "This file type is not allowed.\n"
	db.execute('''INSERT INTO file_data_table (name, type, size)
		VALUES (:name, :type, :size)''',
		{"name":filename, "type":f_ext, "size":f_size})
	#db.commit()

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
	
	rows = db.execute("SELECT * FROM file_data_table")
	temp = {}
	for e in rows:
		temp[e.name] = {
			"filetype":e.type,
			"filesize":e.size
			}
	return jsonify(temp)
	#return render_template("index.html")

'''
Returns the output of the contents of the user requested file via the 'cat' command
'''
@app.route("/<string:input>", methods=["GET"])
def get_metadata(input):
	
	rows = db.execute("SELECT * FROM file_data_table")
	temp = []
	for e in rows:
		if e.name == input:
			file = open(f'{uploads_dir}/{e.name}')
			result = subprocess.run(['cat', f'{uploads_dir}/{e.name}'], 
				stdout=subprocess.PIPE)
			return result.stdout
	return "File not found.\n"

#TODO:
#Make 'upload' only be able to upload .txt. If not .txt, return error
#Make upload return a 'file not found' error
#Check if headers work with errors properly

