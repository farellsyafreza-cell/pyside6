from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidgetItem,
    QLineEdit,
    QTableWidget,
    QHeaderView,
    QMessageBox,
    QAbstractItemView,
    QDialog,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox
)
from PySide6.QtCore import Qt
from database.conn import koneksi_database

class Produk(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)
        self.label=QLabel("Data Produk")

        baris_atas = QHBoxLayout()

        self.cari = QLineEdit()
        self.cari.setPlaceholderText("Cari Produk...")

        self.tambah = QPushButton("+ Tambah")
        self.tambah.clicked.connect(self.tambah_produk)

        self.edit = QPushButton("Edit")
        self.edit.clicked.connect(self.edit_produk)

        self.hapus = QPushButton("Hapus")
        self.hapus.clicked.connect(self.hapus_produk)

        baris_atas.addWidget(self.cari)
        baris_atas.addWidget(self.tambah)
        baris_atas.addWidget(self.edit)
        baris_atas.addWidget(self.hapus)

        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.label)
        layout.addLayout(baris_atas)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Kode Barang",
            "Nama Barang",
            "Kategori",
            "Harga",
            "Stock",
            ""
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.table)
        self.cari.textChanged.connect(self.cari_barang)
        self.cari_barang("")
        self.setLayout(layout)

        self.setStyleSheet("""
            QLabel {
                color: black;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        self.cari.setStyleSheet("""
            QLineEdit {
                color: black;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 4px;
            }
        """)

    def cari_barang(self, teks):
        try:
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)
            query = """
                SELECT p.id, p.kode_barang, p.nama_barang, p.kategori_id, c.nama_kategori,
                       p.harga, p.stok
                FROM products p
                LEFT JOIN categories c ON p.kategori_id = c.id
                WHERE p.nama_barang LIKE %s
                OR p.kode_barang LIKE %s
                ORDER BY p.id ASC
            """
            keyword = (f"%{teks}%")
            cursor.execute(query, (keyword, keyword))
            hasil = cursor.fetchall()
            self.table.setRowCount(0)

            for produk in hasil:
                barisan = self.table.rowCount()
                self.table.insertRow(barisan)
                self.table.setItem(barisan, 0, QTableWidgetItem(str(produk["id"])))
                self.table.setItem(barisan, 1, QTableWidgetItem(str(produk["kode_barang"])))
                self.table.setItem(barisan, 2, QTableWidgetItem(str(produk["nama_barang"])))
                kategori = produk["nama_kategori"] or "-"
                self.table.setItem(barisan, 3, QTableWidgetItem(str(kategori)))
                harga = produk["harga"]
                self.table.setItem(barisan, 4, QTableWidgetItem(f"Rp {float(harga):,.0f}".replace(",", ".")))
                self.table.setItem(barisan, 5, QTableWidgetItem(str(produk["stok"])))
            
            cursor.close()
            db.close()
        except Exception as e:
            QMessageBox.warning(self, "Error Database", f"Gagal mengambil data produk:\n{e}")

    def tambah_produk(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Tambah Produk")
        dialog.setMinimumWidth(400)

        layout = QFormLayout()

        # Kode Barang
        kode = QLineEdit()
        kode.setPlaceholderText("Contoh: BRG001")
        layout.addRow("Kode Barang:", kode)

        # Nama Barang
        nama = QLineEdit()
        nama.setPlaceholderText("Nama barang")
        layout.addRow("Nama Barang:", nama)

        # Kategori
        kategori = QComboBox()
        try:
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)
            query = "SELECT id, nama_kategori FROM categories ORDER BY nama_kategori ASC"
            cursor.execute(query)
            daftar_kategori = cursor.fetchall()
            cursor.close()
            db.close()

            for item in daftar_kategori:
                kategori.addItem(item["nama_kategori"], item["id"])
        except Exception as e:
            QMessageBox.warning(self, "Error Database", f"Gagal mengambil kategori:\n{e}")

        layout.addRow("Kategori:", kategori)

        # Harga
        harga = QDoubleSpinBox()
        harga.setRange(0, 999999999)
        harga.setDecimals(0)
        harga.setPrefix("Rp ")
        layout.addRow("Harga:", harga)

        # Stock
        stok = QSpinBox()
        stok.setRange(0, 999999)
        layout.addRow("Stock:", stok)

       
        # Button
        tombol_simpan = QPushButton("Simpan")
        tombol_batal = QPushButton("Batal")

        baris_tombol = QHBoxLayout()
        baris_tombol.addWidget(tombol_simpan)
        baris_tombol.addWidget(tombol_batal)

        layout.addRow(baris_tombol)
        dialog.setLayout(layout)

        tombol_batal.clicked.connect(dialog.reject)
        tombol_simpan.clicked.connect(
            lambda: self.simpan_produk(
                dialog,
                kode,
                nama,
                kategori,
                harga,
                stok
            )
        )
        dialog.exec()

    def simpan_produk(self, dialog, kode, nama, kategori, harga, stok):
        kode_barang = kode.text().strip()
        nama_barang = nama.text().strip()

        if not kode_barang:
            QMessageBox.warning(dialog, "Peringatan", "Kode barang tidak boleh kosong.")
            return

        if not nama_barang:
            QMessageBox.warning(dialog, "Peringatan", "Nama barang tidak boleh kosong.")
            return

        if kategori.currentIndex() == -1:
            QMessageBox.warning(dialog, "Peringatan", "Silakan pilih kategori.")
            return

        kategori_id = kategori.currentData()
        harga_barang = harga.value()
        stok_barang = stok.value()

        try:
            db = koneksi_database()
            cursor = db.cursor()
            query = """
                INSERT INTO products (kode_barang, nama_barang, kategori_id, harga, stok )
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (kode_barang, nama_barang, kategori_id, harga_barang, stok_barang))
            db.commit()
            cursor.close()
            db.close()

            QMessageBox.information(dialog, "Berhasil", "Produk berhasil ditambahkan.")
            dialog.accept()
            self.cari_barang(self.cari.text())
        except Exception as e:
            QMessageBox.critical(dialog, "Error Database", f"Gagal menambahkan produk:\n{e}")

    # ==========================================
    # EDIT PRODUK
    # ==========================================
    def edit_produk(self):
        baris = self.table.currentRow()
        if baris < 0:
            QMessageBox.warning(
                self,
                "Peringatan",
                "Silakan pilih produk yang ingin diubah dari tabel terlebih dahulu."
            )
            return

        produk_id = self.table.item(baris, 0).text()

        try:
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products WHERE id = %s", (produk_id,))
            data_produk = cursor.fetchone()
            cursor.close()
            db.close()
        except Exception as e:
            QMessageBox.critical(self, "Error Database", f"Gagal mengambil detail produk:\n{e}")
            return

        if not data_produk:
            QMessageBox.warning(self, "Peringatan", "Data produk tidak ditemukan.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Produk")
        dialog.setMinimumWidth(400)

        layout = QFormLayout()

        # Kode Barang
        kode = QLineEdit()
        kode.setText(str(data_produk["kode_barang"]))
        layout.addRow("Kode Barang:", kode)

        # Nama Barang
        nama = QLineEdit()
        nama.setText(str(data_produk["nama_barang"]))
        layout.addRow("Nama Barang:", nama)

        # Kategori
        kategori = QComboBox()
        kategori_id_saat_ini = data_produk["kategori_id"]

        try:
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id, nama_kategori FROM categories ORDER BY nama_kategori ASC")
            daftar_kategori = cursor.fetchall()
            cursor.close()
            db.close()

            index_pilihan = -1
            for idx, item in enumerate(daftar_kategori):
                kategori.addItem(item["nama_kategori"], item["id"])
                if item["id"] == kategori_id_saat_ini:
                    index_pilihan = idx

            if index_pilihan != -1:
                kategori.setCurrentIndex(index_pilihan)
        except Exception as e:
            QMessageBox.warning(self, "Error Database", f"Gagal mengambil kategori:\n{e}")

        layout.addRow("Kategori:", kategori)

        # Harga
        harga = QDoubleSpinBox()
        harga.setRange(0, 999999999)
        harga.setDecimals(0)
        harga.setPrefix("Rp ")
        harga.setValue(float(data_produk["harga"]))
        layout.addRow("Harga:", harga)

        # Stock
        stok = QSpinBox()
        stok.setRange(0, 999999)
        stok.setValue(int(data_produk["stok"]))
        layout.addRow("Stock:", stok)

        

        # Button
        tombol_simpan = QPushButton("Update")
        tombol_batal = QPushButton("Batal")

        baris_tombol = QHBoxLayout()
        baris_tombol.addWidget(tombol_simpan)
        baris_tombol.addWidget(tombol_batal)

        layout.addRow(baris_tombol)
        dialog.setLayout(layout)

        tombol_batal.clicked.connect(dialog.reject)
        tombol_simpan.clicked.connect(
            lambda: self.update_produk(
                dialog,
                produk_id,
                kode,
                nama,
                kategori,
                harga,
                stok,
                
            )
        )
        dialog.exec()

    # ==========================================
    # UPDATE PRODUK
    # ==========================================
    def update_produk(self, dialog, produk_id, kode, nama, kategori, harga, stok, ):
        kode_barang = kode.text().strip()
        nama_barang = nama.text().strip()

        if not kode_barang:
            QMessageBox.warning(dialog, "Peringatan", "Kode barang tidak boleh kosong.")
            return

        if not nama_barang:
            QMessageBox.warning(dialog, "Peringatan", "Nama barang tidak boleh kosong.")
            return

        if kategori.currentIndex() == -1:
            QMessageBox.warning(dialog, "Peringatan", "Silakan pilih kategori.")
            return

        kategori_id = kategori.currentData()
        harga_barang = harga.value()
        stok_barang = stok.value()

        try:
            db = koneksi_database()
            cursor = db.cursor()
            query = """
                UPDATE products
                SET kode_barang = %s,
                    nama_barang = %s,
                    kategori_id = %s,
                    harga = %s,
                    stok = %s
                WHERE id = %s
            """
            cursor.execute(
                query,
                (
                    kode_barang,
                    nama_barang,
                    kategori_id,
                    harga_barang,
                    stok_barang,
                    produk_id
                )
            )
            db.commit()
            cursor.close()
            db.close()

            QMessageBox.information(dialog, "Berhasil", "Produk berhasil diperbarui.")
            dialog.accept()
            self.cari_barang(self.cari.text())
        except Exception as e:
            QMessageBox.critical(dialog, "Error Database", f"Gagal memperbarui produk:\n{e}")

    # ==========================================
    # HAPUS PRODUK
    # ==========================================
    def hapus_produk(self):
        baris = self.table.currentRow()
        if baris < 0:
            QMessageBox.warning(
                self,
                "Peringatan",
                "Silakan pilih produk yang ingin dihapus dari tabel terlebih dahulu."
            )
            return

        produk_id = self.table.item(baris, 0).text()
        nama_barang = self.table.item(baris, 2).text()

        konfirmasi = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus produk '{nama_barang}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if konfirmasi == QMessageBox.Yes:
            try:
                db = koneksi_database()
                cursor = db.cursor()
                cursor.execute("DELETE FROM products WHERE id = %s", (produk_id,))
                db.commit()
                cursor.close()
                db.close()

                QMessageBox.information(self, "Berhasil", "Produk berhasil dihapus.")
                self.cari_barang(self.cari.text())
            except Exception as e:
                QMessageBox.critical(self, "Error Database", f"Gagal menghapus produk:\n{e}")