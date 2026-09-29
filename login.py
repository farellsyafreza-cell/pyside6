from PySide6.QtWidgets import(
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QVBoxLayout
)
from PySide6.QtCore import Qt
from database.conn import koneksi_database

class Loginapp (QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(400, 480)
        self.buat_ui()

    def buat_ui(self):
        judul=QLabel("LOGIN")
        judul.setStyleSheet("""
            QWidget{
            font-size:30px;
            font-weight:bold;
            color:green;
            margin-bottom:20px
            }"""
        )
        judul.setAlignment(Qt.AlignCenter)

        label_username=QLabel("Username")
        label_username.setStyleSheet("""
            QLabel{
            color: #334155;
            font-weight: bold;
            font-size: 14px;
            }"""
           )
                
        self.username=QLineEdit()
        self.username.setPlaceholderText("Masukkan Username")
        self.username.setStyleSheet("""
            QLineEdit{
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus{
                border=2px solid #2563eb;
            }
        """)
        label_password=QLabel("Password")
        label_password.setStyleSheet("""
            QLabel{
            color: #334155;
            font-weight: bold;
            font-size: 14px;
            }"""
        )

        self.password=QLineEdit()
        self.password.setPlaceholderText("Masukkan Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet("""
            QLineEdit{
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus{
                border=2px solid #2563eb;
            }
        """)

        button=QPushButton("Login")
        button.clicked.connect(self.login)
        button.setStyleSheet("""
            QPushButton {
                background-color:#00FF00;
                color:white;
                border-radius: 8px;
                padding: 8px;
            }"""
        )
        button1=QPushButton("Keluar")
        button1.clicked.connect(self.close)
        button1.setStyleSheet("""
            QPushButton{
                background-color:#FF0000;
                color:white;
                border-radius: 8px;
                padding: 8px;
            }"""
        )

        layout= QVBoxLayout()
        layout.setContentsMargins(
            40, 40, 40, 40
        )
        layout.setSpacing(10)
        layout.addWidget(judul)
        layout.addWidget(label_username)
        layout.addWidget(self.username)
        layout.addWidget(label_password)
        layout.addWidget(self.password)
        layout.addSpacing(20)
        layout.addWidget(button)
        layout.addWidget(button1)
        self.setLayout(layout)

    def login(self):
        user=self.username.text()
        pw=self.password.text()

        if user == "" or pw == "":
            QMessageBox.warning(self, "Error", "Diisi dengan lengkap")
            return
        try:
            db=koneksi_database()
            cursor=db.cursor(dictionary=True)
            query= "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (user, pw))
            users=cursor.fetchone()
            cursor.close()
            db.close()
            
            if users:
                QMessageBox.information(self, "Login", "Berhasil!!!")
                nama=users["nama"]
                role=users["role"]
                self.buka_dashboard(nama, role)
            else:
                QMessageBox.warning(self, "Error", "Nama tidak sesuai")
                return
        except Exception as e:
            QMessageBox.critical(self, "Error database", f"Tidak bisa tersambung {e}")
            return 

    def buka_dashboard(self, nama, role):
        from dashboard import Dashboard
        self.dashboard= Dashboard(nama, role)
        self.dashboard.show()
        self.close()

if __name__ == "__main__":
    app=QApplication([])
    window=Loginapp()
    window.show()
    app.exec()