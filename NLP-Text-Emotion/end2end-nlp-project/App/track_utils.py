# Load Database Pkg
import sqlite3
import os
from contextlib import contextmanager

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'data.db')

@contextmanager
def get_db_connection():
	"""Context manager for database connections"""
	conn = sqlite3.connect(db_path)
	try:
		yield conn
	finally:
		conn.close()

# Fxn
def create_page_visited_table():
	"""Create page visit tracking table"""
	with get_db_connection() as conn:
		c = conn.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS pageTrackTable(pagename TEXT, timeOfvisit TIMESTAMP)')
		conn.commit()

def add_page_visited_details(pagename, timeOfvisit):
	"""Add page visit record"""
	with get_db_connection() as conn:
		c = conn.cursor()
		try:
			c.execute('INSERT INTO pageTrackTable(pagename, timeOfvisit) VALUES(?, ?)', (pagename, timeOfvisit))
			conn.commit()
		except sqlite3.Error as e:
			print(f"Database error: {e}")
			conn.rollback()
			raise

def view_all_page_visited_details():
	"""Retrieve all page visit records"""
	try:
		with get_db_connection() as conn:
			c = conn.cursor()
			c.execute('SELECT * FROM pageTrackTable')
			data = c.fetchall()
			return data
	except sqlite3.Error as e:
		print(f"Database error: {e}")
		return []


# Fxn To Track Input & Prediction
def create_emotionclf_table():
	"""Create emotion classification table"""
	with get_db_connection() as conn:
		c = conn.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS emotionclfTable(rawtext TEXT, prediction TEXT, probability NUMBER, timeOfvisit TIMESTAMP)')
		conn.commit()

def add_prediction_details(rawtext, prediction, probability, timeOfvisit):
	"""Add prediction record"""
	with get_db_connection() as conn:
		c = conn.cursor()
		try:
			c.execute('INSERT INTO emotionclfTable(rawtext, prediction, probability, timeOfvisit) VALUES(?, ?, ?, ?)', 
					 (rawtext, prediction, probability, timeOfvisit))
			conn.commit()
		except sqlite3.Error as e:
			print(f"Database error: {e}")
			conn.rollback()
			raise

def view_all_prediction_details():
	"""Retrieve all prediction records"""
	try:
		with get_db_connection() as conn:
			c = conn.cursor()
			c.execute('SELECT * FROM emotionclfTable')
			data = c.fetchall()
			return data
	except sqlite3.Error as e:
		print(f"Database error: {e}")
		return []