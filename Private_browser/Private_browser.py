#!/usr/bin/env python3
import sys
from PyQt6.QtCore import QUrl, Qt, QEvent  # Added QEvent for Type.KeyPress
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar,
    QWidget, QVBoxLayout, QPushButton
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile, QWebEngineSettings, QWebEnginePage
)

class PrivateDevBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultra-Private Dev Browser (Qt6)")
        self.resize(1200, 750)

        # === 1. Off-the-record profile (zero persistence) ===
        self.profile = QWebEngineProfile("NO-PERSISTENCE", self)
        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
        self.profile.setPersistentStoragePath("")   # kills localStorage, IndexedDB, etc.

        # === 2. Main page ===
        self.page = QWebEnginePage(self.profile, self)
        settings = self.page.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, False)

        # === 3. Main browser view ===
        self.browser = QWebEngineView()
        self.browser.setPage(self.page)
        self.browser.load(QUrl("https://duckduckgo.com"))

        # === 4. DevTools view (created early!) ===
        self.devtools_view = QWebEngineView()
        self.devtools_view.resize(950, 700)
        self.devtools_view.setWindowTitle("Developer Tools")
        self.page.setDevToolsPage(self.devtools_view.page())   # ← crucial line

        # === 5. URL bar & navigation ===
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search with DuckDuckGo…")
        self.url_bar.returnPressed.connect(self.navigate)
        self.browser.urlChanged.connect(lambda u: self.url_bar.setText(u.toString()))

        back_btn    = QAction("Back", self)
        forward_btn = QAction("Forward", self)
        reload_btn  = QAction("Reload", self)
        dev_btn     = QPushButton("DevTools")

        back_btn.triggered.connect(self.browser.back)
        forward_btn.triggered.connect(self.browser.forward)
        reload_btn.triggered.connect(self.browser.reload)
        dev_btn.clicked.connect(self.toggle_devtools)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction(back_btn)
        toolbar.addAction(forward_btn)
        toolbar.addAction(reload_btn)
        toolbar.addWidget(self.url_bar)
        toolbar.addWidget(dev_btn)
        self.addToolBar(toolbar)

        # Layout
        central = QWidget()
        lay = QVBoxLayout(central)
        lay.setContentsMargins(0,0,0,0)
        lay.setSpacing(0)
        lay.addWidget(self.browser)
        self.setCentralWidget(central)

        # === 6. F12 shortcut (works globally) ===
        self.installEventFilter(self)

    # ------------------------------------------------------------------
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_F12:
            self.toggle_devtools()
            return True
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------
    def navigate(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        if " " in text and "." not in text:
            url = f"https://duckduckgo.com/?q={QUrl.toPercentEncoding(text)}"
        elif not text.startswith(("http://", "https://", "file://")):
            url = "https://" + text
        else:
            url = text
        self.browser.load(QUrl(url))

    # ------------------------------------------------------------------
    def toggle_devtools(self):
        if self.devtools_view.isVisible():
            self.devtools_view.hide()
        else:
            self.devtools_view.show()
            self.devtools_view.raise_()
            self.devtools_view.setFocus()

# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Dark VS-Code-like theme (optional)
    app.setStyleSheet("""
        QMainWindow { background:#1e1e1e; }
        QToolBar    { background:#252526; border:none; }
        QLineEdit   { background:#2d2d30; color:#ccc; border:1px solid #444; padding:5px; }
        QPushButton { background:#0e639c; color:white; border:none; padding:6px 12px; }
        QPushButton:hover { background:#1177bb; }
    """)

    win = PrivateDevBrowser()
    win.show()
    sys.exit(app.exec())
