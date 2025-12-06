#!/usr/bin/env python3
import sys
import os
from datetime import datetime

# === DEBUG LOG ===
LOG_FILE = os.path.expanduser("~/private_browser_debug.log")
def log(msg):
    t = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{t}] {msg}\n")
    print(f"[LOG] {msg}")

log("=== BROWSER STARTED ===")
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-logging --log-level=3"

from PyQt6.QtCore import Qt, QUrl, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QStackedWidget, QPushButton, QFrame, QLabel
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut


class TabButton(QPushButton):
    """Tab button that can be closed with middle-click"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background: #1e1e1e;
                border-radius: 20px;
                border: none;
            }
            QPushButton:checked {
                background: #2d6abf;
            }
            QPushButton:hover:!checked {
                background: #333;
            }
            QPushButton:hover {
                border: 1px solid #555;
            }
        """)
        
    def mousePressEvent(self, event):
        """Handle mouse clicks including middle-click"""
        if event.button() == Qt.MouseButton.MiddleButton:
            # Emit a signal or directly call close if parent is available
            if hasattr(self, 'on_middle_click'):
                self.on_middle_click()
            event.accept()
        else:
            super().mousePressEvent(event)


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Private Browser")
        self.resize(1500, 900)
        
        # Store references
        self.tab_views = []  # QWebEngineView objects
        self.tab_buttons = []  # TabButton objects
        
        # Create private profile
        self.profile = QWebEngineProfile(self)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
        
        # Setup UI
        central = QWidget()
        self.setCentralWidget(central)
        main = QHBoxLayout(central)
        main.setContentsMargins(0,0,0,0)
        main.setSpacing(0)

        # LEFT RIBBON
        self.ribbon = QWidget()
        self.ribbon.setFixedWidth(56)
        self.ribbon.setStyleSheet("background:#0a0a0a; border-right:1px solid #222;")
        ribbon_layout = QVBoxLayout(self.ribbon)
        ribbon_layout.setContentsMargins(8,12,8,12)
        ribbon_layout.setSpacing(8)

        # Tabs container
        self.tabs_container = QVBoxLayout()
        self.tabs_container.setSpacing(8)
        ribbon_layout.addLayout(self.tabs_container)

        # + New Tab button
        self.newtab_btn = QPushButton("+")
        self.newtab_btn.setFixedSize(40,40)
        self.newtab_btn.setStyleSheet("""
            background:#2d6abf; color:white; border-radius:20px; font-size:24px; font-weight:bold;
            QPushButton:hover { background:#3a7af0; }
        """)
        self.newtab_btn.clicked.connect(self.add_tab)
        ribbon_layout.addStretch()
        ribbon_layout.addWidget(self.newtab_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        main.addWidget(self.ribbon)

        # MAIN AREA
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0,0,0,0)
        right_layout.setSpacing(0)

        # TOP BAR
        topbar = QWidget()
        topbar.setFixedHeight(56)
        topbar.setStyleSheet("background:#0f0f0f; border-bottom:1px solid #222;")
        top_layout = QHBoxLayout(topbar)
        top_layout.setContentsMargins(16,0,16,0)
        top_layout.setSpacing(12)

        # Navigation buttons
        btn_style = """
            QPushButton {
                background:rgba(255,255,255,0.08);
                color:white;
                border:none;
                border-radius:18px;
                font-size:18px;
                font-weight:bold;
            }
            QPushButton:hover {
                background:rgba(255,255,255,0.18);
            }
            QPushButton:disabled {
                opacity:0.3;
            }
        """
        
        self.back = QPushButton("←")
        self.back.setFixedSize(36,36)
        self.back.setStyleSheet(btn_style)
        
        self.forward = QPushButton("→")
        self.forward.setFixedSize(36,36)
        self.forward.setStyleSheet(btn_style)
        
        self.reload = QPushButton("↻")
        self.reload.setFixedSize(36,36)
        self.reload.setStyleSheet(btn_style)

        # URL bar
        self.url = QLineEdit()
        self.url.setPlaceholderText("Search or enter address…")
        self.url.setStyleSheet("""
            background:rgba(255,255,255,0.1);
            color:white;
            border:none;
            border-radius:18px;
            padding:0 16px;
        """)
        self.url.returnPressed.connect(self.navigate)
        
        # DevTools button (smaller, on right side)
        self.dev_tools_btn = QPushButton("🔧")
        self.dev_tools_btn.setFixedSize(32, 32)
        self.dev_tools_btn.setToolTip("Open Developer Tools (Ctrl+Shift+I)")
        self.dev_tools_btn.setStyleSheet("""
            QPushButton {
                background:rgba(255,255,255,0.08);
                color:#888;
                border:none;
                border-radius:16px;
                font-size:14px;
            }
            QPushButton:hover {
                background:rgba(255,255,255,0.15);
                color:#2d6abf;
            }
        """)
        self.dev_tools_btn.clicked.connect(self.toggle_dev_tools)

        top_layout.addWidget(self.back)
        top_layout.addWidget(self.forward)
        top_layout.addWidget(self.reload)
        top_layout.addWidget(self.url, 1)
        top_layout.addWidget(self.dev_tools_btn)

        right_layout.addWidget(topbar)
        
        # Tab content area
        self.stack = QStackedWidget()
        right_layout.addWidget(self.stack)
        main.addWidget(right)

        # Connect signals
        self.back.clicked.connect(self.navigate_back)
        self.forward.clicked.connect(self.navigate_forward)
        self.reload.clicked.connect(self.navigate_reload)
        self.stack.currentChanged.connect(self.update_ui)

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+Shift+I"), self).activated.connect(self.toggle_dev_tools)
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.add_tab)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.close_current_tab)
        
        # Disable context menu (right-click) for main window
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        
        # Add initial tab
        self.add_tab("https://duckduckgo.com")
        log("Browser initialized")

    # ===== NAVIGATION =====
    def navigate_back(self):
        if self.cur():
            self.cur().back()

    def navigate_forward(self):
        if self.cur():
            self.cur().forward()

    def navigate_reload(self):
        if self.cur():
            self.cur().reload()

    def cur(self):
        """Get current web view"""
        if self.stack.count() > 0:
            return self.stack.currentWidget()
        return None

    # ===== TAB MANAGEMENT =====
    def add_tab(self, url="https://duckduckgo.com"):
        """Add a new browser tab"""
        try:
            log(f"Adding tab: {url}")
            
            # Create web page and view
            page = QWebEnginePage(self.profile, self)
            page.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, False)
            
            view = QWebEngineView()
            view.setPage(page)
            
            # Disable right-click context menu on the web view
            view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            
            # Create tab button
            tab_button = TabButton()
            tab_button.clicked.connect(
                lambda: self.switch_to_tab(view, tab_button)
            )
            
            # Connect middle-click to close
            def close_on_middle_click():
                self.close_tab(view, tab_button)
            tab_button.on_middle_click = close_on_middle_click
            
            # Store references
            self.tab_views.append(view)
            self.tab_buttons.append(tab_button)
            
            # Add to UI
            self.tabs_container.addWidget(tab_button)
            self.stack.addWidget(view)
            
            # Set favicon
            view.iconChanged.connect(lambda icon: tab_button.setIcon(icon))
            
            # Connect signals
            view.urlChanged.connect(self.update_ui)
            view.loadFinished.connect(lambda ok: self.update_ui())
            
            # Load URL
            qurl = QUrl(url)
            if qurl.scheme() == "":
                qurl.setScheme("https")
            view.load(qurl)
            
            # Switch to new tab
            self.switch_to_tab(view, tab_button)
            log(f"Tab added. Total: {len(self.tab_views)}")
            
        except Exception as e:
            log(f"Error adding tab: {e}")

    def switch_to_tab(self, view, tab_button):
        """Switch to a specific tab"""
        if view and self.stack.indexOf(view) != -1:
            self.stack.setCurrentWidget(view)
            
            # Update tab button states
            for i, button in enumerate(self.tab_buttons):
                if i < len(self.tab_views):
                    button.setChecked(self.tab_views[i] == view)
            
            self.update_ui()

    def close_tab(self, view, tab_button):
        """Close a specific tab"""
        if len(self.tab_views) <= 1:
            log("Cannot close the last tab")
            return
            
        try:
            index = self.tab_views.index(view)
            
            # Remove from lists
            self.tab_views.pop(index)
            self.tab_buttons.pop(index)
            
            # Remove from UI
            self.stack.removeWidget(view)
            self.tabs_container.removeWidget(tab_button)
            
            # Clean up
            tab_button.deleteLater()
            view.deleteLater()
            
            # If we closed the current tab, switch to another
            if self.stack.count() > 0:
                new_index = min(index, self.stack.count() - 1)
                new_view = self.stack.widget(new_index)
                self.stack.setCurrentIndex(new_index)
                self.update_ui()
                
                # Update tab button states
                for i, button in enumerate(self.tab_buttons):
                    if i < len(self.tab_views):
                        button.setChecked(self.tab_views[i] == new_view)
            
            log(f"Tab closed. Remaining: {len(self.tab_views)}")
            
        except Exception as e:
            log(f"Error closing tab: {e}")

    def close_current_tab(self):
        """Close the currently active tab"""
        current_view = self.cur()
        if current_view:
            for i, view in enumerate(self.tab_views):
                if view == current_view and i < len(self.tab_buttons):
                    self.close_tab(view, self.tab_buttons[i])
                    break

    # ===== DEVELOPER TOOLS =====
    def toggle_dev_tools(self):
        """Toggle developer tools for current tab"""
        view = self.cur()
        if view:
            # Check if dev tools are already open
            if hasattr(view, '_dev_tools_window') and view._dev_tools_window:
                # Close dev tools
                view._dev_tools_window.close()
                view._dev_tools_window = None
                log("Developer Tools closed")
            else:
                # Open dev tools
                self.open_dev_tools(view)
    
    def open_dev_tools(self, view):
        """Open developer tools in a separate window"""
        try:
            # Create dev tools window
            dev_window = QMainWindow()
            dev_window.setWindowTitle(f"Developer Tools - {view.url().toString()[:50]}")
            dev_window.resize(1200, 700)
            
            # Disable context menu on dev tools window too
            dev_window.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            
            # Create web view for dev tools
            dev_view = QWebEngineView()
            dev_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            dev_window.setCentralWidget(dev_view)
            
            # Connect page's dev tools to the window
            view.page().setDevToolsPage(dev_view.page())
            view.page().triggerAction(QWebEnginePage.WebAction.InspectElement)
            
            # Store reference
            view._dev_tools_window = dev_window
            
            # Connect close event
            dev_window.destroyed.connect(
                lambda: setattr(view, '_dev_tools_window', None)
            )
            
            # Show window
            dev_window.show()
            log("Developer Tools opened")
            
        except Exception as e:
            log(f"Error opening dev tools: {e}")

    # ===== UI UPDATES =====
    def update_ui(self):
        """Update UI elements based on current tab"""
        view = self.cur()
        if view:
            try:
                # Update navigation buttons
                self.back.setEnabled(view.history().canGoBack())
                self.forward.setEnabled(view.history().canGoForward())
                
                # Update URL bar
                current_url = view.url().toString()
                self.url.setText(current_url)
                
                # Update dev tools button tooltip
                has_dev_tools = hasattr(view, '_dev_tools_window') and view._dev_tools_window
                self.dev_tools_btn.setText("🔧" if not has_dev_tools else "🛠️")
                self.dev_tools_btn.setToolTip(
                    "Close Developer Tools (Ctrl+Shift+I)" if has_dev_tools 
                    else "Open Developer Tools (Ctrl+Shift+I)"
                )
                
            except Exception as e:
                log(f"UI update error: {e}")

    def navigate(self):
        """Navigate to URL from address bar"""
        text = self.url.text().strip()
        if not text:
            return
        
        view = self.cur()
        if view:
            url = QUrl.fromUserInput(text)
            if url.scheme() == "":
                url.setScheme("https")
            view.load(url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Private Browser")
    
    win = Browser()
    win.show()
    
    sys.exit(app.exec())
