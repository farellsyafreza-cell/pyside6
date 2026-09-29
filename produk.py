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
    QMessageBox
)
from PySide6.QtCore import Qt
from database.conn import koneksi_database

class Produk(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)

        self.label=QLabel("Halaman Data Produk")
        self.cari=QLineEdit()
        self.cari.setPlaceholderText("Cari Produk...")
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.label)
        layout.addWidget(self.cari)
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
        layout.addWidget(self.table)
        self.cari.textChanged.connect(self.cari_barang)
        self.cari_barang("")
        self.setLayout(layout)

        self.label.setStyleSheet("""
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