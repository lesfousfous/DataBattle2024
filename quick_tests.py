from database import Database

db = Database()
cursor = db.database_connection.cursor()
cursor.execute("SELECT COUNT(*) FROM tblsolution")
print(cursor.fetchall())
