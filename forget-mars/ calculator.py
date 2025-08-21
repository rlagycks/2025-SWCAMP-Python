#!/usr/bin/env python3
# calculator.py

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class Calculator(QWidget):
    """
    아이폰 스타일의 계산기 UI를 만드는 클래스.
    실제 계산 기능은 제외하고 UI와 버튼 입력 처리만 구현합니다.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """UI의 기본 설정과 레이아웃을 초기화합니다."""
        self.setWindowTitle('iPhone Calculator')
        self.setGeometry(300, 300, 400, 600) # 윈도우 위치와 크기 설정
        self.setStyleSheet("background-color: #1c1c1c;") # 전체 배경색을 어둡게 설정

        # --- 위젯 생성 ---
        # 숫자와 결과가 표시될 디스플레이 라인
        self.display = QLineEdit()
        self.display.setReadOnly(True) # 읽기 전용으로 설정
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight) # 텍스트 오른쪽 정렬
        self.display.setFixedHeight(100)
        # 디스플레이 스타일 설정
        self.display.setStyleSheet("""
            background-color: #1c1c1c;
            color: white;
            font-size: 70px;
            border: none;
            padding-right: 10px;
        """)
        self.display.setFont(QFont("Helvetica", 45, QFont.Weight.Light))
        self.display.setText("0")

        # --- 그리드 레이아웃 설정 ---
        grid = QGridLayout()
        grid.setSpacing(10) # 버튼 사이의 간격

        # 아이폰 계산기 버튼 레이아웃 정의
        # (텍스트, 행, 열, 행병합, 열병합)
        buttons = [
            ('AC', 0, 0), ('+/-', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 1, 2), ('.', 4, 2), ('=', 4, 3) # 0 버튼은 2칸 차지
        ]

        # --- 위젯을 레이아웃에 추가 ---
        grid.addWidget(self.display, 0, 0, 1, 4) # 디스플레이는 첫 행에 4칸을 차지

        for btn_text, row, col, *span in buttons:
            button = QPushButton(btn_text)
            
            # '0' 버튼의 너비를 다른 버튼의 2배 + 간격으로 설정
            if btn_text == '0':
                button.setFixedSize(170, 80)
            else:
                button.setFixedSize(80, 80) # 나머지 버튼 크기 고정

            button.setFont(QFont("Helvetica", 24))
            
            # 버튼 종류에 따라 스타일 적용
            if btn_text in ('AC', '+/-', '%'):
                button.setStyleSheet("""
                    QPushButton { background-color: #a5a5a5; color: black; border-radius: 40px; }
                    QPushButton:pressed { background-color: #d9d9d9; }
                """)
            elif btn_text in ('÷', '×', '-', '+', '='):
                button.setStyleSheet("""
                    QPushButton { background-color: #f1a33c; color: white; border-radius: 40px; }
                    QPushButton:pressed { background-color: #f9c78b; }
                """)
            else: # 숫자 버튼
                button.setStyleSheet("""
                    QPushButton { background-color: #333333; color: white; border-radius: 40px; }
                    QPushButton:pressed { background-color: #737373; }
                """)

            # 버튼 클릭 시 이벤트 처리 함수 연결
            button.clicked.connect(self.button_clicked)

            if span: # 버튼이 여러 칸을 차지하는 경우 (e.g., '0' 버튼)
                grid.addWidget(button, row + 1, col, span[0], span[1])
            else:
                grid.addWidget(button, row + 1, col)

        self.setLayout(grid)

    def button_clicked(self):
        """버튼이 클릭되었을 때 호출되는 이벤트 핸들러입니다."""
        button = self.sender()
        key = button.text()
        current_text = self.display.text()
        operators = ['÷', '×', '-', '+']

        # 1. AC (초기화) 처리
        if key == 'AC':
            self.display.setText('0')
            return

        # 2. +/- 부호 변경 처리
        if key == '+/-':
            # 마지막 연산자의 위치를 찾음
            last_op_index = -1
            for op in operators:
                last_op_index = max(last_op_index, current_text.rfind(op))

            # 연산자 이후의 숫자 부분을 가져옴
            number_part = current_text[last_op_index + 1:]
            
            if number_part and float(number_part) != 0: # 숫자 부분이 있고 0이 아닐 때만
                if number_part.startswith('-'):
                    # 음수면 양수로
                    new_number_part = number_part[1:]
                else:
                    # 양수면 음수로
                    new_number_part = '-' + number_part
                
                # 전체 텍스트를 재구성
                new_text = current_text[:last_op_index + 1] + new_number_part
                self.display.setText(new_text)
            return

        # 3. = (결과) 처리
        if key == '=':
            # 마지막 글자가 연산자이거나 소수점이면 계산하지 않음
            if current_text and (current_text[-1] in operators or current_text[-1] == '.'):
                return
            # (실제 계산 로직은 여기에 추가)
            # 지금은 아무것도 하지 않음
            return

        # 4. 연산자 입력 처리
        if key in operators:
            # 마지막 글자가 연산자라면 새 연산자로 교체
            if current_text and current_text[-1] in operators:
                self.display.setText(current_text[:-1] + key)
            # 마지막 글자가 소수점이라면 입력 무시
            elif current_text and current_text[-1] == '.':
                return
            else:
                self.display.setText(current_text + key)
            return

        # 5. 소수점 입력 처리
        if key == '.':
            # 현재 입력 중인 숫자에 이미 소수점이 있는지 확인
            last_op_index = -1
            for op in operators:
                last_op_index = max(last_op_index, current_text.rfind(op))
            
            number_part = current_text[last_op_index + 1:]
            
            if '.' not in number_part:
                self.display.setText(current_text + key)
            return

        # 6. 숫자 입력 처리
        if current_text == '0' and key != '.':
            self.display.setText(key)
        else:
            self.display.setText(current_text + key)


def main():
    """메인 실행 함수"""
    # PyQt6 라이브러리가 설치되어 있는지 확인합니다.
    # 설치 명령어: pip install PyQt6
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
