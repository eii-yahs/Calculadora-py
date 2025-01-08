import math
from typing import TYPE_CHECKING
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QLineEdit, QLabel, QWidget, QGridLayout, QPushButton
from variables import BIG_FONT, MINIMUM_WIDTH, MARGIN, SMALL_FONT, MEDIUM_FONT, conver_num, is_empty, is_num_or_dot, is_valid_number
if TYPE_CHECKING:
    from main import MainWindow

class Info(QLabel):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.configStyle()

    def configStyle(self):
        self.setStyleSheet(f'font-size: {SMALL_FONT}px;')
        self.setAlignment(Qt.AlignmentFlag.AlignRight)

class Display(QLineEdit):
    eqPressed = Signal()
    delPressed = Signal()
    clearPressed = Signal()
    inputPressed = Signal(str)
    operatorPressed = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_sty()

    def config_sty(self):
        margins = [MARGIN for _ in range(4)]
        self.setStyleSheet(f'font-size: {BIG_FONT}px;')
        self.setMinimumHeight(BIG_FONT * 2)
        self.setMinimumWidth(MINIMUM_WIDTH)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setTextMargins(*margins)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        text = event.text().strip()
        key = event.key()
        KEYS = Qt.Key

        is_enter = key in [KEYS.Key_Enter, KEYS.Key_Return, KEYS.Key_Equal]
        is_delete = key in [KEYS.Key_Backspace, KEYS.Key_Delete, KEYS.Key_D]
        is_esc = key in [KEYS.Key_Escape, KEYS.Key_C]
        is_operator = key in [
            KEYS.Key_Plus, KEYS.Key_Minus, KEYS.Key_Slash, KEYS.Key_Asterisk,
            KEYS.Key_P,
        ]

        if is_enter:
            self.eqPressed.emit()
            return event.ignore()

        if is_delete:
            self.delPressed.emit()
            return event.ignore()

        if is_esc:
            self.clearPressed.emit()
            return event.ignore()

        if is_operator:
            if text.lower() == 'p':
                text = '^'
            self.operatorPressed.emit(text)
            return event.ignore()

        if is_empty(text):
            return event.ignore()

        if is_num_or_dot(text):
            self.inputPressed.emit(text)
            return event.ignore()

