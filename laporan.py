from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDateEdit,
    QMessageBox
)

from PySide6.QtCore import QDate, Qt

from database.conn import koneksi_database


class Laporan(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)

        self.label = QLabel("Laporan Penjualan")
        layout.addWidget(self.label)

        baris_filter = QHBoxLayout()

        label_dari = QLabel("Dari tanggal:")
        self.tanggal_dari = QDateEdit()
        self.tanggal_dari.setCalendarPopup(True)
        self.tanggal_dari.setDate(QDate.currentDate())

        label_sampai = QLabel("Sampai:")

        self.tanggal_sampai = QDateEdit()
        self.tanggal_sampai.setCalendarPopup(True)
        self.tanggal_sampai.setDate(QDate.currentDate())

        self.tombol_tampil = QPushButton("Tampilkan")
        self.tombol_tampil.clicked.connect(self.tampilkan_laporan)

        baris_filter.addWidget(label_dari)
        baris_filter.addWidget(self.tanggal_dari)
        baris_filter.addWidget(label_sampai)
        baris_filter.addWidget(self.tanggal_sampai)
        baris_filter.addWidget(self.tombol_tampil)

        layout.addLayout(baris_filter)

        self.tabel = QTableWidget()
        self.tabel.setColumnCount(4)
        self.tabel.setHorizontalHeaderLabels([
            "ID",
            "Tanggal",
            "Total",
            "Nama Barang"
        ])

        self.tabel.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.tabel.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        self.tabel.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        self.tabel.horizontalHeader().setSectionResizeMode(3,QHeaderView.Stretch)

        layout.addWidget(self.tabel)

        self.total_label = QLabel("Total Penjualan: Rp 0")

        self.total_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: black;
            }
        """)

        layout.addWidget(self.total_label)

        self.label.setStyleSheet("""
            QLabel {
                color: black;
                font-size: 20px;
                font-weight: bold;
            }
        """)

        self.setStyleSheet("""
            QLabel{
                color: black;
                font-size: 16px;
                font-weight: bold;
            }
        """)

        self.setLayout(layout)

    def tampilkan_laporan(self):

        tanggal_dari = (self.tanggal_dari.date().toString("yyyy-MM-dd"))

        tanggal_sampai = (self.tanggal_sampai.date().toString("yyyy-MM-dd"))
        
        try:
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)
            query = """
                SELECT
                    t.id,
                    t.tanggal,
                    t.total,
                    GROUP_CONCAT(
                        p.nama_barang
                        SEPARATOR ', '
                    ) AS nama_barang
                FROM transactions t

                LEFT JOIN transaction_details td
                    ON t.id = td.transaction_id

                LEFT JOIN products p
                    ON td.product_id = p.id

                WHERE DATE(t.tanggal) BETWEEN %s AND %s

                GROUP BY
                    t.id,
                    t.tanggal,
                    t.total

                ORDER BY t.tanggal ASC
            """
            cursor.execute(query,(tanggal_dari,tanggal_sampai))
            data = cursor.fetchall()
            self.tabel.setRowCount(0)
            total_penjualan = 0

            for trx in data:

                baris = self.tabel.rowCount()

                self.tabel.insertRow(baris)

                # ID
                self.tabel.setItem(
                    baris,
                    0,
                    QTableWidgetItem(
                        str(trx["id"])
                    )
                )

                # Tanggal
                tgl = (
                    trx["tanggal"].strftime("%Y-%m-%d %H:%M:%S")
                    if trx["tanggal"]
                    else "-"
                )

                self.tabel.setItem(
                    baris,
                    1,
                    QTableWidgetItem(tgl)
                )

                # Total
                total = float(trx["total"])

                self.tabel.setItem(
                    baris,
                    2,
                    QTableWidgetItem(
                        f"Rp {total:,.0f}".replace(",", ".")
                    )
                )

                # Nama Barang
                nama_barang = trx["nama_barang"] or "-"

                self.tabel.setItem(
                    baris,
                    3,
                    QTableWidgetItem(nama_barang)
                )
                cursor.close()
                db.close()
            
        except Exception as e:
            QMessageBox.warning(self, "Error Database", f"Gagal mengambil laporan:\n{e}")