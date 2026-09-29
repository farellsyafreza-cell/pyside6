from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)
from PySide6.QtCore import Qt
from database.conn import koneksi_database

class Kategori (QWidget):
    def __init__(self):
        super().__init__()
        layout=QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(5)
        self.label=QLabel("Kategori Barang")
        self.search=QLineEdit()
        self.search.setPlaceholderText("Cari Barang...")
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.label)
        layout.addWidget(self.search)
        self.tabel=QTableWidget()
        self.tabel.setColumnCount(2)
        self.tabel.setHorizontalHeaderLabels([
            "ID",
            "Nama Kategori"
        ])
        self.tabel.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabel.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        layout.addWidget(self.tabel)

        self.label.setStyleSheet("""
            QLabel{
                color:black;
                font-size: 20px;
                font-weight: bold;
            }
            """)
        self.search.setStyleSheet("""
            QLineEdit{
                color:black;
                background-color:white;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 4px;
            }
            """)
        self.search.textChanged.connect(self.cari_kategori)
        self.cari_kategori("")
        self.setLayout(layout)

    def cari_kategori(self, teks):
        db=koneksi_database()
        cursor= db.cursor(dictionary=True)
        query="SELECT id, nama_kategori FROM categories WHERE nama_kategori LIKE %s"
        cursor.execute(query, (f"%{teks}%", ))
        data=cursor.fetchall()
        print(data)
        self.tabel.setRowCount(0)
        for kategori in data:
            baris= self.tabel.rowCount()
            self.tabel.insertRow(baris)
            self.tabel.setItem(baris, 0, QTableWidgetItem(str(kategori["id"])))
            self.tabel.setItem(baris, 1, QTableWidgetItem(kategori["nama_kategori"]))
        cursor.close()
        db.close()
