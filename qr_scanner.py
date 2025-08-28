
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QMessageBox, QApplication,
    QPushButton, QDialog, QProgressBar
)
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2
import sys

scanner = None

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("جاري التحضير...")
        self.setFixedSize(250, 100)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        layout = QVBoxLayout()
        label = QLabel("📷 يتم تشغيل الكاميرا...\n⏳ الرجاء وضع رمز QR أمام العدسة")
        label.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # وضع غير محدد

        layout.addWidget(label)
        layout.addWidget(self.progress)
        self.setLayout(layout)

class QRScannerWindow(QWidget):
    qr_saved = pyqtSignal(str)  # ✅ فقط البايتات

    def __init__(self):
        super().__init__()
        self.setWindowTitle("مسح QR")
        self.setGeometry(150, 150, 400, 300)

        self.label = QLabel("📸 عرض الكاميرا")
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()

        self.cap = cv2.VideoCapture(0)
        self.detector = cv2.QRCodeDetector()

        self.delay_timer = QTimer()
        self.delay_timer.setSingleShot(True)
        self.delay_timer.timeout.connect(self.start_scanning)
        self.delay_timer.start(3000)

    def start_scanning(self):
        self.loading_dialog.close()
        self.timer = QTimer()
        self.timer.timeout.connect(self.scan_frame)
        self.timer.start(100)

    def scan_frame(self):
        ret, frame = self.cap.read()
        if ret:
            data, bbox, _ = self.detector.detectAndDecode(frame)
            if data and bbox is not None and len(data.strip()) > 3:
                self.timer.stop()
                self.cap.release()

                bbox = bbox.astype(int)
                x, y, w, h = cv2.boundingRect(bbox)
                cropped_qr = frame[y:y+h, x:x+w]

                # تحويل الصورة إلى PNG بايتات باستخدام OpenCV
                success, encoded_image = cv2.imencode('.png', cropped_qr)
                if not success:
                    QMessageBox.warning(self, "خطأ", "فشل تحويل الصورة إلى بايتات PNG")
                    return

                qr_bytes = encoded_image.tobytes()

                reply = QMessageBox.question(
                    self,
                    "تأكيد المسح",
                    f"تم مسح الرمز:\n\n{data}\n\nهل تريد المتابعة؟",
                    QMessageBox.Yes | QMessageBox.Cancel
                )

                if reply == QMessageBox.Yes:
                    print("✅ تم تمرير بايتات صورة QR")
                    self.qr_saved.emit(data)
                    self.close()
                else:
                    self.cap = cv2.VideoCapture(0)
                    self.loading_dialog.show()
                    self.delay_timer.start(3000)
                return

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        if self.cap.isOpened():
            self.cap.release()
        self.loading_dialog.close()
        event.accept()

# ✅ تجربة مستقلة
if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = QWidget()
    main_window.setWindowTitle("نافذة تجريبية")
    main_window.setGeometry(100, 100, 300, 200)

    layout = QVBoxLayout()
    label = QLabel("اضغط لبدء المسح")
    button = QPushButton("ابدأ المسح")

    def start_scanner():
        global scanner
        if scanner is None or not scanner.isVisible():
            scanner = QRScannerWindow()
            scanner.qr_saved.connect(lambda data: print("📦 حجم البايتات:", len(data)))
            scanner.show()
        else:
            QMessageBox.information(main_window, "تنبيه", "نافذة المسح مفتوحة بالفعل.")

    button.clicked.connect(start_scanner)

    layout.addWidget(label)
    layout.addWidget(button)
    main_window.setLayout(layout)
    main_window.show()

    sys.exit(app.exec_())
