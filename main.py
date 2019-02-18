import requests
import os
import subprocess
import shutil
from flask import Flask, jsonify, request
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:////{os.getcwd()}/data.db"
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
def create_table():	
	db.execute('''CREATE TABLE if not exists uploads_content 
		(id INTEGER PRIMARY KEY AUTOINCREMENT, 
		name TEXT NOT NULL,
		type TEXT NOT NULL,
		size TEXT NOT NULL,
		date_added REAL NOT NULL
		)''')

uploads_dir = "uploads"
rejected_uploads = "uploads/rejected"
allowed_extensions = set(['txt'])
create_table()
#app.config['UPLOAD_FOLDER'] = uploads_dir

#Scan uploads folder on start up:
#	- done to ensure the Db reflects correctly what is in the folder,
#	for ewxampe, in case user has deleted content from the uploads folder
def insert(f_name, f_ext, f_size):
	db.execute('''INSERT INTO uploads_content (name, type, size, date_added)
		VALUES (:name, :type, :size, :date_added)''',
		{"name":f_name, "type":f_ext, "size":f_size,
		"date_added":os.path.getmtime("uploads")})

def rescan_db():
	last_modified = os.path.getmtime("uploads")
	# rows = db.execute('''SELECT COUNT(*)
	# 	FROM uploads_content
	# 	WHERE added < :last_modified''')
	rows = db.execute('''SELECT date_added 
		FROM uploads_content
		ORDER BY id 
		DESC LIMIT 1''').fetchone()
	# if this is true, it means a file was added without the api...
	if rows is None or rows.date_added != last_modified:
		# therefore table no longer is 100% accurate, so wipe it...
		#raise ValueError("Scannng")
		db.execute("DROP TABLE uploads_content")
		create_table()
		# and re scan the uploads dir
		files = os.listdir(uploads_dir)
		for e in files:
			f_size = os.path.getsize(f'{uploads_dir}/{e}')
			f_ext = e.rsplit('.',1)[1].lower()
			#if the incorrectly added file isn't allowed, move to rejected folder
			if f_ext not in allowed_extensions:
				shutil.move(e, f'{uploads_dir}/{rejected_uploads}')
			insert(e, f_ext, f_size)

rescan_db()
'''
Upload 'file' to the uploads_dir folder and returns data to the user
'''
@app.route('/', methods=['POST'])
def upload():
	rows = db.execute("SELECT * FROM uploads_content")
	file = request.files['file']
	filename = secure_filename(file.filename)
	#print("test")
	#return secure_filename(file.filename)
	#return(os.path.abspath(os.path.dirname(filename)))
	for e in rows:
		if e.name == filename:
			return "File already exists on the server with this name.\n"
	f_ext = filename.rsplit('.',1)[1].lower()
	if f_ext in allowed_extensions:
		
		file.save(os.path.join(uploads_dir, filename))
		f_size = os.path.getsize(f'{uploads_dir}/{filename}')
		#f_size = os.path.getsize(filename)
		#f_size = "1"
	else:
		return "This file type is not allowed.\n"
	insert(filename, f_ext, f_size)
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
			file = open(f'{uploads_dir}/{e.name}')
			result = subprocess.run(['cat', f'{uploads_dir}/{e.name}'], 
				stdout=subprocess.PIPE)
			return result.stdout
	return "File not found.\n"
