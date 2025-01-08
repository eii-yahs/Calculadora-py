from variables import (DARKER, DARKEST, PRIMARY, DARKER2, DARKEST2, PRIMARY2)
from qt_material import apply_stylesheet
qss = f"""
    QPushButton[cssClass="specialButton"] {{
        color: #fff;
        background: {PRIMARY};
    }}
    QPushButton[cssClass="specialButton"]:hover {{
        color: #fff;
        background: {DARKER};
    }}
    QPushButton[cssClass="specialButton"]:pressed {{
        color: #fff;
        background: {DARKEST};
    }}
    QPushButton[cssClass="normalButton"] {{
        color: #fff;
        background: {PRIMARY2};
    }}
    QPushButton[cssClass="normalButton"]:hover {{
        color: #fff;
        background: {DARKER2};
    }}
    QPushButton[cssClass="normalButton"]:pressed {{
        color: #fff;
        background: {DARKEST2};
    }}
"""


def setupTheme(app):
    apply_stylesheet(app, theme='dark_blue.xml')
    app.setStyleSheet(app.styleSheet() + qss)
        valid = False
    return valid
