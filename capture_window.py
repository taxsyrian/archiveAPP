import sys, os, cv2
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QMessageBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

class CaptureWindow(QWidget):
    path_ready = pyqtSignal(str, bytes)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("📷 تصوير مباشر")
        self.setup_ui()
        self.start_camera()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.image_label = QLabel("🎥 بث مباشر من الكاميرا")
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        capture_btn = QPushButton("📸 التقاط الصورة")
        capture_btn.clicked.connect(self.capture_image)
        layout.addWidget(capture_btn)

        self.setLayout(layout)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).scaled(800, 600, Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)

    def generate_image_path(self):
        folder = "images"
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.jpg"
        return os.path.join(folder, filename)

    def capture_image(self):
        if not hasattr(self, 'current_frame'):
            QMessageBox.warning(self, "⚠️ خطأ", "لم يتم التقاط أي إطار من الكاميرا.")
            return
        img_path = self.generate_image_path()
        cv2.imwrite(img_path, self.current_frame)
        with open(img_path, 'rb') as f:
            image_bytes = f.read()
        self.path_ready.emit(os.path.abspath(img_path), image_bytes)
        QMessageBox.information(self, "✅ تم الالتقاط", f"تم حفظ الصورة في:\n{img_path}")

    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    capture_window = CaptureWindow()
    capture_window.show()
    sys.exit(app.exec_())