class Button(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configStyle()

    def configStyle(self):
        font = self.font()
        font.setPixelSize(MEDIUM_FONT)
        self.setFont(font)
        self.setMinimumSize(75, 75)

class ButtonsGrid(QGridLayout):
    def __init__(
            self, display: 'Display', info: 'Info', window: 'MainWindow',
            *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self._gridMask = [
            ['C', '^', '÷', '⌫'],
            ['7', '8', '9', 'x'],
            ['4', '5', '6', '+'],
            ['3', '2', '1', "-"],
            ['%', '0', '.', '⏎'],
        ]
        self.display = display
        self.info = info
        self.window = window
        self._equation = ''
        self._equationInitialValue = ''
        self._left = None
        self._right = None
        self._op = None

        self.equation = self._equationInitialValue
        self._makeGrid()

    @property
    def equation(self):
        return self._equation

    @equation.setter
    def equation(self, value):
        self._equation = value
        self.info.setText(value)

    def _makeGrid(self):
        self.display.eqPressed.connect(self._eq)
        self.display.delPressed.connect(self._backspace)
        self.display.clearPressed.connect(self._clear)
        self.display.inputPressed.connect(self._insertToDisplay)
        self.display.operatorPressed.connect(self._configLeftOp)

        for rowNumber, rowData in enumerate(self._gridMask):
            for colNumber, buttonText in enumerate(rowData):
                button = Button(buttonText)

                if not is_num_or_dot(buttonText) and not is_empty(buttonText):
                    button.setProperty('cssClass', 'specialButton')
                    self._configSpecialButton(button)
                else:
                    button.setProperty('cssClass', 'normalButton')

                self.addWidget(button, rowNumber, colNumber)
                slot = self._makeSlot(self._insertToDisplay, buttonText)
                self._connectButtonClicked(button, slot)

    def _connectButtonClicked(self, button, slot):
        button.clicked.connect(slot)  # type: ignore

    def _configSpecialButton(self, button):
        text = button.text()

        if text == 'C':
            self._connectButtonClicked(button, self._clear)

        if text == '⌫':
            self._connectButtonClicked(button, self.display.backspace)

        if text == 'N':
            self._connectButtonClicked(button, self._invertNumber)

        if text in '+-÷x^%':
            self._connectButtonClicked(
                button,
                self._makeSlot(self._configLeftOp, text)
            )

        if text == '⏎':
            self._connectButtonClicked(button, self._eq)

    @Slot()
    def _makeSlot(self, func, *args, **kwargs):
        @ Slot(bool)
        def realSlot(_):
            func(*args, **kwargs)
        return realSlot

    @Slot()
    def _invertNumber(self):
        displayText = self.display.text()

        if not is_valid_number(displayText):
            return

        number = conver_num(displayText) * -1
        self.display.setText(str(number))

    @Slot()
    def _insertToDisplay(self, text):
        newDisplayValue = self.display.text() + text

        if not is_valid_number(newDisplayValue):
            return

        self.display.insert(text)
        self.display.setFocus()

    @Slot()
    def _clear(self):
        self._left = None
        self._right = None
        self._op = None
        self.equation = self._equationInitialValue
        self.display.clear()
        self.display.setFocus()

    @Slot()
    def _configLeftOp(self, text):
        displayText = self.display.text()  # Deverá ser meu número _left
        self.display.clear()  # Limpa o display
        self.display.setFocus()

        # Se a pessoa clicou no operador sem
        # configurar qualquer número
        if not is_valid_number(displayText) and self._left is None:
            self._showError('ERROR')
            return

        # Se houver algo no número da esquerda,
        # não fazemos nada. Aguardaremos o número da direita.
        if self._left is None:
            self._left = conver_num(displayText)

        self._op = text
        self.equation = f'{self._left} {self._op}'

    @Slot()
    def _eq(self):
        displayText = self.display.text()
        historico = ''

        if not is_valid_number(displayText) or self._left is None:
            self._showError('ERROR')
            return

        self._right = conver_num(displayText)
        self.equation = f'{self._left} {self._op} {self._right}'
        result = 'error'

        try:
            if '^' in self.equation and isinstance(self._left, (float, int)):
                result = math.pow(self._left, self._right)
                result = conver_num(str(result))

            elif '÷' in self.equation and isinstance(self._left, (float, int)):
                result = self._left / self._right
                result = conver_num(str(result))

            elif 'x' in self.equation and isinstance(self._left, (float, int)):
                result = self._left * self._right
                result = conver_num(str(result))

            elif '%' in self.equation and isinstance(self._left, (float, int)):
                result = self._left/100 * self._right
                result = conver_num(str(result))

            else:
                result = eval(self.equation)
        except ZeroDivisionError:
            self._showError('ERROR')
        except OverflowError:
            self._showError('ERROR')

        self.display.clear()
        self.info.setText(f'{self.equation} = {result}')
        with open('history.txt', 'a') as file:
            file.write(f"{self.equation} = {result}\n")
        self._left = result
        self._right = None
        self.display.setFocus()

        if result == 'error':
            self._left = None

    @Slot()
    def _backspace(self):
        self.display.backspace()
        self.display.setFocus()

    def _makeDialog(self, text):
        msgBox = self.window.makeMsgBox()
        msgBox.setText(text)
        return msgBox

    def _showError(self, text):
        msgBox = self._makeDialog(text)
        msgBox.setIcon(msgBox.Icon.Critical)
        msgBox.exec()
        self.display.setFocus()

    def _showInfo(self, text):
        msgBox = self._makeDialog(text)
        msgBox.setIcon(msgBox.Icon.Information)
        msgBox.exec()
        self.display.setFocus()
