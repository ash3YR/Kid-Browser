import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QToolBar, 
                           QAction, QStatusBar, QMessageBox, QLabel, QVBoxLayout, 
                           QWidget)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, pyqtSlot, QTimer
from PyQt5.QtGui import QIcon
from datetime import datetime

# Import utility modules
from utils.content_filter import is_safe_url, profanity, blocked_websites, allowed_websites
from utils.history_manager import load_history, save_history
from utils.parental_controls import ParentalControlsDialog

class SafeWebPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            if not is_safe_url(url.toString()):
                QMessageBox.warning(None, "Access Denied", 
                    "This website is not safe for children!")
                return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class SafeBrowseJunior(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SafeBrowse Junior - AI Safe Internet Companion')
        self.setGeometry(100, 100, 1024, 768)
        
        # Initialize browsing history
        self.history = load_history()
        
        # Create main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create the safe web view
        self.browser = QWebEngineView()
        safe_page = SafeWebPage(self.browser)
        self.browser.setPage(safe_page)
        self.browser.setUrl(QUrl('https://www.kiddle.co'))  # Kid-safe search engine
        
        # Create child-friendly toolbar
        self.create_toolbar()
        
        # Add browser to layout
        layout.addWidget(self.browser)
        
        # Setup status bar
        self.setup_status_bar()
        
        # Connect signals
        self.browser.loadFinished.connect(self.on_load_finished)
        self.browser.urlChanged.connect(self.on_url_changed)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add child-friendly navigation buttons with icons
        back_btn = QAction(QIcon('resources/icons/back.png'), '←', self)
        back_btn.setToolTip('Go Back')
        back_btn.triggered.connect(self.browser.back)
        toolbar.addAction(back_btn)

        forward_btn = QAction(QIcon('resources/icons/forward.png'), '→', self)
        forward_btn.setToolTip('Go Forward')
        forward_btn.triggered.connect(self.browser.forward)
        toolbar.addAction(forward_btn)

        home_btn = QAction(QIcon('resources/icons/home.png'), '🏠', self)
        home_btn.setToolTip('Go Home')
        home_btn.triggered.connect(self.go_home)
        toolbar.addAction(home_btn)

        # Add URL bar with content filtering
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText('Type a website address')
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        # Add Parental Controls Button
        parental_controls_btn = QAction(QIcon('resources/icons/parental_controls.png'), '👪 Parental Controls', self)
        parental_controls_btn.setToolTip('Open Parental Controls')
        parental_controls_btn.triggered.connect(self.open_parental_controls)
        toolbar.addAction(parental_controls_btn)

    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add screen time tracker
        self.time_label = QLabel('Screen Time: 0 minutes')
        self.status_bar.addPermanentWidget(self.time_label)
        
        # Add safety indicator
        self.safety_indicator = QLabel('🛡️ Safe Mode Active')
        self.status_bar.addPermanentWidget(self.safety_indicator)

    def navigate_to_url(self):
        url = self.url_bar.text()
        
        # Add http if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Check URL safety before loading
        if is_safe_url(url):
            self.browser.setUrl(QUrl(url))
        else:
            QMessageBox.warning(self, "Safety Alert",
                "This website might not be safe for children!")
            self.url_bar.setText('')

    def go_home(self):
        self.browser.setUrl(QUrl('https://www.kiddle.co'))

    @pyqtSlot(bool)
    def on_load_finished(self, ok):
        if ok:
            # Log browsing activity
            self.log_activity()

    def log_activity(self):
        activity = {
            'timestamp': datetime.now().isoformat(),
            'url': self.browser.url().toString(),
            'title': self.browser.page().title()
        }
        self.history.append(activity)
        save_history(self.history)

    def on_url_changed(self, url):
        self.url_bar.setText(url.toString())

    def open_parental_controls(self):
        """Open the parental controls dialog."""
        dialog = ParentalControlsDialog(self.history, self)
        dialog.exec_()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('SafeBrowse Junior')
    
    window = SafeBrowseJunior()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()