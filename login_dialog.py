from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
from users import UserManager

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserManager()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('文件管理器 - 登录')
        self.setGeometry(300, 300, 400, 500)
        self.setWindowFlags(Qt.WindowCloseButtonHint)  # 只显示关闭按钮
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                min-height: 25px;
            }
            QPushButton {
                padding: 8px 20px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton#registerBtn {
                background-color: #4CAF50;
            }
            QPushButton#registerBtn:hover {
                background-color: #388E3C;
            }
            QLabel {
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 30, 40, 40)
        
        # Logo和标题
        title_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap('logo.png')  # 你需要准备一个logo图片
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_layout.addWidget(logo_label)
        
        title_label = QLabel('文件管理器')
        title_label.setFont(QFont('Arial', 24, QFont.Bold))
        title_label.setStyleSheet('color: #333;')
        title_layout.addWidget(title_label)
        title_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(title_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet('background-color: #ddd;')
        layout.addWidget(line)
        
        # 添加一些空间
        layout.addSpacing(20)
        
        # 用户名输入
        username_label = QLabel('用户名')
        layout.addWidget(username_label)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText('请输入用户名')
        layout.addWidget(self.username_edit)
        
        # 密码输入
        password_label = QLabel('密码')
        layout.addWidget(password_label)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText('请输入密码')
        layout.addWidget(self.password_edit)
        
        # 添加一些空间
        layout.addSpacing(20)
        
        # 登录按钮
        login_button = QPushButton('登录')
        login_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(login_button)
        
        # 注册按钮
        register_button = QPushButton('注册新用户')
        register_button.setObjectName('registerBtn')
        register_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(register_button)
        
        # 版权信息
        copyright_label = QLabel('© 2024 File Manager. All rights reserved.')
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet('color: #666; font-size: 12px;')
        layout.addWidget(copyright_label)
        
        # 连接信号
        login_button.clicked.connect(self.login)
        register_button.clicked.connect(self.register)
        self.password_edit.returnPressed.connect(self.login)
        
    def login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(self, '提示', '请输入用户名和密码',
                              QMessageBox.Ok, QMessageBox.Ok)
            return
            
        if self.user_manager.verify_user(username, password):
            self.accept()
        else:
            QMessageBox.warning(self, '错误', '用户名或密码错误',
                              QMessageBox.Ok, QMessageBox.Ok)
            self.password_edit.clear()
            
    def register(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(self, '提示', '请输入用户名和密码',
                              QMessageBox.Ok, QMessageBox.Ok)
            return
            
        if len(password) < 6:
            QMessageBox.warning(self, '提示', '密码长度不能少于6位',
                              QMessageBox.Ok, QMessageBox.Ok)
            return
            
        if self.user_manager.add_user(username, password):
            QMessageBox.information(self, '成功', '注册成功！请使用新账号登录',
                                  QMessageBox.Ok, QMessageBox.Ok)
            self.username_edit.clear()
            self.password_edit.clear()
        else:
            QMessageBox.warning(self, '错误', '用户名已存在',
                              QMessageBox.Ok, QMessageBox.Ok) 