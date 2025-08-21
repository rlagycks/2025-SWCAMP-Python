import cv2
import time

class SmileDetector:
    def __init__(self, game_duration=30):
        # Haar Cascade 분류기 로드 (OpenCV 내장)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_smile.xml'
        )
        
        # 게임 설정
        self.smile_count = 0
        self.last_smile_state = False
        self.game_duration = game_duration  # 게임 시간 (초)
        self.start_time = None  # 게임 시작 시간
        
    def start_game(self):
        """게임 시작 시간 기록"""
        self.start_time = time.time()
        
    def get_remaining_time(self):
        """남은 시간 계산"""
        if self.start_time is None:
            return self.game_duration
        elapsed = time.time() - self.start_time
        remaining = max(0, self.game_duration - elapsed)
        return remaining
    
    def is_game_over(self):
        """게임 종료 여부 확인"""
        return self.get_remaining_time() <= 0
        
    def is_smiling(self, frame):
        """현재 프레임에서 웃음 여부 판단"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) == 0:
            return False
        
        # 제일 큰 얼굴 영역에서만 웃음 감지
        x, y, w, h = max(faces, key=lambda f: f[2]*f[1])
        roi_gray = gray[y:y+h, x:x+w]
        smiles = self.smile_cascade.detectMultiScale(
            roi_gray,
            scaleFactor=1.8,
            minNeighbors=20,
            minSize=(25, 25)
        )
        return len(smiles) > 0
    
    def process_frame(self, frame):
        """프레임 처리 및 PASS/재시도 텍스트와 색상 반환"""
        # 게임이 종료되었으면 처리하지 않음
        if self.is_game_over():
            return "TIME UP!", (255, 0, 0)
            
        smiling = self.is_smiling(frame)
        
        # 웃음 상태가 False → True 로 바뀔 때만 카운트 증가
        if smiling and not self.last_smile_state:
            self.smile_count += 1
            print(f"웃음 감지! 현재 점수: {self.smile_count}")
        
        self.last_smile_state = smiling
        
        if smiling:
            return "PASS", (0, 255, 0)
        else:
            return "Try again", (0, 0, 255)

def main():
    # 게임 시간 설정 (30초)
    GAME_TIME = 30
    
    detector = SmileDetector(game_duration=GAME_TIME)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return
    
    print(f"{GAME_TIME}초 동안 최대한 많이 웃어보세요!")
    print("게임이 곧 시작됩니다...")
    
    # 3초 카운트다운
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    print("게임 시작!")
    detector.start_game()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)  # 거울 효과
        
        text, color = detector.process_frame(frame)
        remaining_time = detector.get_remaining_time()
        
        # 메시지 오버레이
        cv2.putText(frame, text, (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)
        
        # 점수 표시
        cv2.putText(frame, f"Score: {detector.smile_count}", (50, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        
        # 남은 시간 표시
        cv2.putText(frame, f"Time: {remaining_time:.1f}s", (50, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 2)
        
        # 종료 안내
        cv2.putText(frame, "Press 'q' to quit", (50, 450),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
        
        cv2.imshow('Timed Smile Detection Game', frame)
        
        # 게임 종료 조건
        if cv2.waitKey(1) & 0xFF == ord('q') or detector.is_game_over():
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # 게임 결과 출력
    print(f"\n게임 종료!")
    print(f"최종 점수: {detector.smile_count}번")
    print(f"게임 시간: {GAME_TIME}초")

if __name__ == "__main__":
    main()
