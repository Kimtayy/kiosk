import sqlite3
import sys
import os
from google.cloud import dialogflow
import speech_recognition as sr
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import pyaudio
import wave





class AdminLoginDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()

        id_label = QLabel('아이디')
        self.id_edit = QLineEdit()
        vbox.addWidget(id_label)
        vbox.addWidget(self.id_edit)

        pw_label = QLabel('비밀번호')
        self.pw_edit = QLineEdit()
        self.pw_edit.setEchoMode(QLineEdit.Password)
        vbox.addWidget(pw_label)
        vbox.addWidget(self.pw_edit)

        hbox = QHBoxLayout()
        login_btn = QPushButton('로그인')
        login_btn.clicked.connect(self.accept)
        hbox.addWidget(login_btn)

        cancel_btn = QPushButton('취소')
        cancel_btn.clicked.connect(self.reject)
        hbox.addWidget(cancel_btn)

        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def get_id_pw(self):
        return self.id_edit.text(), self.pw_edit.text()


class CoffeeKiosk(QMainWindow):
    def __init__(self):
        super().__init__()

        self.order_items = []
        self.total_price = 0
        self.initUI()

        # Dialogflow 인증 정보 설정
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'test2-388310-65b7d7dfa68e.json'
        self.project_id = 'PROJECT_ID'
        self.session_id = 'SESSION_ID'
        self.language_code = 'ko-KR'

        # Dialogflow 세션 생성
        self.session_client = dialogflow.SessionsClient()
        self.session = self.session_client.session_path(self.project_id, self.session_id)

        # 주문한 메뉴와 수량을 저장할 리스트
        self.order_list = []

    def initUI(self):

        menubar = self.menuBar()
        admin_menu = menubar.addMenu('관리자')

        admin_login_action = QAction('로그인', self)
        admin_login_action.triggered.connect(self.show_admin_login)
        admin_menu.addAction(admin_login_action)

        self.setWindowTitle('커피 키오스크')

        # 음성 인식 객체 생성
        self.recognizer = sr.Recognizer()


        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a grid layout
        layout = QGridLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)

        # Connect to the SQLite database
        conn = sqlite3.connect('coffee.db')
        cursor = conn.cursor()

        # Fetch the menu items from the database
        cursor.execute("SELECT * FROM coffee")
        menu_items = cursor.fetchall()

        # Create the menu items dynamically using a loop
        for index, item in enumerate(menu_items):
            name = item[1]
            image_path = item[2]
            price = item[3]

            # Create QLabel for the image
            image_label = QLabel(self)
            pixmap = QPixmap(image_path).scaled(200, 200, Qt.KeepAspectRatio)
            image_label.setPixmap(pixmap)

            # Create QLabel for the price
            price_label = QLabel(f'{price}원', self)

            # # Create QSpinBox for quantity selection
            # spinbox = QSpinBox(self)
            # spinbox.setMinimum(0)
            # spinbox.setMaximum(20)
            # spinbox.valueChanged.connect(self.update_total_price)

            # Create QPushButton for menu item
            btn = QPushButton(name, self)
            btn.setStyleSheet("background-color: #A0522D; color: white;")
            btn.clicked.connect(lambda _, name=name: self.menu_item_clicked(name))

            # Add the widgets to the layout
            layout.addWidget(image_label, index // 4 * 4, index % 4)
            layout.addWidget(price_label, index // 4 * 4 + 1, index % 4)
            # layout.addWidget(spinbox, index // 4 * 4 + 2, index % 4)
            layout.addWidget(btn, index // 4 * 4 + 2, index % 4)

        # Set column and row stretch
        layout.setColumnStretch(0, 1)
        layout.setRowStretch(index // 4 + 3, 1)

        # Close the database connection
        # conn.close()

        # Create a table for order items
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["메뉴", "수량", "가격", "취소"])
        self.order_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.order_table.setSelectionBehavior(QTableWidget.SelectRows)

        # Create a layout for the order section
        order_layout = QVBoxLayout()

        # Create QLabel for total price
        self.total_price_label = QLabel()

        # Create QPushButton for purchase
        purchase_button = QPushButton("구매")
        purchase_button.setStyleSheet("background-color: #008000; color: white;")
        purchase_button.clicked.connect(self.purchase_items)
        order_layout.addWidget(purchase_button)

        # Create QPushButton for cancel
        cancel_button = QPushButton('취소', self)
        cancel_button.setStyleSheet("background-color: #FF0000; color: white;")
        cancel_button.clicked.connect(self.cancel_clicked)
        order_layout.addWidget(cancel_button)

        # Add the order_layout to the main layout
        layout.addLayout(order_layout, (index // 4) * 4 + 4, 0, 1, 4)

        # 음성 인식을 위한 QPushButton 생성
        speech_recognition_button = QPushButton("음성 인식 시작", self)
        speech_recognition_button.setStyleSheet("background-color: #4169E1; color: white;")
        speech_recognition_button.clicked.connect(self.start_speech_recognition)
        layout.addWidget(speech_recognition_button, index // 4, (index % 4) * 2, 1, 2)


        # Create a layout for the order table
        order_table_layout = QVBoxLayout()
        order_table_layout.addWidget(self.order_table)

        # Add the order_table_layout to the main layout
        layout.addLayout(order_table_layout, (index // 4) * 4 + 5, 0, 1, 4)

        # Create a QLabel for total price
        self.total_price_label = QLabel()
        layout.addWidget(self.total_price_label, index // 4 + 8, 3, 1, 4)

        # Close the database connection
        self.show()
        conn.close()
    
    def start_speech_recognition(self):
        # 녹음된 오디오를 저장할 경로를 정의합니다
        audio_path = "recorded_audio.wav"

        # 인식기 인스턴스를 생성합니다
        recognizer = sr.Recognizer()

        # 마이크 인스턴스를 생성합니다
        microphone = sr.Microphone()

        with microphone as source:
            # 소음 환경에서 더 나은 인식을 위해 주변 소음 임계값을 조정합니다
            recognizer.adjust_for_ambient_noise(source)

            print("듣는 중...")

            try:
                # 사용자로부터 오디오 입력을 캡처합니다
                audio = recognizer.listen(source)

                # 캡처한 오디오를 파일에 저장합니다
                with open(audio_path, "wb") as file:
                    file.write(audio.get_wav_data())

                print("음성 인식이 완료되었습니다.")

                # 캡처한 오디오에 대해 음성 인식을 수행합니다
                recognized_text = recognizer.recognize_google(audio, language="ko-KR")
                print("인식된 텍스트:", recognized_text)

                # 인식된 텍스트를 처리하거나 명령에 따라 작업을 수행합니다
                self.process_recognized_text(recognized_text)

            except sr.UnknownValueError:
                print("음성 인식이 이해되지 않았습니다.")

            except sr.RequestError as e:
                print("음성 인식 서비스에서 결과를 요청할 수 없습니다:", e)


    def process_recognized_text(self, text):
        # 인식된 텍스트에 따라 작업을 수행합니다
        # 여기에 원하는 로직을 구현할 수 있습니다
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
        
        if target_names in text:
            # 주문 명령을 처리합니다
            self.process_order_command()

        else:
            # 잘못된 명령입니다
            print("잘못된 명령입니다.")

    def menu_item_clicked(self, name):
        # Handle the menu item clicked event
        # print(f"Menu item clicked: {name}")
        
         # Connect to the SQLite database
        conn = sqlite3.connect('coffee.db')
        cursor = conn.cursor()

        # Check if the menu item already exists in the order table
        for row in range(self.order_table.rowCount()):
            item_name = self.order_table.item(row, 0).text()
            if item_name == name:
                return  # Skip adding the menu item if it already exists

        # Fetch the price from the database based on the menu item name
        cursor.execute("SELECT price FROM coffee WHERE name=?", (name,))
        result = cursor.fetchone()
        if result:
            price = result[0]

            # Add the clicked menu item to the order table
            row = self.order_table.rowCount()
            self.order_table.insertRow(row)
            self.order_table.setItem(row, 0, QTableWidgetItem(name))

            # Create QSpinBox for quantity selection
            spinbox = QSpinBox(self)
            spinbox.setMinimum(0)
            spinbox.setMaximum(20)
            spinbox.setValue(1)
            spinbox.valueChanged.connect(lambda value, row=row, price=price: self.update_item_price(row, price, value))
            self.order_table.setCellWidget(row, 1, spinbox)

            # Calculate the total price for the initial quantity
            total_price = price * spinbox.value()
            self.order_table.setItem(row, 2, QTableWidgetItem(str(total_price)))

            # Create QPushButton for cancel
            cancel_button = QPushButton('취소', self)
            cancel_button.setStyleSheet("background-color: #FF0000; color: white;")
            cancel_button.clicked.connect(self.cancel_item_clicked)
            self.order_table.setCellWidget(row, 3, cancel_button)

            self.update_total_price()

        # Close the database connection
        conn.close()

    def update_item_price(self, row, price, quantity):
        total_price = price * quantity
        self.order_table.setItem(row, 2, QTableWidgetItem(str(total_price)))
        self.update_total_price()

    def cancel_item_clicked(self):
        # Handle the cancel item clicked event
        button = self.sender()
        if button:
            row = self.order_table.indexAt(button.pos()).row()
            self.order_table.removeRow(row)
            self.update_total_price()

    def update_total_price(self):
        total_price = sum(int(self.order_table.item(row, 2).text()) for row in range(self.order_table.rowCount()))
        self.total_price_label.setText(f'총 가격: {total_price}원')

    def purchase_clicked(self):
        # Handle the purchase button clicked event
        total_price = 0
        for row in range(self.order_table.rowCount()):
            price_item = self.order_table.item(row, 2)
            if price_item:
                price = int(price_item.text())
                total_price += price
        print(f"Total Price: {total_price}")

    def cancel_clicked(self):
        # Handle the cancel button clicked event
        self.order_table.clearContents()
        self.order_table.setRowCount(0)

    def purchase_items(self):
        # Perform the purchase logic here
        print("Purchase items")

        # Clear the order table and update the total price
        self.order_table.clearContents()
        self.update_total_price()

    def show_admin_login(self):
        dialog = AdminLoginDialog()
        dialog.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.ImhNoAutoUppercase)
        if dialog.exec_() == QDialog.Accepted:
            id, pw = dialog.get_id_pw()
            if id == 'admin' and pw == '1111':
                self.show_new_window()
                #QMessageBox.information(self, '로그인 성공', '로그인에 성공했습니다.')
            else:
                QMessageBox.warning(self, '로그인 실패', '아이디 또는 비밀번호가 올바르지 않습니다.')





# 메인 애플리케이션 실행
app = QApplication([])
window = CoffeeKiosk()
# window.show_admin_login()
app.exec_()
