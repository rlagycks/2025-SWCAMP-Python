import sys
import math
import random

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QApplication, QGridLayout, QLineEdit,
                             QPushButton, QWidget)

# --- 스타일시트 상수 정의 ---
BG_COLOR = "#1c1c1c"
DISPLAY_STYLE = f"""
    background-color: {BG_COLOR}; color: white; font-size: 60px;
    border: none; padding-right: 10px;
"""
ORANGE_BUTTON_STYLE = """
    QPushButton { background-color: #f1a33c; color: white; border-radius: 25px; }
    QPushButton:pressed { background-color: #f9c78b; }
"""
GRAY_BUTTON_STYLE = """
    QPushButton { background-color: #a5a5a5; color: black; border-radius: 25px; }
    QPushButton:pressed { background-color: #d9d9d9; }
"""
DARK_GRAY_BUTTON_STYLE = """
    QPushButton { background-color: #333333; color: white; border-radius: 25px; }
    QPushButton:pressed { background-color: #737373; }
"""
FUNC_BUTTON_STYLE = """
    QPushButton { background-color: #2e2e2e; color: white; border-radius: 25px; }
    QPushButton:pressed { background-color: #5e5e5e; }
"""


class Calculator:
    """
    기본 계산기의 상태와 연산 로직을 담당하는 기반 클래스.
    """
    def __init__(self):
        self.reset()

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError
        return a / b

    def reset(self):
        self.current_input = '0'
        self.first_operand = None
        self.operator = None
        self.waiting_for_second_operand = False
        self.calculation_finished = False

    def negative_positive(self):
        if self.current_input != '0':
            self.current_input = (self.current_input[1:] if self.current_input.startswith('-')
                                  else '-' + self.current_input)

    def percent(self):
        value = float(self.current_input) / 100
        self.current_input = self._format_result(value)

    def input_digit(self, digit):
        if self.calculation_finished:
            self.reset()
        if self.waiting_for_second_operand:
            self.current_input = digit
            self.waiting_for_second_operand = False
        else:
            self.current_input = (digit if self.current_input == '0'
                                  else self.current_input + digit)

    def input_decimal(self):
        if self.calculation_finished:
            self.reset()
        if '.' not in self.current_input:
            self.current_input += '.'

    def set_operator(self, op):
        if self.operator and not self.waiting_for_second_operand:
            self.equal()
        self.first_operand = float(self.current_input)
        self.operator = op
        self.waiting_for_second_operand = True
        self.calculation_finished = False

    def equal(self):
        if self.operator is None or self.waiting_for_second_operand:
            return
        second_operand = float(self.current_input)
        op_map = {
            '+': self.add, '-': self.subtract,
            '×': self.multiply, '÷': self.divide,
            'xʸ': self.power, 'ʸ√x': self.y_root_x
        }
        result = op_map[self.operator](self.first_operand, second_operand)
        self.current_input = self._format_result(result)
        self.first_operand = result
        self.operator = None
        self.calculation_finished = True

    def _format_result(self, value):
        if not isinstance(value, (int, float)):
            return "Error"
        if abs(value) > 1e15 or (abs(value) < 1e-9 and value != 0):
            return f"{value:.7e}"
        if value == int(value):
            return str(int(value))
        return str(round(value, 9))


