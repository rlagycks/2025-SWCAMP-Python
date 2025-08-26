#!/usr/bin/env python3
# cctv.py

"""
CCTV.zip 파일의 압축을 해제하고, YOLOv8 모델을 OpenCV DNN 모듈로 로드하여
폴더 내 이미지에서 사람(우주인 포함)을 탐지하고 결과를 표시합니다.
ultralytics는 모델 변환에만 사용하고, 탐지는 OpenCV로 수행합니다.

실행 전 필요한 라이브러리:
- Pillow, opencv-python, ultralytics, onnx
"""

import os
import sys
import zipfile
import cv2
import numpy as np
from tkinter import Tk, Canvas, messagebox
from PIL import Image, ImageTk
from ultralytics import YOLO

# --- 상수 정의 ---
ZIP_FILE_NAME = 'CCTV.zip'
IMAGE_DIR = 'cctv'
YOLO_MODEL_PT = 'yolov8m.pt'
ONNX_MODEL_PATH = 'yolov8m.onnx'


class MarsImageHelper:
    """
    이미지 파일 처리(압축 해제, 로드)를 담당하는 클래스.
    """
    def __init__(self, zip_path, extract_to):
        self.zip_path = zip_path
        self.image_dir = extract_to
        self.image_list = []

    def unzip_images(self):
        if not os.path.exists(self.zip_path):
            messagebox.showerror('오류', f"'{self.zip_path}' 파일을 찾을 수 없습니다.")
            return False
        if os.path.exists(self.image_dir):
            print(f"INFO: '{self.image_dir}' 폴더가 이미 존재합니다. 압축 해제를 건너뜁니다.")
            return True
        try:
            print(f"INFO: '{self.zip_path}' 파일의 압축을 해제합니다...")
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.image_dir)
            print(f"SUCCESS: 압축을 풀어 '{self.image_dir}' 폴더를 생성했습니다.")
            return True
        except Exception as e:
            messagebox.showerror('오류', f"압축 해제 중 오류: {e}")
            return False

    def load_images(self):
        if not os.path.exists(self.image_dir):
            return False
        try:
            valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
            files = sorted(os.listdir(self.image_dir))
            self.image_list = [
                os.path.join(self.image_dir, f) for f in files
                if f.lower().endswith(valid_extensions)
            ]
            if not self.image_list:
                messagebox.showwarning('경고', f"'{self.image_dir}' 폴더에 이미지 파일이 없습니다.")
                return False
            print(f"SUCCESS: 총 {len(self.image_list)}개의 이미지 파일을 찾았습니다.")
            return True
        except Exception as e:
            messagebox.showerror('오류', f"이미지 목록을 불러오는 중 오류 발생: {e}")
            return False


