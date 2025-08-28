from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
import qrcode
from io import BytesIO
import sys

class QRDisplay(QWidget):
    qr_saved = pyqtSignal(QPixmap, bytes)  # إشارة لتمرير الصورة والبايتات

    def __init__(self, qr_text):
        super().__init__()
        self.setWindowTitle("عرض QR")
        self.setFixedSize(400, 450)

        self.qr_text = qr_text
        self.qr_pixmap = None
        self.qr_bytes = None

        # عنصر عرض QR
        self.qr_label = QLabel("جاري توليد QR...")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(300, 300)

        # زر حفظ
        self.save_button = QPushButton("حفظ QR وتمريره")
        self.save_button.clicked.connect(self.save_qr)

        layout = QVBoxLayout()
        layout.addWidget(self.qr_label)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

        # توليد QR مباشرة
        self.generate_qr()

    def generate_qr(self):
        if not self.qr_text:
            self.qr_label.setText("لا يوجد بيانات لتوليد QR")
            return

        qr_img = qrcode.make(self.qr_text)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        self.qr_bytes = buffer.getvalue()
        print(f"توليد QR للنص: {self.qr_text}")
        print(f"حجم البايتات: {len(self.qr_bytes)}")
        self.qr_pixmap = QPixmap()
        self.qr_pixmap.loadFromData(self.qr_bytes)

        if not self.qr_pixmap.loadFromData(self.qr_bytes):
            self.qr_label.setText("فشل تحميل صورة QR")
            return

        self.qr_label.setPixmap(self.qr_pixmap)

    def save_qr(self):
        print("تم الضغط على زر حفظ QR")

        # تمرير الصورة والبايتات عبر الإشارة
        self.qr_saved.emit(self.qr_pixmap, self.qr_bytes)
        self.close()  # إغلاق النافذة بعد التمرير (اختياري)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qrt="HH"
    qrd = QRDisplay(qrt)
    qrd.show()
    sys.exit(app.exec_())