class EngineeringCalculatorLogic(Calculator):
    """
    CalculatorLogic을 상속받아 공학용 기능을 추가한 클래스.
    """
    def __init__(self):
        super().__init__()
        self.is_deg_mode = True
        self.memory = 0

    def reset(self):
        super().reset()
        # 메모리는 AC에 초기화되지 않음

    def apply_unary_function(self, func):
        value = float(self.current_input)
        result = func(value)
        self.current_input = self._format_result(result)
        self.calculation_finished = True

    # --- 삼각함수 ---
    def _to_angle(self, val):
        return math.radians(val) if self.is_deg_mode else val

    def sin(self, val): return math.sin(self._to_angle(val))
    def cos(self, val): return math.cos(self._to_angle(val))
    def tan(self, val):
        if self.is_deg_mode and val % 180 == 90: raise ValueError
        return math.tan(self._to_angle(val))
    def asin(self, val):
        result_rad = math.asin(val)
        return math.degrees(result_rad) if self.is_deg_mode else result_rad
    def acos(self, val):
        result_rad = math.acos(val)
        return math.degrees(result_rad) if self.is_deg_mode else result_rad
    def atan(self, val):
        result_rad = math.atan(val)
        return math.degrees(result_rad) if self.is_deg_mode else result_rad

    # --- 쌍곡선 함수 ---
    def sinh(self, val): return math.sinh(val)
    def cosh(self, val): return math.cosh(val)
    def tanh(self, val): return math.tanh(val)
    def asinh(self, val): return math.asinh(val)
    def acosh(self, val): return math.acosh(val)
    def atanh(self, val): return math.atanh(val)

    # --- 거듭제곱 및 루트 ---
    def square(self, val): return val ** 2
    def cube(self, val): return val ** 3
    def power(self, base, exp): return base ** exp
    def inverse(self, val):
        if val == 0: raise ZeroDivisionError
        return 1 / val
    def sqrt(self, val): return math.sqrt(val)
    def cbrt(self, val): return val ** (1/3)
    def y_root_x(self, base, root):
        if base < 0 and root % 2 == 0: raise ValueError
        return base ** (1/root)
    def exp_e(self, val): return math.exp(val)
    def exp_10(self, val): return 10 ** val

    # --- 로그 및 기타 ---
    def ln(self, val): return math.log(val)
    def log10(self, val): return math.log10(val)
    def factorial(self, val):
        if val != int(val) or val < 0: raise ValueError
        return float(math.factorial(int(val)))
    def pi(self):
        self.current_input = self._format_result(math.pi)
        self.calculation_finished = True
    def e(self):
        self.current_input = self._format_result(math.e)
        self.calculation_finished = True
    def rand(self):
        self.current_input = self._format_result(random.random())
        self.calculation_finished = True

    # --- 메모리 기능 ---
    def memory_clear(self): self.memory = 0
    def memory_add(self): self.memory += float(self.current_input)
    def memory_subtract(self): self.memory -= float(self.current_input)
    def memory_recall(self):
        self.current_input = self._format_result(self.memory)
        self.calculation_finished = True