class PersonDetectorApp(Tk):
    """
    OpenCV DNN 모듈로 YOLOv8 모델을 실행하여 사람을 찾고,
    결과를 tkinter UI에 표시하는 애플리케이션 클래스.
    """
    def __init__(self, image_helper):
        super().__init__()
        self.title('OpenCV DNN + YOLOv8 CCTV 사람 탐지기')
        self.geometry('1200x800')
        self.image_helper = image_helper
        self.current_search_index = 0
        self.files_with_person_found = 0
        self.total_files_to_search = len(self.image_helper.image_list)

        self.canvas = Canvas(self, bg='black')
        self.canvas.pack(expand=True, fill='both')
        self.photo_on_canvas = None

        self.bind('<Return>', self.resume_search)
        self.bind('<Escape>', lambda e: self.quit())
        print("\n--- OpenCV DNN 기반 사람 탐색 시작 ---")

        # --- YOLOv8 ONNX 모델을 OpenCV로 로드 ---
        try:
            self.net = cv2.dnn.readNetFromONNX(ONNX_MODEL_PATH)
        except cv2.error as e:
            messagebox.showerror('모델 로드 오류', f"OpenCV가 ONNX 모델을 로드하지 못했습니다.\n기존 onnx 파일을 삭제하고 다시 실행해보세요.\n\n{e}")
            self.quit()
            return
            
        self.input_width = 640
        self.input_height = 640
        self.conf_threshold = 0.4  # 신뢰도 임계값 조정
        self.nms_threshold = 0.5

        self.after(100, self.search_next_image)

    def search_next_image(self, event=None):
        if self.current_search_index >= self.total_files_to_search:
            self.show_summary()
            return

        image_path = self.image_helper.image_list[self.current_search_index]
        progress = f"({self.current_search_index + 1}/{self.total_files_to_search})"
        print(f"\n{progress} 탐색 중: {os.path.basename(image_path)}")
        self.title(f'탐색 중... {progress} - {os.path.basename(image_path)}')

        image, found_people = self.detect_people_opencv_yolo(image_path)

        if found_people:
            self.files_with_person_found += 1
            print(f"  -> 결과: 사람 탐지됨! 계속하려면 Enter 키를 누르세요.")
            self.display_image(image)
        else:
            print("  -> 결과: 감지된 사람 없음.")
            self.current_search_index += 1
            self.after(10, self.search_next_image)

    def resume_search(self, event=None):
        self.current_search_index += 1
        self.search_next_image()

    def detect_people_opencv_yolo(self, image_path):
        frame = cv2.imread(image_path)
        if frame is None: return None, False

        # 1. 이미지 전처리
        blob = cv2.dnn.blobFromImage(
            frame, 1/255.0, (self.input_width, self.input_height),
            swapRB=True, crop=False
        )
        self.net.setInput(blob)
        
        # 2. 모델 추론
        preds = self.net.forward()
        
        # 3. 결과 후처리 (YOLOv8 출력 형식에 맞게 수정)
        frame_height, frame_width = frame.shape[:2]
        x_factor = frame_width / self.input_width
        y_factor = frame_height / self.input_height

        class_ids, confidences, boxes = [], [], []
        
        # 출력을 (8400, 84) 형태로 변환하여 처리 용이하게 함
        predictions = np.squeeze(preds).T
        
        for pred in predictions:
            class_scores = pred[4:]
            class_id = np.argmax(class_scores)
            confidence = class_scores[class_id]

            if confidence > self.conf_threshold and class_id == 0: # class_id 0 is 'person'
                confidences.append(float(confidence))
                
                cx, cy, w, h = pred[0:4]
                
                left = int((cx - w/2) * x_factor)
                top = int((cy - h/2) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                
                boxes.append([left, top, width, height])

        # Non-Maximum Suppression 적용
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)
        
        found = len(indices) > 0
        if found:
            for i in indices:
                box = boxes[i]
                left, top, width, height = box[0], box[1], box[2], box[3]
                cv2.rectangle(frame, (left, top), (left + width, top + height), (0, 255, 0), 3)
                cv2.putText(frame, "PERSON", (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        return frame, found

    def display_image(self, cv_image):
        if cv_image is None: return
        image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        pil_image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        self.photo_on_canvas = ImageTk.PhotoImage(pil_image)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width / 2, canvas_height / 2,
                                anchor='center', image=self.photo_on_canvas)

    def show_summary(self):
        print("\n--- 모든 이미지 탐색 완료 ---")
        summary_message = (
            f"총 {self.total_files_to_search}개 이미지 탐색 완료.\n\n"
            f"사람이 탐지된 이미지: {self.files_with_person_found}개"
        )
        messagebox.showinfo('탐색 완료', summary_message)
        self.quit()

def setup_model():
    """YOLOv8 모델을 다운로드하고 OpenCV 호환 ONNX로 변환합니다."""
    if os.path.exists(ONNX_MODEL_PATH):
        print(f"INFO: '{ONNX_MODEL_PATH}' 모델이 이미 존재합니다.")
        return True
    try:
        print("INFO: YOLOv8m 모델을 다운로드하고 ONNX로 변환합니다...")
        model = YOLO(YOLO_MODEL_PT)
        # 고정 크기(640x640) 모델로 변환하여 OpenCV 호환성 확보
        model.export(format='onnx', opset=12, imgsz=640)
        print("SUCCESS: 모델 변환 완료.")
        return True
    except Exception as e:
        messagebox.showerror('모델 오류', f"YOLO 모델 설정 중 오류가 발생했습니다: {e}")
        return False

def main():
    if not setup_model():
        sys.exit(1)
        
    image_helper = MarsImageHelper(ZIP_FILE_NAME, IMAGE_DIR)
    if not image_helper.unzip_images():
        sys.exit(1)
    if not image_helper.load_images():
        sys.exit(1)
        
    app = PersonDetectorApp(image_helper)
    app.mainloop()

if __name__ == '__main__':
    main()
