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
    QDoubleSpinBox,
    QGroupBox
)
from PySide6.QtCore import Qt
from datetime import datetime
from database.conn import koneksi_database


class DialogTransaksiBaru(QDialog):
    def __init__(self, parent=None, user_id=1):
        super().__init__(parent)
        self.user_id = user_id
        self.cart_items = []  # list of dict: {product_id, nama_barang, kode_barang, harga, jumlah, subtotal}
        
        self.setWindowTitle("Transaksi Baru")
        self.resize(700, 550)
        
        self.init_ui()
        self.generate_nomor_transaksi()
        self.load_produk()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Header Info
        header_group = QGroupBox("Informasi Transaksi")
        header_layout = QFormLayout()
        
        self.lbl_nomor_trx = QLineEdit()
        self.lbl_nomor_trx.setReadOnly(True)
        header_layout.addRow("Nomor Transaksi:", self.lbl_nomor_trx)
        
        header_group.setLayout(header_layout)
        main_layout.addWidget(header_group)

        # Form Pilih Produk
        produk_group = QGroupBox("Pilih Produk")
        produk_layout = QHBoxLayout()

        self.combo_produk = QComboBox()
        self.combo_produk.setMinimumWidth(250)
        self.combo_produk.currentIndexChanged.connect(self.on_produk_changed)

        self.lbl_harga = QLabel("Rp 0")
        self.lbl_harga.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.spin_jumlah = QSpinBox()
        self.spin_jumlah.setRange(1, 9999)
        self.spin_jumlah.setValue(1)
        self.spin_jumlah.valueChanged.connect(self.update_subtotal_preview)

        self.lbl_subtotal_preview = QLabel("Rp 0")
        self.lbl_subtotal_preview.setStyleSheet("font-weight: bold; font-size: 14px; color: green;")

        btn_tambah_item = QPushButton("+ Tambah")
        btn_tambah_item.setStyleSheet("background-color: #2563eb; color: white; padding: 6px 12px;")
        btn_tambah_item.clicked.connect(self.tambah_ke_keranjang)

        produk_layout.addWidget(QLabel("Produk:"))
        produk_layout.addWidget(self.combo_produk)
        produk_layout.addWidget(QLabel("Harga:"))
        produk_layout.addWidget(self.lbl_harga)
        produk_layout.addWidget(QLabel("Qty:"))
        produk_layout.addWidget(self.spin_jumlah)
        produk_layout.addWidget(QLabel("Subtotal:"))
        produk_layout.addWidget(self.lbl_subtotal_preview)
        produk_layout.addWidget(btn_tambah_item)

        produk_group.setLayout(produk_layout)
        main_layout.addWidget(produk_group)

        # Tabel Keranjang
        self.table_cart = QTableWidget()
        self.table_cart.setColumnCount(6)
        self.table_cart.setHorizontalHeaderLabels([
            "ID Produk", "Nama Barang", "Harga", "Jumlah", "Subtotal", "Aksi"
        ])
        self.table_cart.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_cart.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_cart.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_cart.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_cart.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_cart.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table_cart.setEditTriggers(QAbstractItemView.NoEditTriggers)

        main_layout.addWidget(self.table_cart)

        # Total & Pembayaran
        bayar_group = QGroupBox("Pembayaran")
        bayar_layout = QFormLayout()

        self.lbl_total = QLabel("Rp 0")
        self.lbl_total.setStyleSheet("font-size: 22px; font-weight: bold; color: blue;")
        bayar_layout.addRow("Total Belanja:", self.lbl_total)

        self.spin_bayar = QDoubleSpinBox()
        self.spin_bayar.setRange(0, 999999999)
        self.spin_bayar.setDecimals(0)
        self.spin_bayar.setPrefix("Rp ")
        self.spin_bayar.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.spin_bayar.valueChanged.connect(self.hitung_kembalian)
        bayar_layout.addRow("Bayar:", self.spin_bayar)

        self.lbl_kembalian = QLabel("Rp 0")
        self.lbl_kembalian.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
        bayar_layout.addRow("Kembalian:", self.lbl_kembalian)

        bayar_group.setLayout(bayar_layout)
        main_layout.addWidget(bayar_group)

        # Tombol Aksi
        baris_tombol = QHBoxLayout()
        self.btn_proses = QPushButton("Proses Transaksi")
        self.btn_proses.setStyleSheet("background-color: green; color: white; font-size: 16px; padding: 10px;")
        self.btn_proses.clicked.connect(self.proses_transaksi)

        btn_batal = QPushButton("Batal")
        btn_batal.setStyleSheet("background-color: red; color: white; font-size: 16px; padding: 10px;")
        btn_batal.clicked.connect(self.reject)

        baris_tombol.addWidget(self.btn_proses)
        baris_tombol.addWidget(btn_batal)
        main_layout.addLayout(baris_tombol)

    def generate_nomor_transaksi(self):
        tgl_str = datetime.now().strftime("%Y%m%d")
        prefix = f"TRX-{tgl_str}-"
        try:
            db = koneksi_database()
            cursor = db.cursor()
            query = "SELECT COUNT(*) FROM transactions WHERE nomor_transaksi LIKE %s"
            cursor.execute(query, (f"{prefix}%",))
            count = cursor.fetchone()[0]
            cursor.close()
            db.close()
            nomor = f"{prefix}{count + 1:04d}"
        except Exception:
            nomor = f"{prefix}0001"
        self.lbl_nomor_trx.setText(nomor)

    def load_produk(self):
        try:
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id, kode_barang, nama_barang, harga, stok FROM products ORDER BY nama_barang ASC")
            daftar = cursor.fetchall()
            cursor.close()
            db.close()

            self.combo_produk.clear()
            for prod in daftar:
                label = f"{prod['nama_barang']} (Stok: {prod['stok']})"
                self.combo_produk.addItem(label, prod)

            self.on_produk_changed()
        except Exception as e:
            QMessageBox.warning(self, "Error Database", f"Gagal memuat produk:\n{e}")

    def on_produk_changed(self):
        prod = self.combo_produk.currentData()
        if prod:
            harga = float(prod["harga"])
            self.lbl_harga.setText(f"Rp {harga:,.0f}".replace(",", "."))
            self.update_subtotal_preview()

    def update_subtotal_preview(self):
        prod = self.combo_produk.currentData()
        if prod:
            harga = float(prod["harga"])
            qty = self.spin_jumlah.value()
            subtotal = harga * qty
            self.lbl_subtotal_preview.setText(f"Rp {subtotal:,.0f}".replace(",", "."))

    def tambah_ke_keranjang(self):
        prod = self.combo_produk.currentData()
        if not prod:
            QMessageBox.warning(self, "Peringatan", "Pilih produk terlebih dahulu.")
            return

        qty = self.spin_jumlah.value()
        stok_tersedia = prod["stok"]

        # Cek apakah produk sudah ada di keranjang
        existing_item = next((item for item in self.cart_items if item["product_id"] == prod["id"]), None)
        total_qty_di_cart = (existing_item["jumlah"] if existing_item else 0) + qty

        if total_qty_di_cart > stok_tersedia:
            QMessageBox.warning(
                self,
                "Stok Tidak Cukup",
                f"Stok produk '{prod['nama_barang']}' hanya tersedia {stok_tersedia}."
            )
            return

        harga = float(prod["harga"])

        if existing_item:
            existing_item["jumlah"] += qty
            existing_item["subtotal"] = existing_item["jumlah"] * harga
        else:
            self.cart_items.append({
                "product_id": prod["id"],
                "nama_barang": prod["nama_barang"],
                "kode_barang": prod["kode_barang"],
                "harga": harga,
                "jumlah": qty,
                "subtotal": harga * qty
            })

        self.refresh_cart_table()

    def refresh_cart_table(self):
        self.table_cart.setRowCount(0)
        total = 0.0

        for row, item in enumerate(self.cart_items):
            self.table_cart.insertRow(row)
            self.table_cart.setItem(row, 0, QTableWidgetItem(str(item["product_id"])))
            self.table_cart.setItem(row, 1, QTableWidgetItem(str(item["nama_barang"])))
            self.table_cart.setItem(row, 2, QTableWidgetItem(f"Rp {item['harga']:,.0f}".replace(",", ".")))
            self.table_cart.setItem(row, 3, QTableWidgetItem(str(item["jumlah"])))
            self.table_cart.setItem(row, 4, QTableWidgetItem(f"Rp {item['subtotal']:,.0f}".replace(",", ".")))

            btn_hapus = QPushButton("Hapus")
            btn_hapus.setStyleSheet("background-color: darkred; color: white; padding: 2px 6px;")
            btn_hapus.clicked.connect(lambda _, r=row: self.hapus_item_cart(r))
            self.table_cart.setCellWidget(row, 5, btn_hapus)

            total += item["subtotal"]

        self.lbl_total.setText(f"Rp {total:,.0f}".replace(",", "."))
        self.hitung_kembalian()

    def hapus_item_cart(self, index):
        if 0 <= index < len(self.cart_items):
            self.cart_items.pop(index)
            self.refresh_cart_table()

    def hitung_kembalian(self):
        total = sum(item["subtotal"] for item in self.cart_items)
        bayar = self.spin_bayar.value()
        kembalian = bayar - total
        if kembalian < 0:
            self.lbl_kembalian.setText(f"- Rp {abs(kembalian):,.0f}".replace(",", "."))
            self.lbl_kembalian.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
        else:
            self.lbl_kembalian.setText(f"Rp {kembalian:,.0f}".replace(",", "."))
            self.lbl_kembalian.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")

    def proses_transaksi(self):
        if not self.cart_items:
            QMessageBox.warning(self, "Peringatan", "Keranjang belanja masih kosong!")
            return

        total = sum(item["subtotal"] for item in self.cart_items)
        bayar = self.spin_bayar.value()

        if bayar < total:
            QMessageBox.warning(
                self,
                "Peringatan",
                f"Jumlah pembayaran kurang! Total: Rp {total:,.0f}, Bayar: Rp {bayar:,.0f}".replace(",", ".")
            )
            return

        kembalian = bayar - total
        nomor_trx = self.lbl_nomor_trx.text()

        try:
            db = koneksi_database()
            cursor = db.cursor()

            # Insert Header Transaksi
            query_trx = """
                INSERT INTO transactions (nomor_transaksi, user_id, total, bayar, kembalian)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_trx, (nomor_trx, self.user_id, total, bayar, kembalian))
            trx_id = cursor.lastrowid

            # Insert Detail Transaksi & Update Stok
            query_detail = """
                INSERT INTO transaction_details (transaction_id, product_id, harga, jumlah, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """
            query_update_stok = """
                UPDATE products SET stok = stok - %s WHERE id = %s
            """

            for item in self.cart_items:
                cursor.execute(query_detail, (
                    trx_id,
                    item["product_id"],
                    item["harga"],
                    item["jumlah"],
                    item["subtotal"]
                ))
                cursor.execute(query_update_stok, (item["jumlah"], item["product_id"]))

            db.commit()
            cursor.close()
            db.close()

            QMessageBox.information(
                self,
                "Transaksi Berhasil",
                f"Transaksi '{nomor_trx}' berhasil disimpan!\nKembalian: Rp {kembalian:,.0f}".replace(",", ".")
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error Database", f"Gagal memproses transaksi:\n{e}")


class DialogDetailTransaksi(QDialog):
    def __init__(self, parent=None, transaction_id=None):
        super().__init__(parent)
        self.transaction_id = transaction_id
        self.setWindowTitle("Detail Transaksi")
        self.resize(650, 450)
        self.init_ui()
        self.load_detail()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_info = QLabel()
        self.lbl_info.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.lbl_info)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID Detail", "Kode Barang", "Nama Barang", "Harga", "Jumlah",
        ])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        btn_tutup = QPushButton("Tutup")
        btn_tutup.clicked.connect(self.accept)
        layout.addWidget(btn_tutup)

    def load_detail(self):
        try:
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)

            # Query Header Info
            cursor.execute("""
                SELECT t.*, u.nama AS nama_user
                FROM transactions t
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.id = %s
            """, (self.transaction_id,))
            trx = cursor.fetchone()

            if trx:
                tgl_format = trx["tanggal"].strftime("%Y-%m-%d %H:%M:%S") if trx["tanggal"] else "-"
                info_text = (
                    f"No. Transaksi: {trx['nomor_transaksi']}  |  Tanggal: {tgl_format}\n"
                    f"User: {trx.get('nama_user') or trx['user_id']}  |  "
                    f"Total: Rp {float(trx['total']):,.0f}  |  "
                    f"Bayar: Rp {float(trx['bayar']):,.0f}  |  "
                    f"Kembalian: Rp {float(trx['kembalian']):,.0f}".replace(",", ".")
                )
                self.lbl_info.setText(info_text)

            # Query Detail Items
            cursor.execute("""
                SELECT d.*, p.kode_barang, p.nama_barang
                FROM transaction_details d
                LEFT JOIN products p ON d.product_id = p.id
                WHERE d.transaction_id = %s
                ORDER BY d.id ASC
            """, (self.transaction_id,))
            details = cursor.fetchall()
            cursor.close()
            db.close()

            self.table.setRowCount(0)
            for row, d in enumerate(details):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(d["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(d["kode_barang"] or "-")))
                self.table.setItem(row, 2, QTableWidgetItem(str(d["nama_barang"] or "-")))
                harga = float(d["harga"])
                self.table.setItem(row, 3, QTableWidgetItem(f"Rp {harga:,.0f}".replace(",", ".")))
                self.table.setItem(row, 4, QTableWidgetItem(str(d["jumlah"])))

        except Exception as e:
            QMessageBox.warning(self, "Error Database", f"Gagal memuat detail transaksi:\n{e}")


class Transaksi(QWidget):
    def __init__(self, user_id=1):
        super().__init__()
        self.user_id = user_id

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)

        label_judul = QLabel("Data Transaksi")
        label_judul.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
        layout.addWidget(label_judul)

        baris_atas = QHBoxLayout()

        self.cari = QLineEdit()
        self.cari.setPlaceholderText("Cari Nomor Transaksi...")
        self.cari.setStyleSheet("""
            QLineEdit {
                color: black;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 4px;
            }
        """)
        self.setStyleSheet("""
            QLabel{
                color: black;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.cari.textChanged.connect(self.cari_transaksi)

        self.tambah = QPushButton("+ Transaksi Baru")
        self.tambah.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 6px 12px;")
        self.tambah.clicked.connect(self.tambah_transaksi)

        self.detail = QPushButton("Detail")
        self.detail.clicked.connect(self.lihat_detail)

        self.hapus = QPushButton("Hapus")
        self.hapus.setStyleSheet("background-color: red; color: white; padding: 6px 12px;")
        self.hapus.clicked.connect(self.hapus_transaksi)

        baris_atas.addWidget(self.cari)
        baris_atas.addWidget(self.tambah)
        baris_atas.addWidget(self.detail)
        baris_atas.addWidget(self.hapus)

        layout.setAlignment(Qt.AlignTop)
        layout.addLayout(baris_atas)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Nomor Transaksi",
            "Tanggal",
            "User ID",
            "Total",
            "Bayar",
            "Kembalian"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.doubleClicked.connect(self.lihat_detail)

        layout.addWidget(self.table)

        self.cari_transaksi("")
        self.setLayout(layout)

    def cari_transaksi(self, teks=""):
        try:
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)
            query = """
                SELECT t.id, t.nomor_transaksi, t.tanggal, t.user_id, u.nama AS nama_user,
                       t.total, t.bayar, t.kembalian
                FROM transactions t
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.nomor_transaksi LIKE %s
                ORDER BY t.id DESC
            """
            keyword = f"%{teks}%"
            cursor.execute(query, (keyword,))
            hasil = cursor.fetchall()
            self.table.setRowCount(0)

            for trx in hasil:
                baris = self.table.rowCount()
                self.table.insertRow(baris)
                self.table.setItem(baris, 0, QTableWidgetItem(str(trx["id"])))
                self.table.setItem(baris, 1, QTableWidgetItem(str(trx["nomor_transaksi"])))
                tgl = trx["tanggal"].strftime("%Y-%m-%d %H:%M:%S") if trx["tanggal"] else "-"
                self.table.setItem(baris, 2, QTableWidgetItem(tgl))
                user_name = trx["nama_user"] or str(trx["user_id"])
                self.table.setItem(baris, 3, QTableWidgetItem(user_name))
                total = float(trx["total"])
                self.table.setItem(baris, 4, QTableWidgetItem(f"Rp {total:,.0f}".replace(",", ".")))
                bayar = float(trx["bayar"])
                self.table.setItem(baris, 5, QTableWidgetItem(f"Rp {bayar:,.0f}".replace(",", ".")))
                kembalian = float(trx["kembalian"])
                self.table.setItem(baris, 6, QTableWidgetItem(f"Rp {kembalian:,.0f}".replace(",", ".")))

            cursor.close()
            db.close()
        except Exception as e:
            QMessageBox.warning(self, "Error Database", f"Gagal mengambil data transaksi:\n{e}")

    def tambah_transaksi(self):
        dialog = DialogTransaksiBaru(self, user_id=self.user_id)
        if dialog.exec() == QDialog.Accepted:
            self.cari_transaksi(self.cari.text())

    def lihat_detail(self):
        baris = self.table.currentRow()
        if baris < 0:
            QMessageBox.warning(self, "Peringatan", "Silakan pilih transaksi dari tabel terlebih dahulu.")
            return

        trx_id = self.table.item(baris, 0).text()
        dialog = DialogDetailTransaksi(self, transaction_id=trx_id)
        dialog.exec()

    def hapus_transaksi(self):
        baris = self.table.currentRow()
        if baris < 0:
            QMessageBox.warning(self, "Peringatan", "Silakan pilih transaksi yang ingin dihapus.")
            return

        trx_id = self.table.item(baris, 0).text()
        nomor_trx = self.table.item(baris, 1).text()

        konfirmasi = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus transaksi '{nomor_trx}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if konfirmasi == QMessageBox.Yes:
            try:
                db = koneksi_database()
                cursor = db.cursor()
                # Hapus detail dulu baru header (foreign key safety)
                cursor.execute("DELETE FROM transaction_details WHERE transaction_id = %s", (trx_id,))
                cursor.execute("DELETE FROM transactions WHERE id = %s", (trx_id,))
                db.commit()
                cursor.close()
                db.close()

                QMessageBox.information(self, "Berhasil", f"Transaksi '{nomor_trx}' berhasil dihapus.")
                self.cari_transaksi(self.cari.text())
            except Exception as e:
                QMessageBox.critical(self, "Error Database", f"Gagal menghapus transaksi:\n{e}")
