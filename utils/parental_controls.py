import json
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QListWidget, QLineEdit, QLabel, QMessageBox

# Load or create parental controls settings
def load_parental_controls():
    try:
        with open('parental_controls.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create the file with default settings
        default_settings = {
            "blocked_websites": [],
            "allowed_websites": []
        }
        with open('parental_controls.json', 'w') as f:
            json.dump(default_settings, f, indent=2)
        return default_settings

# Save parental controls settings
def save_parental_controls(settings):
    with open('parental_controls.json', 'w') as f:
        json.dump(settings, f, indent=2)

# Global variables for blocked and allowed websites
settings = load_parental_controls()
blocked_websites = settings.get("blocked_websites", [])
allowed_websites = settings.get("allowed_websites", [])

class ParentalControlsDialog(QDialog):
    def __init__(self, history, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parental Controls")
        self.setGeometry(200, 200, 400, 300)
        
        self.history = history
        
        # Layout
        layout = QVBoxLayout()
        
        # View Browsing History
        self.history_label = QLabel("Browsing History:")
        self.history_list = QListWidget()
        self.update_history_list()
        layout.addWidget(self.history_label)
        layout.addWidget(self.history_list)
        
        # Block/Allow Websites
        self.block_label = QLabel("Block/Allow Websites:")
        self.block_input = QLineEdit()
        self.block_input.setPlaceholderText("Enter website URL to block/allow")
        self.block_button = QPushButton("Block Website")
        self.block_button.clicked.connect(self.block_website)
        self.allow_button = QPushButton("Allow Website")
        self.allow_button.clicked.connect(self.allow_website)
        layout.addWidget(self.block_label)
        layout.addWidget(self.block_input)
        layout.addWidget(self.block_button)
        layout.addWidget(self.allow_button)
        
        self.setLayout(layout)
    
    def update_history_list(self):
        """Update the browsing history list."""
        self.history_list.clear()
        for entry in self.history:
            self.history_list.addItem(f"{entry['timestamp']} - {entry['title']} ({entry['url']})")
    
    def block_website(self):
        """Block a website."""
        url = self.block_input.text().strip()
        if url:
            if url not in blocked_websites:
                blocked_websites.append(url)
                save_parental_controls({
                    "blocked_websites": blocked_websites,
                    "allowed_websites": allowed_websites
                })
                QMessageBox.information(self, "Blocked", f"{url} has been blocked.")
            else:
                QMessageBox.warning(self, "Already Blocked", f"{url} is already blocked.")
        else:
            QMessageBox.warning(self, "Error", "Please enter a valid URL.")
    
    def allow_website(self):
        """Allow a website."""
        url = self.block_input.text().strip()
        if url:
            if url in blocked_websites:
                blocked_websites.remove(url)
                save_parental_controls({
                    "blocked_websites": blocked_websites,
                    "allowed_websites": allowed_websites
                })
                QMessageBox.information(self, "Allowed", f"{url} has been allowed.")
            else:
                QMessageBox.warning(self, "Not Blocked", f"{url} is not in the blocked list.")
        else:
            QMessageBox.warning(self, "Error", "Please enter a valid URL.")