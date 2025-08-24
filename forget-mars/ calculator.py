#!/usr/bin/env python3
# calculator.py

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class CalculatorLogic:
    """
    계산기의 모든 상태와 연산 로직을 담당하는 클래스.
    UI와 독립적으로 동작합니다.
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
            return "Error"
        return a / b

    def reset(self):
        """모든 상태를 초기화합니다."""
        self.current_input = '0'
        self.first_operand = None
        self.operator = None
        self.waiting_for_second_operand = False
        self.calculation_finished = False # 계산 완료 상태 플래그

    def input_digit(self, digit):
        """숫자 입력을 처리합니다."""
        if self.calculation_finished:
            self.reset() # 계산 후 새 숫자 입력 시 초기화

        if self.waiting_for_second_operand:
            self.current_input = digit
            self.waiting_for_second_operand = False
        else:
            if self.current_input == '0':
                self.current_input = digit
            else:
                self.current_input += digit

    def input_decimal(self):
        """소수점 입력을 처리합니다."""
        if self.calculation_finished:
            self.reset()
        if '.' not in self.current_input:
            self.current_input += '.'

    def negative_positive(self):
        """음수/양수 전환을 처리합니다."""
        if self.current_input != '0':
            if self.current_input.startswith('-'):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
        self.calculation_finished = False

    def percent(self):
        """퍼센트 계산을 처리합니다."""
        try:
            value = float(self.current_input) / 100
            self.current_input = self._format_result(value)
        except ValueError:
            self.current_input = "Error"
        self.calculation_finished = False

    def set_operator(self, op):
        """연산자 입력을 처리합니다."""
        if self.operator and not self.waiting_for_second_operand:
            self.equal()
        
        try:
            self.first_operand = float(self.current_input)
            self.operator = op
            self.waiting_for_second_operand = True
            self.calculation_finished = False
        except ValueError:
            self.current_input = "Error"
            
    def equal(self):
        """'=' 버튼 또는 연속된 연산자 입력 시 계산을 수행합니다."""
        if self.operator is None or self.waiting_for_second_operand:
            return

        try:
            second_operand = float(self.current_input)
            result = 0
            
            op_map = {
                '+': self.add,
                '-': self.subtract,
                '×': self.multiply,
                '÷': self.divide
            }
            
            result = op_map[self.operator](self.first_operand, second_operand)

            if result == "Error":
                self.current_input = "Error"
            else:
                self.current_input = self._format_result(result)

            self.first_operand = result if result != "Error" else None
            self.operator = None
            self.calculation_finished = True

        except (ValueError, TypeError):
            self.current_input = "Error"
            self.operator = None

    def _format_result(self, value):
        """계산 결과를 디스플레이 형식에 맞게 변환합니다."""
        if abs(value) > 1e15 or (abs(value) < 1e-6 and value != 0):
             return f"{value:.6e}"
        
        if value == int(value):
            return str(int(value))
        else:
            return str(round(value, 6))


class Calculator(QWidget):
    """
    계산기 UI를 생성하고 CalculatorLogic과 연결하여 상호작용을 처리합니다.
    """
    def __init__(self):
        super().__init__()
        self.logic = CalculatorLogic()
        self.init_ui()

    def init_ui(self):
        """UI의 기본 설정과 레이아웃을 초기화합니다."""
        self.setWindowTitle('iPhone Calculator')
        self.setGeometry(300, 300, 400, 600)
        self.setStyleSheet("background-color: #1c1c1c;")

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFixedHeight(100)
        self.display.setStyleSheet("""
            background-color: #1c1c1c; color: white; font-size: 70px;
            border: none; padding-right: 10px;
        """)
        self.display.setFont(QFont("Helvetica", 45, QFont.Weight.Light))
        self.display.setText("0")

        grid = QGridLayout()
        grid.setSpacing(10)

        buttons = [
            ('AC', 0, 0), ('+/-', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 1, 2), ('.', 4, 2), ('=', 4, 3)
        ]

        grid.addWidget(self.display, 0, 0, 1, 4)

        for btn_text, row, col, *span in buttons:
            button = QPushButton(btn_text)
            if btn_text == '0':
                button.setFixedSize(170, 80)
            else:
                button.setFixedSize(80, 80)
            button.setFont(QFont("Helvetica", 24))
            
            if btn_text in ('AC', '+/-', '%'):
                button.setStyleSheet("QPushButton { background-color: #a5a5a5; color: black; border-radius: 40px; } QPushButton:pressed { background-color: #d9d9d9; }")
            elif btn_text in ('÷', '×', '-', '+', '='):
                button.setStyleSheet("QPushButton { background-color: #f1a33c; color: white; border-radius: 40px; } QPushButton:pressed { background-color: #f9c78b; }")
            else:
                button.setStyleSheet("QPushButton { background-color: #333333; color: white; border-radius: 40px; } QPushButton:pressed { background-color: #737373; }")
            
            button.clicked.connect(self.button_clicked)
            if span:
                grid.addWidget(button, row + 1, col, span[0], span[1])
            else:
                grid.addWidget(button, row + 1, col)
        self.setLayout(grid)

    def button_clicked(self):
        """UI 버튼 클릭을 감지하고 로직 클래스의 해당 메소드를 호출합니다."""
        button = self.sender()
        key = button.text()

        if self.logic.current_input == "Error" and key != 'AC':
            return

        if key.isdigit():
            self.logic.input_digit(key)
        elif key == '.':
            self.logic.input_decimal()
        elif key in ('÷', '×', '-', '+'):
            self.logic.set_operator(key)
        elif key == '=':
            self.logic.equal()
        elif key == 'AC':
            self.logic.reset()
        elif key == '+/-':
            self.logic.negative_positive()
        elif key == '%':
            self.logic.percent()
        
        self.update_display()

    def update_display(self):
        """로직의 현재 상태를 기반으로 디스플레이를 업데이트합니다."""
        # 연산자가 활성화되어 있고 두 번째 피연산자를 기다리는 상태일 때
        if self.logic.operator and self.logic.waiting_for_second_operand:
            display_text = f"{self.logic._format_result(self.logic.first_operand)} {self.logic.operator}"
        # 연산자가 활성화되어 있고 두 번째 피연산자를 입력 중일 때
        elif self.logic.operator and self.logic.first_operand is not None:
            display_text = f"{self.logic._format_result(self.logic.first_operand)} {self.logic.operator} {self.logic.current_input}"
        # 그 외의 모든 경우 (첫 숫자 입력, 계산 완료 등)
        else:
            display_text = self.logic.current_input
        
        self.display.setText(display_text)


def main():
    """메인 실행 함수"""
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
