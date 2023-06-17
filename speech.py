import os
import sqlite3
import speech_recognition as sr

# Google Cloud 인증 키 파일 경로 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "test2-388310-65b7d7dfa68e.json"

# 데이터베이스 연결 및 쿼리 실행
def get_names_from_database():
    conn = sqlite3.connect("coffee.db")
    cursor = conn.cursor()

    query = "SELECT name FROM coffee"
    cursor.execute(query)

    names = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return names

# 데이터베이스에서 이름을 가져옴
target_names = get_names_from_database()

# 마이크를 통해 음성 입력 받기
def process_audio_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("마이크로부터 음성을 입력하세요:")
        audio = r.listen(source)

    return audio

while True:
    try:
        audio = process_audio_input()
        transcript = client.recognize_google_cloud(audio)
        print("인식된 텍스트:", transcript)

        for target_name in target_names:
            if target_name in transcript:
                print("타켓 데이터 '{}'가 포함되어 있습니다.".format(target_name))
                # 타켓 데이터를 활용하는 추가 작업 수행
                # ...
            else:
                print("타켓 데이터 '{}'가 포함되어 있지 않습니다.".format(target_name))

    except sr.UnknownValueError:
        print("음성을 인식할 수 없습니다.")
    except sr.RequestError as e:
        print("음성 인식 서비스에 접근할 수 없습니다. 오류: {}".format(e))