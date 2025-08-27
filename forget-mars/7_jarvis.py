#!/usr/bin/env python3
# jarvis.py

"""
시스템의 기본 마이크를 사용하여 음성을 녹음하고,
지정된 폴더에 '년월일-시간분초.wav' 형식으로 저장하는 스크립트.

실행 전 'PyAudio' 라이브러리 설치가 필요합니다.
(pip install PyAudio)
"""

import os
import sys
import wave
import pyaudio
from datetime import datetime

# --- 녹음 관련 상수 정의 ---
CHUNK = 1024
FORMAT = pyaudio.paInt16  # 16비트 오디오 포맷
CHANNELS = 1              # 모노 채널
RATE = 44100              # 샘플링 레이트 (Hz)
RECORDS_DIR = 'records'   # 녹음 파일을 저장할 하위 폴더 이름


class AudioRecorder:
    """
    오디오 녹음 및 파일 저장을 담당하는 클래스.
    """
    def __init__(self):
        """
        AudioRecorder 클래스의 인스턴스를 초기화하고,
        PyAudio 객체를 준비하며 저장 폴더를 설정합니다.
        """
        self.audio_interface = pyaudio.PyAudio()
        self._setup_directory()

    def _setup_directory(self):
        """
        녹음 파일을 저장할 'records' 폴더가 없으면 생성합니다.
        """
        if not os.path.exists(RECORDS_DIR):
            try:
                os.makedirs(RECORDS_DIR)
                print(f"'{RECORDS_DIR}' 폴더를 생성했습니다.")
            except OSError as e:
                print(f"'{RECORDS_DIR}' 폴더 생성에 실패했습니다: {e}")
                sys.exit(1)

    def _generate_filename(self):
        """
        현재 날짜와 시간을 기반으로 파일 이름을 생성합니다.
        형식: '년월일-시간분초.wav'
        """
        now = datetime.now()
        filename = now.strftime('%Y%m%d-%H%M%S') + '.wav'
        return os.path.join(RECORDS_DIR, filename)

    def record_audio(self):
        """
        시스템의 기본 마이크로부터 오디오 스트림을 열고 녹음을 시작합니다.
        사용자가 Ctrl+C를 누르면 녹음이 중지됩니다.
        """
        try:
            stream = self.audio_interface.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
        except OSError as e:
            print(f'오디오 장치를 열 수 없습니다. 마이크가 연결되어 있는지 확인하세요: {e}')
            return None

        print('녹음을 시작합니다... (중지하려면 Ctrl+C를 누르세요)')
        frames = []

        try:
            while True:
                data = stream.read(CHUNK)
                frames.append(data)
        except KeyboardInterrupt:
            print('\n녹음이 중지되었습니다.')
        finally:
            # 스트림과 PyAudio 인터페이스를 안전하게 닫습니다.
            stream.stop_stream()
            stream.close()
            self.audio_interface.terminate()

        return frames

    def save_recording(self, frames):
        """
        녹음된 오디오 프레임들을 .wav 파일로 저장합니다.
        """
        if not frames:
            print('녹음된 데이터가 없어 파일을 저장하지 않습니다.')
            return

        filename = self._generate_filename()

        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(self.audio_interface.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
            print(f"녹음 파일이 '{filename}'(으)로 저장되었습니다.")
        except Exception as e:
            print(f'파일 저장 중 오류가 발생했습니다: {e}')


def main():
    """
    메인 실행 함수.
    AudioRecorder를 사용하여 녹음을 진행하고 파일을 저장합니다.
    """
    recorder = AudioRecorder()
    recorded_frames = recorder.record_audio()

    if recorded_frames:
        recorder.save_recording(recorded_frames)


if __name__ == '__main__':
    main()
