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
        layout.setSpacing(10)
        self.label=QLabel("Kategori Barang")
        baris_atas = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Cari Barang...")

        self.tambah = QPushButton("Tambah")
        self.tambah.clicked.connect(self.tambah_kategori)

        self.edit = QPushButton("Edit")
        self.edit.clicked.connect(self.edit_kategori)
        self.hapus = QPushButton("Hapus")
        self.hapus.clicked.connect(self.hapus_kategori)

        baris_atas.addWidget(self.label)
        baris_atas.addStretch()
        baris_atas.addWidget(self.tambah)
        baris_atas.addWidget(self.edit)
        baris_atas.addWidget(self.hapus)

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
            query = """INSERT INTO categories (nama_kategori) VALUES (%s)"""
            
            cursor.execute(query, (nama,))
           
            db.commit()
            cursor.close()
            db.close()
            QMessageBox.information(
                self,
                "Berhasil",
                "Kategori berhasil ditambahkan."
            )
            
            self.cari_kategori(
                self.search.text()
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Database",
                f"Gagal menambahkan kategori:\n{e}"
            )

    def edit_kategori(self):

        baris = self.tabel.currentRow()

        if baris < 0:
            QMessageBox.warning(
                self,
                "Peringatan",
                "Silakan pilih kategori yang ingin diedit."
            )
            return

        kategori_id = self.tabel.item(baris, 0).text()
        nama_lama = self.tabel.item(baris, 1).text()

        nama_baru, ok = QInputDialog.getText(
            self,
            "Edit Kategori",
            "Nama Kategori:",
            text=nama_lama
        )

        if not ok:
            return

        nama_baru = nama_baru.strip()

        if not nama_baru:
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
                UPDATE categories
                SET nama_kategori = %s
                WHERE id = %s
            """

            cursor.execute(
                query,
                (nama_baru, kategori_id)
            )

            db.commit()

            cursor.close()
            db.close()

            QMessageBox.information(
                self,
                "Berhasil",
                "Kategori berhasil diperbarui."
            )

            self.cari_kategori(
                self.search.text()
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error Database",
                f"Gagal mengedit kategori:\n{e}"
            )

    def hapus_kategori(self):

        baris = self.tabel.currentRow()

        if baris < 0:
            QMessageBox.warning(
                self,
                "Peringatan",
                "Silakan pilih kategori yang ingin dihapus."
            )
            return

        kategori_id = self.tabel.item(baris, 0).text()
        nama_kategori = self.tabel.item(baris, 1).text()

        konfirmasi = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus kategori "
            f"'{nama_kategori}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if konfirmasi != QMessageBox.Yes:
            return

        try:

            db = koneksi_database()
            cursor = db.cursor()

            # Cek apakah kategori masih digunakan produk
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM products
                WHERE kategori_id = %s
                """,
                (kategori_id,)
            )

            jumlah_produk = cursor.fetchone()[0]

            if jumlah_produk > 0:

                cursor.close()
                db.close()

                QMessageBox.warning(
                    self,
                    "Tidak Bisa Dihapus",
                    f"Kategori '{nama_kategori}' masih digunakan "
                    f"oleh {jumlah_produk} produk.\n\n"
                    "Hapus atau pindahkan produk tersebut terlebih dahulu."
                )

                return

            # Hapus kategori
            cursor.execute(
                """
                DELETE FROM categories
                WHERE id = %s
                """,
                (kategori_id,)
            )

            db.commit()

            cursor.close()
            db.close()

            QMessageBox.information(
                self,
                "Berhasil",
                f"Kategori '{nama_kategori}' berhasil dihapus."
            )

            self.cari_kategori(
                self.search.text()
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error Database",
                f"Gagal menghapus kategori:\n{e}"
            )