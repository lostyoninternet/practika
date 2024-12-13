DARK_THEME = """
QWidget {
    background-color: #2D2D2D;
    color: #FFFFFF;
    font-size: 12px;
}

QLabel {
    color: #FFFFFF;
    padding: 5px;
}

QPushButton {
    background-color: #007ACC;
    border: none;
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #005999;
}

QPushButton:pressed {
    background-color: #003366;
}

QComboBox {
    background-color: #3D3D3D;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px;
    min-width: 100px;
}

QComboBox:hover {
    border: 1px solid #007ACC;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: url(down_arrow.png);
    width: 12px;
    height: 12px;
}

QSpinBox, QDoubleSpinBox {
    background-color: #3D3D3D;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px;
    min-width: 80px;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border: 1px solid #007ACC;
}

QDateEdit {
    background-color: #3D3D3D;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px;
    min-width: 100px;
}

QDateEdit:hover {
    border: 1px solid #007ACC;
}

QRadioButton {
    spacing: 8px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
}

QRadioButton::indicator:unchecked {
    background-color: #3D3D3D;
    border: 2px solid #555555;
    border-radius: 8px;
}

QRadioButton::indicator:checked {
    background-color: #007ACC;
    border: 2px solid #007ACC;
    border-radius: 8px;
}

QGroupBox {
    border: 1px solid #555555;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #F5F5F5;
    color: #2D2D2D;
    font-size: 12px;
}

QLabel {
    color: #2D2D2D;
    padding: 5px;
}

QPushButton {
    background-color: #007ACC;
    border: none;
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #005999;
}

QPushButton:pressed {
    background-color: #003366;
}

QComboBox {
    background-color: white;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 5px;
    min-width: 100px;
}

QComboBox:hover {
    border: 1px solid #007ACC;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: url(down_arrow.png);
    width: 12px;
    height: 12px;
}

QSpinBox, QDoubleSpinBox {
    background-color: white;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 5px;
    min-width: 80px;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border: 1px solid #007ACC;
}

QDateEdit {
    background-color: white;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 5px;
    min-width: 100px;
}

QDateEdit:hover {
    border: 1px solid #007ACC;
}

QRadioButton {
    spacing: 8px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
}

QRadioButton::indicator:unchecked {
    background-color: white;
    border: 2px solid #CCCCCC;
    border-radius: 8px;
}

QRadioButton::indicator:checked {
    background-color: #007ACC;
    border: 2px solid #007ACC;
    border-radius: 8px;
}

QGroupBox {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
}
"""
