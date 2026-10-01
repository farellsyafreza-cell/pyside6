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

        baris_atas = QHBoxLayout()

        self.cari = QLineEdit()
        self.cari.setPlaceholderText("Cari Produk...")

        self.tambah = QPushButton("+ Tambah")
        self.tambah.clicked.connect(self.tambah_produk)
        layout.setAlignment(Qt.AlignTop)
        layout.addLayout(baris_atas)
        layout.addWidget(self.cari)
        layout.addWidget(self.tambah)
        self.table=QTableWidget()
        self.table.setColumnCount(6)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Kode Barang",
            "Nama Barang",
            "Kategori Id",
            "Harga",
            "Stock"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.table)
        self.cari.textChanged.connect(self.cari_barang)
        self.cari_barang("")
        self.setLayout(layout)

        self.setStyleSheet("""
            QLabel{
                color:black;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        self.cari.setStyleSheet("""
            QLineEdit{
                color:black;
                background-color:white;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 4px;
            }
        """)

    def cari_barang(self, teks):
        try:
            db=koneksi_database()
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
            keyword=(f"%{teks}%")
            cursor.execute(query, (keyword, keyword))
            hasil = cursor.fetchall()
            print(f"Hasil: {hasil}")
            self.table.setRowCount(0)


            for produk in hasil:
            
                barisan= self.table.rowCount()
                self.table.insertRow(barisan)
                self.table.setItem(barisan, 0, QTableWidgetItem(str(produk["id"])))
                self.table.setItem(barisan, 1, QTableWidgetItem(str(produk["kode_barang"])))
                self.table.setItem(barisan, 2, QTableWidgetItem(str(produk["nama_barang"])))
                kategori=produk["nama_kategori"] or "-"
                self.table.setItem(barisan, 3, QTableWidgetItem(str(kategori)))
                harga=produk["harga"]
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

        # =========================
        # KODE BARANG
        # =========================

        kode = QLineEdit()
        kode.setPlaceholderText("Contoh: BRG001")

        layout.addRow(
            "Kode Barang:",
            kode
        )

        # =========================
        # NAMA BARANG
        # =========================

        nama = QLineEdit()
        nama.setPlaceholderText("Nama barang")

        layout.addRow(
            "Nama Barang:",
            nama
        )

        # =========================
        # KATEGORI
        # =========================

        kategori = QComboBox()

        try:

            db = koneksi_database()
            cursor = db.cursor(dictionary=True)

            query = """
                SELECT id, nama_kategori
                FROM categories
                ORDER BY nama_kategori ASC
            """

            cursor.execute(query)

            daftar_kategori = cursor.fetchall()

            cursor.close()
            db.close()

            for item in daftar_kategori:

                kategori.addItem(
                    item["nama_kategori"],
                    item["id"]
                )

        except Exception as e:

            QMessageBox.warning(
                self,
                "Error Database",
                f"Gagal mengambil kategori:\n{e}"
            )

        layout.addRow(
            "Kategori:",
            kategori
        )

        # =========================
        # HARGA
        # =========================

        harga = QDoubleSpinBox()

        harga.setRange(
            0,
            999999999
        )

        harga.setDecimals(0)

        harga.setPrefix("Rp ")

        layout.addRow(
            "Harga:",
            harga
        )

        # =========================
        # STOCK
        # =========================

        stok = QSpinBox()

        stok.setRange(
            0,
            999999
        )

        layout.addRow(
            "Stock:",
            stok
        )

        # =========================
        # BUTTON
        # =========================

        tombol_simpan = QPushButton("Simpan")
        tombol_batal = QPushButton("Batal")

        baris_tombol = QHBoxLayout()

        baris_tombol.addWidget(
            tombol_simpan
        )

        baris_tombol.addWidget(
            tombol_batal
        )

        layout.addRow(
            baris_tombol
        )

        dialog.setLayout(layout)

        # =========================
        # BATAL
        # =========================

        tombol_batal.clicked.connect(
            dialog.reject
        )

        # =========================
        # SIMPAN
        # =========================

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

    # ==========================================
    # SIMPAN PRODUK
    # ==========================================

    def simpan_produk(
        self,
        dialog,
        kode,
        nama,
        kategori,
        harga,
        stok
    ):

        kode_barang = kode.text().strip()
        nama_barang = nama.text().strip()

        # =========================
        # VALIDASI
        # =========================

        if not kode_barang:

            QMessageBox.warning(
                dialog,
                "Peringatan",
                "Kode barang tidak boleh kosong."
            )

            return

        if not nama_barang:

            QMessageBox.warning(
                dialog,
                "Peringatan",
                "Nama barang tidak boleh kosong."
            )

            return

        if kategori.currentIndex() == -1:

            QMessageBox.warning(
                dialog,
                "Peringatan",
                "Silakan pilih kategori."
            )

            return

        kategori_id = kategori.currentData()

        harga_barang = harga.value()

        stok_barang = stok.value()

        # =========================
        # INSERT DATABASE
        # =========================

        try:

            db = koneksi_database()
            cursor = db.cursor()

            query = """
                INSERT INTO products
                (
                    kode_barang,
                    nama_barang,
                    kategori_id,
                    harga,
                    stok
                )
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    kode_barang,
                    nama_barang,
                    kategori_id,
                    harga_barang,
                    stok_barang
                )
            )

            db.commit()

            cursor.close()
            db.close()

            QMessageBox.information(
                dialog,
                "Berhasil",
                "Produk berhasil ditambahkan."
            )

            dialog.accept()

            # Refresh tabel
            self.cari_barang(
                self.cari.text()
            )

        except Exception as e:

            QMessageBox.critical(
                dialog,
                "Error Database",
                f"Gagal menambahkan produk:\n{e}"
            )