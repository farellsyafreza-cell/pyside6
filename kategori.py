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
    QHeaderView,
    QInputDialog,
    QAbstractItemView
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
        baris_atas = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Cari Barang...")

        self.tambah = QPushButton("+ Tambah")
        self.tambah.clicked.connect(self.tambah_kategori)

        baris_atas.addWidget(self.search)
        baris_atas.addWidget(self.tambah)

        layout.addLayout(baris_atas)
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
        self.tabel.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabel.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.tabel)

        self.label.setStyleSheet("""
            QLabel{
                color:black;
                font-size: 20px;
                font-weight: bold;
            }
            """)

        self.setStyleSheet("""
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

    def tambah_kategori(self):

        nama, ok = QInputDialog.getText(
            self,
            "Tambah Kategori",
            "Nama Kategori:"
        )

        if not ok:
            return

        nama = nama.strip()

        if not nama:

            QMessageBox.warning(
                self,
                "Peringatan",
                "Nama kategori tidak boleh kosong."
            )

            return

        try:

            db = koneksi_database()
            cursor = db.cursor()

            query = """
                INSERT INTO categories (nama_kategori)
                VALUES (%s)
            """

            cursor.execute(
                query,
                (nama,)
            )

            db.commit()

            cursor.close()
            db.close()

            QMessageBox.information(
                self,
                "Berhasil",
                "Kategori berhasil ditambahkan."
            )

            # Refresh tabel
            self.cari_kategori(
                self.search.text()
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error Database",
                f"Gagal menambahkan kategori:\n{e}"
            )