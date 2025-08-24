#!/usr/bin/env python3
# engineering_calculator.py

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ScientificCalculator(QWidget):
    """
    아이폰 스타일의 공학용 계산기 UI를 만드는 클래스.
    """
    def __init__(self):
        super().__init__()
        self.init_state()
        self.init_ui()

    def init_state(self):
        """계산기 상태 변수를 초기화합니다."""
        self.current_input = '0'
        self.first_operand = None
        self.operator = None
        self.waiting_for_second_operand = False

    def init_ui(self):
        """UI의 기본 설정과 레이아웃을 초기화합니다."""
        self.setWindowTitle('iPhone Scientific Calculator')
        self.setGeometry(100, 100, 800, 500) # 가로로 긴 창
        self.setStyleSheet("background-color: #1c1c1c;")

        # --- 위젯 생성 ---
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFixedHeight(80)
        self.display.setStyleSheet("""
            background-color: #1c1c1c;
            color: white;
            font-size: 60px;
            border: none;
            padding-right: 10px;
        """)
        self.display.setFont(QFont("Helvetica", 40, QFont.Weight.Light))
        self.display.setText("0")

        # --- 그리드 레이아웃 설정 ---
        grid = QGridLayout()
        grid.setSpacing(10)

        buttons = [
            ['(', ')', 'mc', 'm+', 'm-', 'mr', 'AC', '+/-', '%', '÷'],
            ['2nd', 'x²', 'x³', 'xʸ', 'eˣ', '10ˣ', '7', '8', '9', '×'],
            ['¹/ₓ', '√x', '∛x', 'ʸ√x', 'ln', 'log₁₀', '4', '5', '6', '-'],
            ['x!', 'sin', 'cos', 'tan', 'e', 'EE', '1', '2', '3', '+'],
            ['Rad', 'sinh', 'cosh', 'tanh', 'π', 'Rand', '0', '.', '=']
        ]

        grid.addWidget(self.display, 0, 0, 1, 10)

        for row_idx, row_buttons in enumerate(buttons):
            col_idx = 0
            for btn_text in row_buttons:
                if col_idx >= 10: break
                
                button = QPushButton(btn_text)
                button.setFont(QFont("Helvetica", 16))

                if btn_text in ('÷', '×', '-', '+', '='):
                    button.setStyleSheet("QPushButton { background-color: #f1a33c; color: white; border-radius: 25px; } QPushButton:pressed { background-color: #f9c78b; }")
                elif btn_text in ('AC', '+/-', '%', 'mc', 'm+', 'm-', 'mr'):
                    button.setStyleSheet("QPushButton { background-color: #a5a5a5; color: black; border-radius: 25px; } QPushButton:pressed { background-color: #d9d9d9; }")
                elif btn_text.isdigit() or btn_text == '.':
                    button.setStyleSheet("QPushButton { background-color: #333333; color: white; border-radius: 25px; } QPushButton:pressed { background-color: #737373; }")
                else:
                    button.setStyleSheet("QPushButton { background-color: #2e2e2e; color: white; border-radius: 25px; } QPushButton:pressed { background-color: #5e5e5e; }")
                
                button.clicked.connect(self.button_clicked)
                
                if btn_text == '0':
                    button.setFixedSize(150, 50)
                    grid.addWidget(button, row_idx + 1, col_idx, 1, 2)
                    col_idx += 2
                else:
                    button.setFixedSize(70, 50)
                    grid.addWidget(button, row_idx + 1, col_idx)
                    col_idx += 1
        self.setLayout(grid)

    def button_clicked(self):
        """버튼 클릭을 감지하고 상태를 변경한 후 디스플레이를 업데이트합니다."""
        button = self.sender()
        key = button.text()
        operators = ['÷', '×', '-', '+']

        if key == 'AC':
            self.init_state()
        elif key.isdigit():
            if self.waiting_for_second_operand:
                self.current_input = key
                self.waiting_for_second_operand = False
            else:
                self.current_input = key if self.current_input == '0' else self.current_input + key
        elif key == '.':
            if '.' not in self.current_input:
                self.current_input += '.'
        elif key in operators:
            if self.operator and not self.waiting_for_second_operand:
                # 연속 연산 (e.g., 3 + 4 -) -> 7 -
                # (계산 기능은 없으므로 상태만 초기화)
                self.first_operand = self.current_input
            else:
                self.first_operand = self.current_input
            
            self.operator = key
            self.waiting_for_second_operand = True
        elif key == '=':
            # (계산 기능은 없으므로 상태만 초기화)
            self.init_state()
        else: # 공학용 버튼들 (단순 추가)
            self.current_input = key + '(' + self.current_input + ')'

        self.update_display()

    def update_display(self):
        """계산기 상태에 따라 디스플레이 텍스트를 업데이트합니다."""
        if self.operator and self.first_operand is not None:
            if self.waiting_for_second_operand:
                # 5 + 입력 후
                display_text = f"{self.first_operand} {self.operator}"
            else:
                # 5 + 3 입력 중
                display_text = f"{self.first_operand} {self.operator} {self.current_input}"
        else:
            # 첫 숫자 입력 중 또는 계산 완료 후
            display_text = self.current_input
        
        self.display.setText(display_text)


def main():
    """메인 실행 함수"""
    app = QApplication(sys.argv)
    calc = ScientificCalculator()
    calc.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
