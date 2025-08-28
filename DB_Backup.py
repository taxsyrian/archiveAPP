import sys
import os
import zipfile
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog, QMessageBox
)
from ftplib import FTP

class BackupApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("إدارة النسخ الاحتياطية")
        self.setGeometry(300, 300, 400, 200)

        self.label = QLabel("اختر الإجراء المطلوب:", self)

        self.btn_backup = QPushButton("1️⃣ إنشاء نسخة احتياطية", self)
        self.btn_zip = QPushButton("2️⃣ ضغط النسخة", self)
        self.btn_upload = QPushButton("3️⃣ رفع إلى السيرفر", self)

        self.btn_backup.clicked.connect(self.create_backup)
        self.btn_zip.clicked.connect(self.compress_backup)
        self.btn_upload.clicked.connect(self.upload_backup)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_backup)
        layout.addWidget(self.btn_zip)
        layout.addWidget(self.btn_upload)
        self.setLayout(layout)

        self.sql_file = ""
        self.zip_file = ""

    def create_backup(self):
        user = "root"
        password = "your_password"
        db_name = "your_database"
        host = "localhost"

        folder = QFileDialog.getExistingDirectory(self, "اختر مجلد الحفظ")
        if not folder:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.sql_file = os.path.join(folder, f"{db_name}_backup_{timestamp}.sql")

        dump_command = f"mysqldump -h {host} -u {user} -p{password} {db_name} > \"{self.sql_file}\""
        result = os.system(dump_command)

        if result == 0:
            QMessageBox.information(self, "تم", f"تم إنشاء النسخة:\n{self.sql_file}")
        else:
            QMessageBox.critical(self, "خطأ", "فشل في إنشاء النسخة الاحتياطية.")

    def compress_backup(self):
        if not self.sql_file or not os.path.exists(self.sql_file):
            QMessageBox.warning(self, "تنبيه", "لم يتم العثور على ملف النسخة الاحتياطية.")
            return

        self.zip_file = self.sql_file.replace(".sql", ".zip")
        try:
            with zipfile.ZipFile(self.zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(self.sql_file, os.path.basename(self.sql_file))
            os.remove(self.sql_file)
            QMessageBox.information(self, "تم", f"تم ضغط الملف:\n{self.zip_file}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ في الضغط", str(e))

    def upload_backup(self):
        if not self.zip_file or not os.path.exists(self.zip_file):
            QMessageBox.warning(self, "تنبيه", "لم يتم العثور على ملف مضغوط للرفع.")
            return

        ftp_host = "your.ftp.server"
        ftp_user = "ftp_username"
        ftp_pass = "ftp_password"

        try:
            with FTP(ftp_host) as ftp:
                ftp.login(ftp_user, ftp_pass)
                with open(self.zip_file, 'rb') as f:
                    ftp.storbinary(f"STOR {os.path.basename(self.zip_file)}", f)
            QMessageBox.information(self, "نجاح", "تم رفع النسخة إلى السيرفر بنجاح.")
        except Exception as e:
            QMessageBox.critical(self, "خطأ في الرفع", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BackupApp()
    window.show()
    sys.exit(app.exec_())
