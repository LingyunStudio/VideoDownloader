"""全局浅色现代风 QSS 样式。"""

QSS = """
* {
    font-family: "Microsoft YaHei UI", "Segoe UI", "PingFang SC", sans-serif;
    font-size: 13px;
    color: #1f2330;
}

QWidget#Root {
    background-color: #f4f6fb;
}

QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #e4e8f0;
    border-radius: 14px;
}
QFrame#CardRaised {
    background-color: #ffffff;
    border: 1px solid #dce2ee;
    border-radius: 14px;
}

QLabel { background: transparent; }

QLabel#Brand {
    font-size: 19px;
    font-weight: 700;
    color: #1f2330;
}
QLabel#Title {
    font-size: 19px;
    font-weight: 700;
    color: #1f2330;
}
QLabel#Subtitle { color: #6b7280; font-size: 12px; }
QLabel#MetaKey { color: #9aa1b1; font-size: 11px; }
QLabel#MetaVal { color: #374151; font-size: 12px; font-weight: 600; }
QLabel#Section {
    color: #6b7280;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
}
QLabel#Hint { color: #9aa1b1; font-size: 11px; }
QLabel#QueueEmpty { color: #b3b9c8; font-size: 12px; }

QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d8dee9;
    border-radius: 10px;
    padding: 11px 14px;
    selection-background-color: #3b6ef6;
}
QLineEdit:focus { border: 1px solid #3b6ef6; }

QPushButton {
    background-color: #3b6ef6;
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 600;
    color: #ffffff;
}
QPushButton:hover { background-color: #2f5fe0; }
QPushButton:pressed { background-color: #2954c4; }
QPushButton:disabled { background-color: #cdd5e3; color: #ffffff; }

QPushButton#Secondary {
    background-color: #ffffff;
    border: 1px solid #d8dee9;
    color: #374151;
}
QPushButton#Secondary:hover {
    background-color: #eef2fa;
    border: 1px solid #3b6ef6;
    color: #2f5fe0;
}

QPushButton#Danger {
    background-color: #fff1f3;
    border: 1px solid #f3c2cc;
    color: #e23e5b;
    padding: 6px 14px;
}
QPushButton#Danger:hover { background-color: #ffe0e5; color: #c92a45; }
QPushButton#Danger:disabled { color: #d8b8c0; border-color: #f0d8de; background-color: #fafafa; }

QComboBox {
    background-color: #ffffff;
    border: 1px solid #d8dee9;
    border-radius: 9px;
    padding: 8px 12px;
    min-height: 18px;
    min-width: 70px;
    color: #374151;
}
QComboBox:hover { border: 1px solid #3b6ef6; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #9aa1b1;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d8dee9;
    border-radius: 8px;
    selection-background-color: #3b6ef6;
    selection-color: #ffffff;
    outline: none;
    padding: 6px;
    color: #374151;
}

QCheckBox { spacing: 8px; background: transparent; color: #374151; }
QCheckBox::indicator {
    width: 18px; height: 18px;
    border-radius: 5px;
    border: 1px solid #c4ccda;
    background-color: #ffffff;
}
QCheckBox::indicator:hover { border: 1px solid #3b6ef6; }
QCheckBox::indicator:checked {
    background-color: #3b6ef6;
    border: 1px solid #3b6ef6;
}

QProgressBar {
    background-color: #e8ecf4;
    border: none;
    border-radius: 7px;
    height: 10px;
    text-align: center;
    color: transparent;
    font-size: 1px;
}
QProgressBar::chunk {
    background-color: #3b6ef6;
    border-radius: 7px;
}
QProgressBar#Done::chunk { background-color: #1aa260; }
QProgressBar#Error::chunk { background-color: #e23e5b; }

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e4e8f0;
    border-radius: 10px;
    gridline-color: #eef1f7;
    selection-background-color: #3b6ef6;
    selection-color: #ffffff;
    outline: none;
    alternate-background-color: #fafbfd;
}
QTableWidget::item { padding: 6px 8px; border: none; }
QHeaderView::section {
    background-color: #f4f6fb;
    color: #6b7280;
    border: none;
    border-right: 1px solid #e4e8f0;
    border-bottom: 1px solid #e4e8f0;
    padding: 7px 8px;
    font-weight: 700;
}

QScrollArea { background: transparent; border: none; }
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #cdd5e3;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #aab4c6; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }

QSplitter::handle { background-color: #f4f6fb; }
QSplitter::handle:horizontal { width: 3px; }

QStatusBar { background-color: #f4f6fb; color: #9aa1b1; }
QStatusBar QLabel { color: #9aa1b1; }

QFrame#Divider { background-color: #e4e8f0; max-height: 1px; }

QToolTip {
    background-color: #1f2330;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 5px 8px;
}
"""
