from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLineEdit, QPushButton, QLabel, QMessageBox, QCheckBox
from PySide6.QtCore import Qt

class BrokerLoginDialog(QDialog):
    def __init__(self, broker_manager, parent=None):
        super().__init__(parent)
        self.broker_manager = broker_manager
        self.setWindowTitle("Broker Login")
        self.setFixedSize(300, 300)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.broker_combo = QComboBox()
        self.broker_combo.addItems(["Dhan", "Zerodha", "Angel", "Fyers"])
        layout.addWidget(QLabel("Select Broker:"))
        layout.addWidget(self.broker_combo)
        
        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("Client ID / API Key")
        layout.addWidget(self.client_id_input)
        
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Access Token / Secret")
        self.token_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.token_input)
        
        self.remember_cb = QCheckBox("Remember Login")
        layout.addWidget(self.remember_cb)
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self._handle_login)
        layout.addWidget(self.login_btn)
        
    def _handle_login(self):
        broker_name = self.broker_combo.currentText().lower()
        if not self.broker_manager.initialize_broker(broker_name):
            QMessageBox.critical(self, "Error", f"Failed to initialize {broker_name}.")
            return
            
        credentials = {
            "client_id": self.client_id_input.text(),
            "api_key": self.client_id_input.text(),
            "app_id": self.client_id_input.text(),
            "access_token": self.token_input.text(),
            "auth_token": self.token_input.text()
        }
        
        success = self.broker_manager.login_active_broker(credentials)
        if success:
            if self.remember_cb.isChecked():
                self.broker_manager.security_manager.store_token(broker_name, credentials)
            QMessageBox.information(self, "Success", "Logged in successfully.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Authentication failed.")
