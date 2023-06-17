'''
import os
from google.cloud import speech
import sqlite3

# Google Cloud 인증 키 파일 경로 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "test2-388310-65b7d7dfa68e.json"

# 음성 파일 경로 설정
audio_file_path = "audio.wav"

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

# 클라이언트 초기화
client = speech.SpeechClient()

# 음성 파일을 읽어들임
with open(audio_file_path, "rb") as audio_file:
    audio_data = audio_file.read()

# 음성을 텍스트로 변환
audio = speech.RecognitionAudio(content=audio_data)
config = speech.RecognitionConfig(language_code="ko-KR")

response = client.recognize(config=config, audio=audio)

# 인식된 텍스트 확인 및 타켓 데이터 검사
for result in response.results:
    transcript = result.alternatives[0].transcript
    print("인식된 텍스트:", transcript)

    for target_name in target_names:
        if target_name in transcript:
            print("타켓 데이터 '{}'가 포함되어 있습니다.".format(target_name))
            # 타켓 데이터를 활용하는 추가 작업 수행
            # ...
        else:
            print("타켓 데이터 '{}'가 포함되어 있지 않습니다.".format(target_name))
'''

import os
import speech_recognition as sr
import sqlite3

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

try:
    while True:
        r = sr.Recognizer()

        with sr.Microphone() as source:
            print('음성을 입력하세요')
            audio = r.listen(source)
            try:
                stt = r.recognize_google(audio, language='ko-KR')
                print('음성변환 : ' + stt)

                for target_name in target_names:
                    if target_name in stt:
                        print("타켓 데이터 '{}'가 포함되어 있습니다.".format(target_name))
                        # 타켓 데이터를 활용하는 추가 작업 수행
                        image_label = QLabel(self)
                        pixmap = QPixmap(image_path).scaled(200, 200, Qt.KeepAspectRatio)
                        image_label.setPixmap(pixmap)

                        # Create QLabel for the price
                        price_label = QLabel(f'{price}원', self)

                        # Create QPushButton for menu item
                        btn = QPushButton(name, self)
                        btn.setStyleSheet("background-color: #A0522D; color: white;")
                        btn.clicked.connect(lambda _, name=name: self.menu_item_clicked(name))

                        # Connect the click event of the image_label to menu_item_clicked
                        image_label.mousePressEvent = lambda _, name=name: self.menu_item_clicked(name)

                    else:
                        print("타켓 데이터 '{}'가 포함되어 있지 않습니다.".format(target_name))

            except sr.UnknownValueError:
                print('오디오를 이해할 수 없습니다.')
            except sr.RequestError as e:
                print(f'에러가 발생하였습니다. 에러원인 : {e}')

except KeyboardInterrupt:
    pass
