'''
Python에서 기본 제공되는 명령어만 사용해야 하며 별도의 라이브러리나 패키지를 사용해서는 안된다.
Python의 coding style guide를 확인하고 가이드를 준수해서 코딩한다.
(PEP 8 – 파이썬 코드 스타일 가이드 | peps.python.org)
    문자열을 표현 할 때에는 ‘ ’을 기본으로 사용한다. 다만 문자열 내에서 ‘을 사용할 경우와 같이 부득이한 경우에는 “ “를 사용한다.
    foo = (0,) 와 같이 대입문의 = 앞 뒤로는 공백을 준다.
    들여 쓰기는 공백을 기본으로 사용합니다.


로그 분석을 위해 Python으로 소프트웨어를 개발해야 한다. 이를 위해서 먼저 Python을 설치해야 한다.
빠른 개발을 위해 Python 개발 도구들을 알아보고 비교해서 하나의 도구를 선정해서 설치한다.
설치가 잘 되었는지 확인 하기 위해서 ‘Hello Mars’를 출력해 본다.
본격적으로 로그를 분석하기 위해서 mission_computer_main.log 파일을 열고 전체 내용을 화면에 출력해 본다. 이때 코드는 main.py 파일로 저장한다.
(로그 데이터는 별도 제공)
파일을 처리 할 때에 발생할 수 있는 예외를 처리한다.
mission_computer_main.log의 내용을 통해서 사고의 원인을 분석하고 정리해서 보고서(log_analysis.md)를 Markdown 형태로 를 작성해 놓는다.

출력 결과를 시간의 역순으로 정렬해서 출력한다.
출력 결과 중 문제가 되는 부분만 따로 파일로 저장한다.
'''


import os
import json

# 현재 디렉터리 설정
os.chdir(os.path.dirname(__file__))

# 로그 파일 읽기
try:
    with open('mission_computer_main.log', 'r', encoding='utf-8') as f:
        mars_logs = [line.strip() for line in f.readlines()]
except FileNotFoundError:
    print('로그 파일이 존재하지 않습니다.')
    exit(1)
except PermissionError:
    print('로그 파일에 접근 권한이 없습니다.')
    exit(1)

# 로그 파싱 (timestamp, message만 추출)
log_mars = []
for line in mars_logs:
    parts = line.split(',', 2)
    if len(parts) == 3:
        timestamp, event, message = parts
        log_mars.append((timestamp.strip(), message.strip()))

# 시간 역순 출력
for timestamp, message in reversed(log_mars):
    print(f'{timestamp}, {message}')

# 로그를 딕셔너리로 변환 후 JSON 저장
log_dict = {timestamp: message for timestamp, message in log_mars}
with open('mission_computer_main.json', 'w', encoding='utf-8') as f:
    json.dump(log_dict, f, ensure_ascii=False, indent=4)

# 로그에서 내용 검색
for timestamp, message in log_dict.items():
    if 'Oxygen' in message.lower():
        print(f'{timestamp}: {message}')