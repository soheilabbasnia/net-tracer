"""
NetTracer - Design System & Qt Style Sheets (QSS)
Faithfully implements the modern dark theme, colors, and typography from the HTML prototype.
"""

# Color Palette Constants
COLOR_BG_DARK = "#1a1b1e"       # Main Window Background
COLOR_CARD_DARK = "#25262a"     # Primary Card Background
COLOR_CARD_DARKER = "#1f2024"   # Nested Card & Section Background
COLOR_ACCENT = "#00d28a"        # Mint Green Accent
COLOR_ACCENT_HOVER = "#0add9d"  # Brighter Mint Green
COLOR_TEXT_MAIN = "#ffffff"     # High-contrast white
COLOR_TEXT_MUTED = "#9ca3af"    # Muted gray
COLOR_BORDER = "#2c2e33"        # Subtle outline
COLOR_BORDER_LIGHT = "rgba(255, 255, 255, 0.08)"
COLOR_PROGRESS_BG = "#374151"   # Progress bar / ring background track

APPLICATION_QSS = f"""
/* Global Reset */
QWidget {{
    font-family: 'Poppins', 'Segoe UI', 'Ubuntu', sans-serif;
    color: {COLOR_TEXT_MAIN};
    background-color: transparent;
    font-size: 13px;
}}

QMainWindow {{
    background-color: {COLOR_BG_DARK};
}}

/* Custom Scrollbars matching prototype */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px 0px 0px 0px;
}}

QScrollBar::handle:vertical {{
    background: {COLOR_PROGRESS_BG};
    min-height: 24px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLOR_ACCENT};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
    background: none;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

/* Pill Action Buttons (Suspend, Export) */
QPushButton.pill-btn {{
    background-color: {COLOR_ACCENT};
    color: {COLOR_BG_DARK};
    font-weight: 700;
    font-size: 13px;
    border-radius: 20px;
    padding: 10px 18px;
    border: none;
}}

QPushButton.pill-btn:hover {{
    background-color: {COLOR_ACCENT_HOVER};
}}

QPushButton.pill-btn:pressed {{
    background-color: #00b074;
}}

/* Secondary / Subtle Buttons */
QPushButton.subtle-btn {{
    background-color: rgba(255, 255, 255, 0.05);
    color: {COLOR_TEXT_MUTED};
    font-size: 11px;
    font-weight: 600;
    border-radius: 14px;
    padding: 6px 14px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}}

QPushButton.subtle-btn:hover {{
    background-color: rgba(255, 255, 255, 0.1);
    color: {COLOR_TEXT_MAIN};
    border: 1px solid rgba(255, 255, 255, 0.18);
}}

/* Form Controls: QSpinBox (for Quota GB) */
QSpinBox, QDoubleSpinBox {{
    background-color: {COLOR_BG_DARK};
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    color: {COLOR_TEXT_MAIN};
    padding: 4px 8px;
    font-size: 13px;
    font-weight: 600;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {COLOR_ACCENT};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    width: 0px;
    border: none;
}}

/* Form Controls: QComboBox (for Data Retention) */
QComboBox {{
    background-color: {COLOR_BG_DARK};
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    color: {COLOR_TEXT_MAIN};
    padding: 8px 32px 8px 16px;
    font-size: 13px;
    font-weight: 500;
    min-width: 110px;
}}

QComboBox:hover {{
    border: 1px solid rgba(255, 255, 255, 0.25);
}}

QComboBox:focus {{
    border: 1px solid {COLOR_ACCENT};
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border: none;
}}

QComboBox::down-arrow {{
    width: 0px;
    height: 0px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {COLOR_TEXT_MUTED};
    margin-right: 12px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLOR_CARD_DARK};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    color: {COLOR_TEXT_MAIN};
    selection-background-color: {COLOR_ACCENT};
    selection-color: {COLOR_BG_DARK};
    padding: 4px;
}}

/* Tooltips */
QToolTip {{
    background-color: {COLOR_CARD_DARK};
    color: {COLOR_TEXT_MAIN};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 11px;
}}
"""