class ScientificCalculator(QWidget):
    """
    공학용 계산기 UI를 생성하고 EngineeringCalculator과 연결합니다.
    """
    def __init__(self):
        super().__init__()
        self.logic = EngineeringCalculatorLogic()
        self.is_2nd_active = False
        self.buttons = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('iPhone Scientific Calculator')
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        self.display = QLineEdit("0", self)
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFixedHeight(80)
        self.display.setStyleSheet(DISPLAY_STYLE)
        self.display.setFont(QFont("Helvetica", 40, QFont.Weight.Light))

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.display, 0, 0, 1, 10)

        button_layout = [
            ['(', ')', 'mc', 'm+', 'm-', 'mr', 'AC', '+/-', '%', '÷'],
            ['2nd', 'x²', 'x³', 'xʸ', 'eˣ', '10ˣ', '7', '8', '9', '×'],
            ['¹/ₓ', '√x', '∛x', 'ʸ√x', 'ln', 'log₁₀', '4', '5', '6', '-'],
            ['x!', 'sin', 'cos', 'tan', 'e', 'EE', '1', '2', '3', '+'],
            ['Rad', 'sinh', 'cosh', 'tanh', 'π', 'Rand', '0', '.', '=']
        ]

        for r, row_buttons in enumerate(button_layout):
            c = 0
            for text in row_buttons:
                if c >= 10: break
                button = self._create_button(text)
                self.buttons[text] = button
                if text == '0':
                    grid.addWidget(button, r + 1, c, 1, 2)
                    c += 2
                else:
                    grid.addWidget(button, r + 1, c)
                    c += 1
        self.setLayout(grid)

    def _create_button(self, text):
        button = QPushButton(text)
        button.setFont(QFont("Helvetica", 16))

        if text in ('÷', '×', '-', '+', '=', 'xʸ', 'ʸ√x'):
            button.setStyleSheet(ORANGE_BUTTON_STYLE)
        elif text in ('AC', '+/-', '%', 'mc', 'm+', 'm-', 'mr'):
            button.setStyleSheet(GRAY_BUTTON_STYLE)
        elif text.isdigit() or text == '.':
            button.setStyleSheet(DARK_GRAY_BUTTON_STYLE)
        else:
            button.setStyleSheet(FUNC_BUTTON_STYLE)

        button.clicked.connect(self.button_clicked)
        button.setFixedSize(150 if text == '0' else 70, 50)
        return button

    def button_clicked(self):
        button = self.sender()
        key = button.text()

        try:
            if self.logic.current_input == "Error" and key != 'AC': return

            # 기능별로 로직 메소드 호출
            if key.isdigit(): self.logic.input_digit(key)
            elif key == '.': self.logic.input_decimal()
            elif key in ('÷', '×', '-', '+', 'xʸ', 'ʸ√x'): self.logic.set_operator(key)
            elif key == '=': self.logic.equal()
            elif key == 'AC': self.logic.reset()
            elif key == '+/-': self.logic.negative_positive()
            elif key == '%': self.logic.percent()
            # --- 단항 연산자 매핑 ---
            elif key == 'sin': self.logic.apply_unary_function(self.logic.sin)
            elif key == 'cos': self.logic.apply_unary_function(self.logic.cos)
            elif key == 'tan': self.logic.apply_unary_function(self.logic.tan)
            elif key == 'sin⁻¹': self.logic.apply_unary_function(self.logic.asin)
            elif key == 'cos⁻¹': self.logic.apply_unary_function(self.logic.acos)
            elif key == 'tan⁻¹': self.logic.apply_unary_function(self.logic.atan)
            elif key == 'sinh': self.logic.apply_unary_function(self.logic.sinh)
            elif key == 'cosh': self.logic.apply_unary_function(self.logic.cosh)
            elif key == 'tanh': self.logic.apply_unary_function(self.logic.tanh)
            elif key == 'sinh⁻¹': self.logic.apply_unary_function(self.logic.asinh)
            elif key == 'cosh⁻¹': self.logic.apply_unary_function(self.logic.acosh)
            elif key == 'tanh⁻¹': self.logic.apply_unary_function(self.logic.atanh)
            elif key == 'x²': self.logic.apply_unary_function(self.logic.square)
            elif key == 'x³': self.logic.apply_unary_function(self.logic.cube)
            elif key == '¹/ₓ': self.logic.apply_unary_function(self.logic.inverse)
            elif key == '√x': self.logic.apply_unary_function(self.logic.sqrt)
            elif key == '∛x': self.logic.apply_unary_function(self.logic.cbrt)
            elif key == 'eˣ': self.logic.apply_unary_function(self.logic.exp_e)
            elif key == '10ˣ': self.logic.apply_unary_function(self.logic.exp_10)
            elif key == 'ln': self.logic.apply_unary_function(self.logic.ln)
            elif key == 'log₁₀': self.logic.apply_unary_function(self.logic.log10)
            elif key == 'x!': self.logic.apply_unary_function(self.logic.factorial)
            # --- 상수 ---
            elif key == 'π': self.logic.pi()
            elif key == 'e': self.logic.e()
            elif key == 'Rand': self.logic.rand()
            # --- 메모리 ---
            elif key == 'mc': self.logic.memory_clear()
            elif key == 'm+': self.logic.memory_add()
            elif key == 'm-': self.logic.memory_subtract()
            elif key == 'mr': self.logic.memory_recall()
            # --- 토글 버튼 ---
            elif key == '2nd': self.toggle_2nd()
            elif key in ('Rad', 'Deg'):
                self.logic.is_deg_mode = not self.logic.is_deg_mode
                button.setText("Deg" if self.logic.is_deg_mode else "Rad")

        except (ValueError, TypeError, ZeroDivisionError, OverflowError):
            self.logic.current_input = "Error"
        
        self.update_display()

    def toggle_2nd(self):
        self.is_2nd_active = not self.is_2nd_active
        
        # 2nd 버튼 스타일 변경
        style = (GRAY_BUTTON_STYLE if self.is_2nd_active
                 else FUNC_BUTTON_STYLE)
        self.buttons['2nd'].setStyleSheet(style)

        # 토글될 버튼들의 텍스트 변경
        toggle_map = {
            'sin': 'sin⁻¹', 'cos': 'cos⁻¹', 'tan': 'tan⁻¹',
            'sinh': 'sinh⁻¹', 'cosh': 'cosh⁻¹', 'tanh': 'tanh⁻¹',
            'ln': 'log₂', 'log₁₀': 'logᵧ' # 예시, 실제 기능은 추가 구현 필요
        }
        for old, new in toggle_map.items():
            if self.is_2nd_active:
                self.buttons[old].setText(new)
                self.buttons[new] = self.buttons.pop(old)
            else:
                self.buttons[new].setText(old)
                self.buttons[old] = self.buttons.pop(new)

    def update_display(self):
        if self.logic.operator and self.logic.first_operand is not None:
            first_op_str = self.logic._format_result(self.logic.first_operand)
            if self.logic.waiting_for_second_operand:
                display_text = f"{first_op_str} {self.logic.operator}"
            else:
                display_text = (f"{first_op_str} {self.logic.operator} "
                                f"{self.logic.current_input}")
        else:
            display_text = self.logic.current_input
        self.display.setText(display_text)


def main():
    """메인 실행 함수"""
    app = QApplication(sys.argv)
    calc = ScientificCalculator()
    calc.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
