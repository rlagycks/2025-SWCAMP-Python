#!/usr/bin/env python3
# cctv.py

"""
CCTV.zip 파일의 압축을 해제하고,
폴더 내의 이미지를 키보드 방향키로 탐색할 수 있는 이미지 뷰어.

실행 전 'Pillow' 라이브러리 설치가 필요합니다.
(pip install Pillow)
tkinter는 Python 표준 라이브러리이므로 별도 설치가 필요 없습니다.
"""

import os
import sys
import zipfile
from tkinter import Tk, Canvas, messagebox
from PIL import Image, ImageTk

# --- 상수 정의 ---
os.chdir(os.path.dirname(__file__))
ZIP_FILE_NAME = 'cctv.zip'
IMAGE_DIR = 'cctv'


class MarsImageHelper:
    """
    이미지 파일 처리(압축 해제, 로드, 탐색)를 담당하는 클래스.
    """
    def __init__(self, zip_path, extract_to):
        """
        클래스 초기화 시 zip 파일 경로와 압축 해제 경로를 설정합니다.
        """
        self.zip_path = zip_path
        self.image_dir = extract_to
        self.image_list = []
        self.current_index = 0

    def unzip_images(self):
        """
        지정된 zip 파일의 압축을 해제합니다.
        폴더가 이미 존재하면 압축 해제를 건너뜁니다.
        """
        if not os.path.exists(self.zip_path):
            messagebox.showerror(
                '오류', f"'{self.zip_path}' 파일을 찾을 수 없습니다."
            )
            return False

        if os.path.exists(self.image_dir):
            print(f"'{self.image_dir}' 폴더가 이미 존재합니다. 압축 해제를 건너뜁니다.")
            return True

        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.image_dir)
            print(f"'{self.zip_path}' 파일의 압축을 풀어 '{self.image_dir}' 폴더를 생성했습니다.")
            return True
        except zipfile.BadZipFile:
            messagebox.showerror('오류', f"'{self.zip_path}'은(는) 유효한 zip 파일이 아닙니다.")
            return False
        except Exception as e:
            messagebox.showerror('오류', f"압축 해제 중 오류가 발생했습니다: {e}")
            return False

    def load_images(self):
        """
        압축 해제된 폴더에서 이미지 파일 목록을 불러옵니다.
        """
        if not os.path.exists(self.image_dir):
            return False

        try:
            # 지원하는 이미지 확장자 목록
            valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
            files = sorted(os.listdir(self.image_dir))
            self.image_list = [
                os.path.join(self.image_dir, f) for f in files
                if f.lower().endswith(valid_extensions)
            ]
            if not self.image_list:
                messagebox.showwarning('경고', f"'{self.image_dir}' 폴더에 이미지 파일이 없습니다.")
                return False
            return True
        except Exception as e:
            messagebox.showerror('오류', f"이미지 목록을 불러오는 중 오류 발생: {e}")
            return False

    def get_current_image_path(self):
        """현재 인덱스에 해당하는 이미지 파일 경로를 반환합니다."""
        if not self.image_list:
            return None
        return self.image_list[self.current_index]

    def next_image(self):
        """다음 이미지로 인덱스를 이동시킵니다."""
        if self.image_list:
            self.current_index = (self.current_index + 1) % len(self.image_list)

    def previous_image(self):
        """이전 이미지로 인덱스를 이동시킵니다."""
        if self.image_list:
            self.current_index = (self.current_index - 1) % len(self.image_list)


class ImageViewer(Tk):
    """
    Canvas를 사용한 이미지 뷰어
    """
    def __init__(self, image_helper):
        super().__init__()
        self.title('CCTV 이미지 뷰어')
        self.geometry('800x600')
        self.configure(bg='black')  # 배경색 설정
        
        self.image_helper = image_helper
        
        # Label 대신 Canvas 사용
        self.canvas = Canvas(self, width=800, height=600, bg='black')
        self.canvas.pack(expand=True, fill='both')
        
        # 이미지 참조 저장
        self.current_photo = None
        self.image_id = None
        
        self.bind('<Left>', self.show_previous_image)
        self.bind('<Right>', self.show_next_image)
        self.bind('<Escape>', lambda e: self.quit())
        
        self.focus_set()
        self.update_image()

    def update_image(self):
        """화면에 표시될 이미지를 업데이트합니다."""
        image_path = self.image_helper.get_current_image_path()
        if not image_path:
            self.quit()
            return

        try:
            # 이미지 열기
            image = Image.open(image_path)
            
            # RGB 변환
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 크기 조절
            image.thumbnail((750, 550), Image.Resampling.LANCZOS)
            
            # PhotoImage 생성
            self.current_photo = ImageTk.PhotoImage(image)
            
            # 기존 이미지 삭제
            if self.image_id:
                self.canvas.delete(self.image_id)
            
            # Canvas 중앙에 이미지 배치
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Canvas 크기가 아직 계산되지 않은 경우 기본값 사용
            if canvas_width <= 1:
                canvas_width = 800
            if canvas_height <= 1:
                canvas_height = 600
                
            x = canvas_width // 2
            y = canvas_height // 2
            
            self.image_id = self.canvas.create_image(x, y, image=self.current_photo, anchor='center')
            
            self.title(f'CCTV 이미지 뷰어 - {os.path.basename(image_path)}')
            
        except Exception as e:
            messagebox.showerror('이미지 로드 오류', f"파일을 열 수 없습니다: {image_path}\n{e}")
            self.quit()

    def show_next_image(self, event=None):
        """다음 이미지를 표시합니다."""
        self.image_helper.next_image()
        self.update_image()

    def show_previous_image(self, event=None):
        """이전 이미지를 표시합니다."""
        self.image_helper.previous_image()
        self.update_image()



def main():
    """
    메인 실행 함수.
    이미지 헬퍼를 초기화하고 이미지 뷰어를 실행합니다.
    """
    image_helper = MarsImageHelper(ZIP_FILE_NAME, IMAGE_DIR)

    if not image_helper.unzip_images():
        sys.exit(1)

    if not image_helper.load_images():
        sys.exit(1)

    app = ImageViewer(image_helper)
    app.mainloop()


if __name__ == '__main__':
    main()
