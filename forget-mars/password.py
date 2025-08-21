#!/usr/bin/env python3
# caesar_cipher_decoder.py

import string
import os

# --- 상수 정의 ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PASSWORD_FILE = os.path.join(SCRIPT_DIR, 'password.txt')
RESULT_FILE = os.path.join(SCRIPT_DIR, 'result.txt')

def caesar_cipher_decode(target_text: str):
    """
    주어진 텍스트에 대해 카이사르 암호 해독을 수행하고,
    가능한 모든 경우의 수를 출력한 뒤 사용자의 선택을 받아 결과를 저장합니다.
    """
    # 알파벳 소문자/대문자 준비
    lower_alphabet = string.ascii_lowercase
    upper_alphabet = string.ascii_uppercase

    decoded_results = []

    print("--- 카이사르 암호 해독 시작 ---\n")
    # 자리수는 알파벳 수만큼 반복 (0~25, 총 26번)
    for shift in range(len(lower_alphabet)):
        # 원본 알파벳과, shift만큼 밀린 새로운 알파벳 순서를 만듭니다.
        # 예: shift가 1일 때, 'abc...' -> 'bcd...za'
        shifted_lower = lower_alphabet[shift:] + lower_alphabet[:shift]
        shifted_upper = upper_alphabet[shift:] + upper_alphabet[:shift]

        # 변환 규칙(테이블) 생성
        # 소문자는 소문자 규칙으로, 대문자는 대문자 규칙으로 변환합니다.
        translation_table = str.maketrans(
            lower_alphabet + upper_alphabet,
            shifted_lower + shifted_upper
        )

        # 변환 규칙을 적용하여 텍스트 해독
        decoded_text = target_text.translate(translation_table)
        decoded_results.append(decoded_text)

        # 자리수(shift)에 따라서 해독된 결과를 출력
        # 사용자가 보기 편하도록 1부터 시작하는 번호를 붙입니다.
        print(f"[{shift + 1:2d}] {decoded_text}")

    print("\n--- 해독 완료 ---")

    while True:
        try:
            # 눈으로 식별 가능한 번호를 사용자로부터 입력받음
            user_choice = input("해독된 암호의 번호를 입력하세요 (1-26): ")
            choice_index = int(user_choice) - 1

            # 사용자가 올바른 범위의 번호를 입력했는지 확인
            if 0 <= choice_index < len(decoded_results):
                final_password = decoded_results[choice_index]
                print(f"\n선택한 암호: {final_password}")

                # 최종 암호를 result.txt 파일로 저장
                try:
                    with open(RESULT_FILE, 'w', encoding='utf-8') as f:
                        f.write(final_password)
                    print(f"암호를 '{RESULT_FILE}' 파일에 성공적으로 저장했습니다.")
                except IOError as e:
                    print(f"오류: 결과를 파일에 저장하는 데 실패했습니다 - {e}")
                
                break # 루프 종료
            else:
                print("잘못된 번호입니다. 1부터 26 사이의 숫자를 입력해주세요.")
        except ValueError:
            print("숫자만 입력해주세요.")
        except Exception as e:
            print(f"예상치 못한 오류가 발생했습니다: {e}")

def main():
    """메인 실행 함수"""
    try:
        # password.txt 파일을 읽어옴
        with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
            encrypted_password = f.read().strip()
        
        if not encrypted_password:
            print(f"오류: '{PASSWORD_FILE}' 파일이 비어있습니다.")
            return

        # 카이사르 암호 해독 함수 호출
        caesar_cipher_decode(target_text=encrypted_password)

    except FileNotFoundError:
        print(f"오류: '{PASSWORD_FILE}' 파일을 찾을 수 없습니다.")
        print("이 스크립트와 동일한 폴더에 password.txt 파일을 만들어주세요.")
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")


if __name__ == '__main__':
    main()
