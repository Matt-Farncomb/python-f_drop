import os
import shutil
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def create_table(db):	
	db.execute('''CREATE TABLE if not exists uploads_content 
		(id INTEGER PRIMARY KEY AUTOINCREMENT, 
		name TEXT NOT NULL,
		type TEXT NOT NULL,
		size TEXT NOT NULL,
		date_added REAL NOT NULL
		)''')
	db.commit()

def insert(db, f_name, f_ext, f_size):
	db.execute('''INSERT INTO uploads_content (name, type, size, date_added)
		VALUES (:name, :type, :size, :date_added)''',
		{"name":f_name, "type":f_ext, "size":f_size,
		"date_added":os.path.getmtime("uploads")})
	db.commit()

'''
Scan the uploads folder to find any files added since last DB update
'''
def rescan_db(db, uploads_dir, allowed_extensions):
	last_modified = os.path.getmtime("uploads")

	rows = db.execute('''SELECT date_added 
		FROM uploads_content
		ORDER BY id 
		DESC LIMIT 1''').fetchone()
	# Compare the date of latest added file to date modified of uploads_dir...
	# if different, a file was added manually without the api...
	if rows is None or rows.date_added != last_modified:
		# therefore table no longer is 100% accurate, so wipe it...
		db.execute("DROP TABLE uploads_content")
		create_table(db)
		# and re scan the uploads dir
		files = os.listdir(uploads_dir)
		for e in files:
			f_size = os.path.getsize(f'{uploads_dir}/{e}')
			f_ext = e.rsplit('.',1)[1].lower()
			# if manually added file type isn't allowed... 
			# move to rejected folder
			if f_ext not in allowed_extensions:
				shutil.move(e, f'{uploads_dir}/{rejected_uploads}')
			insert(db, e, f_ext, f_size)