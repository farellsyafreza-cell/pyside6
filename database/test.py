from conn import koneksi_database

db=koneksi_database()

if db.is_connected:
    print("Database telah terhubung")
else:
    print("Database tidak bisa terhubung")


db.close()