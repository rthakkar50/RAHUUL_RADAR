from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QComboBox, QPushButton, QFormLayout, QFrame
from PySide6.QtCore import Qt, QTimer
from ui.styles import CARD_BG, BTN_BLUE
from core.config_manager import ConfigManager

class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("SETTINGS")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        card = QFrame()
        card.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 8px;")
        form = QFormLayout(card)
        form.setContentsMargins(20, 20, 20, 20)
        form.setSpacing(20)
        
        self.inp_cap = QLineEdit()
        self.inp_cap.setStyleSheet("background-color: #161B22; color: #E6EDF3; padding: 8px; border: 1px solid #30363D; border-radius: 4px;")
        form.addRow("Capital", self.inp_cap)
        
        self.spin_risk = QSpinBox()
        self.spin_risk.setRange(1, 100)
        self.spin_risk.setSuffix("%")
        self.spin_risk.setStyleSheet("background-color: #161B22; color: #E6EDF3; padding: 8px; border: 1px solid #30363D; border-radius: 4px;")
        form.addRow("Risk", self.spin_risk)
        
        self.spin_hold = QSpinBox()
        self.spin_hold.setRange(1, 365)
        self.spin_hold.setStyleSheet("background-color: #161B22; color: #E6EDF3; padding: 8px; border: 1px solid #30363D; border-radius: 4px;")
        form.addRow("Holding Days", self.spin_hold)
        
        self.combo_yahoo = QComboBox()
        self.combo_yahoo.addItems(["Auto", "1 Min", "5 Min", "15 Min"])
        self.combo_yahoo.setStyleSheet("background-color: #161B22; color: #E6EDF3; padding: 8px; border: 1px solid #30363D; border-radius: 4px;")
        form.addRow("Scanner Refresh", self.combo_yahoo)
        
        self.combo_provider = QComboBox()
        self.combo_provider.addItems(["Yahoo Finance", "Dhan API"])
        self.combo_provider.setStyleSheet("background-color: #161B22; color: #E6EDF3; padding: 8px; border: 1px solid #30363D; border-radius: 4px;")
        form.addRow("Data Provider", self.combo_provider)
        
        self.inp_dhan_client = QLineEdit()
        self.inp_dhan_client.setPlaceholderText("Dhan Client ID")
        self.inp_dhan_client.setStyleSheet("background-color: #161B22; color: #E6EDF3; padding: 8px; border: 1px solid #30363D; border-radius: 4px;")
        form.addRow("Dhan Client ID", self.inp_dhan_client)
        
        self.inp_dhan_token = QLineEdit()
        self.inp_dhan_token.setPlaceholderText("Dhan Access Token")
        self.inp_dhan_token.setEchoMode(QLineEdit.Password)
        self.inp_dhan_token.setStyleSheet("background-color: #161B22; color: #E6EDF3; padding: 8px; border: 1px solid #30363D; border-radius: 4px;")
        form.addRow("Dhan Access Token", self.inp_dhan_token)
        
        # Telegram Settings
        warning_lbl = QLabel("⚠️ API Keys are saved securely to .env file")
        warning_lbl.setStyleSheet("color: #D29922; font-size: 12px; font-style: italic;")
        form.addRow("", warning_lbl)

        self.inp_tg_token = QLineEdit()
        self.inp_tg_token.setPlaceholderText("Enter Telegram Bot Token")
        self.inp_tg_token.setEchoMode(QLineEdit.Password)
        self.inp_tg_token.setStyleSheet("background-color: #161B22; color: #E6EDF3; padding: 8px; border: 1px solid #30363D; border-radius: 4px;")
        form.addRow("Telegram Token", self.inp_tg_token)
        
        self.inp_tg_chat = QLineEdit()
        self.inp_tg_chat.setPlaceholderText("Enter Chat ID")
        self.inp_tg_chat.setStyleSheet("background-color: #161B22; color: #E6EDF3; padding: 8px; border: 1px solid #30363D; border-radius: 4px;")
        form.addRow("Telegram Chat ID", self.inp_tg_chat)
        
        layout.addWidget(card)
        
        self.btn_save = QPushButton("Save Settings")
        self.btn_save.setStyleSheet("background-color: #238636; color: white; font-weight: bold; padding: 10px 16px; border-radius: 4px; margin-top: 10px;")
        self.btn_save.clicked.connect(self.save_settings)
        layout.addWidget(self.btn_save, alignment=Qt.AlignRight)
        
        layout.addStretch()
        
        self.load_settings()
        
    def load_settings(self):
        config = self.config_manager.load_config()
        self.inp_cap.setText(str(config.get("capital", "100000")))
        self.spin_risk.setValue(config.get("risk_pct", 1))
        self.spin_hold.setValue(config.get("holding_days", 45))
        
        yahoo = config.get("yahoo_refresh", "Auto")
        idx = self.combo_yahoo.findText(yahoo)
        if idx >= 0:
            self.combo_yahoo.setCurrentIndex(idx)
            
        provider = config.get("data_provider", "yahoo")
        p_idx = 1 if provider == "dhan" else 0
        self.combo_provider.setCurrentIndex(p_idx)
        
        def mask(val):
            if not val: return ""
            return "********" + val[-4:] if len(val) > 8 else "********"
            
        self.inp_dhan_client.setText(config.get("dhan_client_id", ""))
        self.inp_dhan_token.setText(mask(config.get("dhan_access_token", "")))
            
        self.inp_tg_token.setText(mask(config.get("telegram_token", "")))
        self.inp_tg_chat.setText(config.get("telegram_chat_id", ""))
            
    def save_settings(self):
        config = {
            "capital": self.inp_cap.text(),
            "risk_pct": self.spin_risk.value(),
            "holding_days": self.spin_hold.value(),
            "yahoo_refresh": self.combo_yahoo.currentText(),
            "data_provider": "dhan" if self.combo_provider.currentIndex() == 1 else "yahoo",
            "dhan_client_id": self.inp_dhan_client.text().strip(),
            "dhan_access_token": self.inp_dhan_token.text().strip(),
            "telegram_token": self.inp_tg_token.text().strip(),
            "telegram_chat_id": self.inp_tg_chat.text().strip()
        }
        self.config_manager.save_config(config)
        
        self.btn_save.setText("Saved!")
        QTimer.singleShot(2000, lambda: self.btn_save.setText("Save Settings"))
