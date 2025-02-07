import sys
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QToolBar, 
                           QAction, QProgressBar, QStatusBar, QMessageBox, 
                           QLabel, QVBoxLayout, QWidget)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, pyqtSlot
from PyQt5.QtGui import QIcon
import requests
from better_profanity import profanity
from datetime import datetime
import json

class SafeWebPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            # Check if URL is in allowed list
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
        self.history = []
        
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
        
        # Setup content filtering
        self.setup_content_filtering()
        
        # Create status bar with time limit indicator
        self.setup_status_bar()
        
        # Connect signals
        self.browser.loadFinished.connect(self.on_load_finished)
        self.browser.urlChanged.connect(self.on_url_changed)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add child-friendly navigation buttons with icons
        back_btn = QAction('←', self)
        back_btn.setToolTip('Go Back')
        back_btn.triggered.connect(self.browser.back)
        toolbar.addAction(back_btn)

        forward_btn = QAction('→', self)
        forward_btn.setToolTip('Go Forward')
        forward_btn.triggered.connect(self.browser.forward)
        toolbar.addAction(forward_btn)

        home_btn = QAction('🏠', self)
        home_btn.setToolTip('Go Home')
        home_btn.triggered.connect(self.go_home)
        toolbar.addAction(home_btn)

        # Add URL bar with content filtering
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText('Type a website address')
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

    def setup_content_filtering(self):
        # Load custom profanity filter
        profanity.load_censor_words()
        
        # Add custom blocked words and patterns
        self.blocked_patterns = [
            r'\b(drugs?|alcohol|gambling|violence)\b',
            r'\b(xxx|porn|adult|crime|boobs|melons|whiskers|cannons)\b',
            # Add more patterns as needed
        ]

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
            # Scan page content for inappropriate material
            self.browser.page().toHtml(self.check_page_content)
            
            # Log browsing activity
            self.log_activity()

    def check_page_content(self, html_content):
        # Check for inappropriate content
        clean_content = profanity.censor(html_content)
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                self.browser.setHtml(
                    "<h1>Content Blocked</h1><p>This page contains inappropriate content.</p>")
                return

        if clean_content != html_content:
            self.browser.setHtml(clean_content)

    def log_activity(self):
        activity = {
            'timestamp': datetime.now().isoformat(),
            'url': self.browser.url().toString(),
            'title': self.browser.page().title()
        }
        self.history.append(activity)
        
        # Save to file (you could also send to a parent's dashboard)
        with open('browsing_history.json', 'w') as f:
            json.dump(self.history, f, indent=2)

    def on_url_changed(self, url):
        self.url_bar.setText(url.toString())

def is_safe_url(url):
    # Basic URL safety check (expand this with a proper API/database)
    unsafe_keywords = ['adult', 'xxx', 'porn', 'gambling', 'violence']
    return not any(keyword in url.lower() for keyword in unsafe_keywords)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('SafeBrowse Junior')
    
    window = SafeBrowseJunior()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()