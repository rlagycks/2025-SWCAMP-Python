#!/usr/bin/env python3
# jarvis.py

"""
시스템의 기본 마이크를 사용하여 음성을 녹음하고,
녹음된 파일을 텍스트로 변환하여 CSV 파일로 저장하는 스크립트.

실행 전 필요한 라이브러리:
- PyAudio (pip install PyAudio)
- SpeechRecognition (pip install SpeechRecognition)
- pydub (pip install pydub)
"""

import os
import sys
import csv
import wave
import pyaudio
import speech_recognition as sr
from datetime import datetime
from pydub import AudioSegment
from pydub.silence import split_on_silence

# --- 상수 정의 ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORDS_DIR = 'records'
CSV_HEADER = ['timestamp', 'recognized_text']


class AudioRecorder:
    """
    오디오 녹음 및 파일 저장을 담당하는 클래스.
    """
    def __init__(self):
        self.audio_interface = pyaudio.PyAudio()
        self._setup_directory()

    def _setup_directory(self):
        if not os.path.exists(RECORDS_DIR):
            try:
                os.makedirs(RECORDS_DIR)
                print(f"'{RECORDS_DIR}' 폴더를 생성했습니다.")
            except OSError as e:
                print(f"'{RECORDS_DIR}' 폴더 생성에 실패했습니다: {e}")
                sys.exit(1)

    def _generate_filename(self):
        now = datetime.now()
        filename = now.strftime('%Y%m%d-%H%M%S') + '.wav'
        return os.path.join(RECORDS_DIR, filename)

    def record_audio(self):
        try:
            stream = self.audio_interface.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
        except OSError as e:
            print(f'오디오 장치를 열 수 없습니다: {e}')
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
            stream.stop_stream()
            stream.close()
            self.audio_interface.terminate()
        return frames

    def save_recording(self, frames):
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


class SpeechToTextConverter:
    """
    녹음된 음성 파일을 텍스트로 변환하고 CSV로 저장하는 클래스.
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def _get_wav_files(self):
        """'records' 폴더에서 .wav 파일 목록을 가져옵니다."""
        if not os.path.exists(RECORDS_DIR):
            return []
        return [f for f in os.listdir(RECORDS_DIR) if f.endswith('.wav')]

    def _create_csv_path(self, wav_filename):
        """WAV 파일명에 해당하는 CSV 파일 경로를 생성합니다."""
        base_name = os.path.splitext(wav_filename)[0]
        return os.path.join(RECORDS_DIR, base_name + '.csv')

    def transcribe_audio_chunk(self, audio_chunk):
        """오디오 청크를 텍스트로 변환합니다."""
        try:
            with audio_chunk.export(format='wav') as f:
                audio_data = sr.AudioFile(f)
                with audio_data as source:
                    audio_content = self.recognizer.record(source)
            return self.recognizer.recognize_google(
                audio_content, language='ko-KR'
            )
        except sr.UnknownValueError:
            return '[인식 불가]'
        except sr.RequestError:
            return '[API 요청 실패]'

    def process_recordings(self):
        """모든 녹음 파일을 순회하며 STT를 수행하고 CSV로 저장합니다."""
        wav_files = self._get_wav_files()
        if not wav_files:
            print(f"'{RECORDS_DIR}' 폴더에 분석할 음성 파일이 없습니다.")
            return

        for wav_file in wav_files:
            wav_path = os.path.join(RECORDS_DIR, wav_file)
            csv_path = self._create_csv_path(wav_file)

            # 이미 분석된 파일은 건너뜁니다.
            if os.path.exists(csv_path):
                print(f"'{wav_file}'은(는) 이미 분석되었습니다. 건너뜁니다.")
                continue

            print(f"\n'{wav_file}' 파일 분석 중...")
            try:
                sound = AudioSegment.from_wav(wav_path)
                chunks = split_on_silence(
                    sound,
                    min_silence_len=500,
                    silence_thresh=sound.dBFS - 14,
                    keep_silence=100
                )
            except Exception as e:
                print(f"오디오 파일을 처리하는 중 오류 발생: {e}")
                continue

            results = []
            total_duration_ms = 0
            for i, chunk in enumerate(chunks):
                timestamp_sec = total_duration_ms / 1000.0
                text = self.transcribe_audio_chunk(chunk)
                results.append({'timestamp': f'{timestamp_sec:.2f}s', 'recognized_text': text})
                print(f"  - {timestamp_sec:.2f}s: {text}")
                total_duration_ms += len(chunk)

            self.save_to_csv(results, csv_path)

    def save_to_csv(self, data, csv_path):
        """분석 결과를 CSV 파일로 저장합니다."""
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
                writer.writeheader()
                writer.writerows(data)
            print(f"분석 결과가 '{csv_path}'에 저장되었습니다.")
        except IOError as e:
            print(f"CSV 파일 저장 중 오류 발생: {e}")


def main():
    """
    메인 실행 함수.
    녹음과 STT 변환을 순차적으로 진행합니다.
    """
    # 1. 음성 녹음
    recorder = AudioRecorder()
    recorded_frames = recorder.record_audio()
    if recorded_frames:
        recorder.save_recording(recorded_frames)

    # 2. 녹음된 파일 STT 변환
    print('\n--- 음성 파일 분석 시작 ---')
    converter = SpeechToTextConverter()
    converter.process_recordings()
    print('--- 모든 분석 완료 ---')


if __name__ == '__main__':
    main()
