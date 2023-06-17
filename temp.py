import sys
import os
from google.cloud import dialogflow
import speech_recognition as sr
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class CoffeeKiosk(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

        # Dialogflow 인증 정보 설정
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'capstone-kiosk-eff1d91cef43.json'
        self.project_id = 'PROJECT_ID'
        self.session_id = 'SESSION_ID'
        self.language_code = 'ko-KR'

        # Dialogflow 세션 생성
        self.session_client = dialogflow.SessionsClient()
        self.session = self.session_client.session_path(self.project_id, self.session_id)

        # 주문한 메뉴와 수량을 저장할 리스트
        self.order_list = []

    def initUI(self):
        self.setWindowTitle('커피 키오스크')

        # 음성 인식 객체 생성
        self.recognizer = sr.Recognizer()

        # 아메리카노 이미지 추가
        am_img = QLabel(self)
        am_pixmap = QPixmap('americano.jpg').scaled(300, 300, Qt.KeepAspectRatio)
        am_img.setPixmap(am_pixmap)

        # 아메리카노 가격 추가
        self.am_price = 4500
        am_price_label = QLabel(f'{self.am_price}원', self)

        # 아메리카노 개수 선택
        self.am_spinbox = QSpinBox(self)
        self.am_spinbox.setMinimum(0)
        self.am_spinbox.setMaximum(20)
        self.am_spinbox.valueChanged.connect(self.update_total_price)

        # 아메리카노 버튼 추가
        btn1 = QPushButton('아메리카노', self)
        btn1.setStyleSheet("background-color: #A0522D; color: white;")
        btn1.clicked.connect(self.americano)

        # 카페라떼 이미지 추가
        latte_img = QLabel(self)
        latte_pixmap = QPixmap('latte.jpg').scaled(300, 300, Qt.KeepAspectRatio)
        latte_img.setPixmap(latte_pixmap)

        # 카페라떼 가격 추가
        self.latte_price = 5000
        latte_price_label = QLabel(f'{self.latte_price}원', self)

        # 카페라떼 개수 선택
        self.latte_spinbox = QSpinBox(self)
        self.latte_spinbox.setMinimum(0)
        self.latte_spinbox.setMaximum(20)
        self.latte_spinbox.valueChanged.connect(self.update_total_price)

        # 카페라떼 버튼 추가
        btn2 = QPushButton('카페라떼', self)
        btn2.setStyleSheet("background-color: #A0522D; color: white;")
        btn2.clicked.connect(self.latte)

        # 카푸치노 이미지 추가
        capp_img = QLabel(self)
        capp_pixmap = QPixmap('cappuccino.jpg').scaled(300, 300, Qt.KeepAspectRatio)
        capp_img.setPixmap(capp_pixmap)

        # 카푸치노 가격 추가
        self.capp_price = 5000
        capp_price_label = QLabel(f'{self.capp_price}원', self)

        # 카푸치노 개수 선택
        self.capp_spinbox = QSpinBox(self)
        self.capp_spinbox.setMinimum(0)
        self.capp_spinbox.setMaximum(20)
        self.capp_spinbox.valueChanged.connect(self.update_total_price)

        # 카푸치노 버튼 추가
        btn3 = QPushButton('카푸치노', self)
        btn3.setStyleSheet("background-color: #A0522D; color: white;")
        btn3.clicked.connect(self.cappuccino)

        # 카라멜마끼야또 이미지 추가
        caramel_img = QLabel(self)
        caramel_pixmap = QPixmap('caramelMacchiato.jpg').scaled(300, 300, Qt.KeepAspectRatio)
        caramel_img.setPixmap(caramel_pixmap)

        # 카라멜마끼야또 가격 추가
        self.caramel_price = 4500
        caramel_price_label = QLabel(f'{self.caramel_price}원', self)

        # 카라멜마끼야또 개수 선택
        self.caramel_spinbox = QSpinBox(self)
        self.caramel_spinbox.setMinimum(0)
        self.caramel_spinbox.setMaximum(20)
        self.caramel_spinbox.valueChanged.connect(self.update_total_price)
        # 카라멜마끼야또 버튼 추가
        btn4 = QPushButton('카라멜마끼야또', self)
        btn4.setStyleSheet("background-color: #A0522D; color: white;")
        btn4.clicked.connect(self.caramel)

        # 콜드블루 이미지 추가
        cb_img = QLabel(self)
        cb_pixmap = QPixmap('coldbrew.jpg').scaled(300, 300, Qt.KeepAspectRatio)
        cb_img.setPixmap(cb_pixmap)

        # 콜드블루 가격 추가
        self.cb_price = 4500
        cb_price_label = QLabel(f'{self.cb_price}원', self)

        # 콜드블루 개수 선택
        self.cb_spinbox = QSpinBox(self)
        self.cb_spinbox.setMinimum(0)
        self.cb_spinbox.setMaximum(20)
        self.cb_spinbox.valueChanged.connect(self.update_total_price)

        # 콜드블루 버튼 추가
        btn5 = QPushButton('콜드블루', self)
        btn5.setStyleSheet("background-color: #A0522D; color: white;")
        btn5.clicked.connect(self.cb)

        # 돌체콜드블루 이미지 추가
        dcb_img = QLabel(self)
        dcb_pixmap = QPixmap('dolceColdbrew.jpg').scaled(300, 300, Qt.KeepAspectRatio)
        dcb_img.setPixmap(dcb_pixmap)

        # 돌체콜드블루 가격 추가
        self.dcb_price = 5000
        dcb_price_label = QLabel(f'{self.dcb_price}원', self)

        # 돌체콜드블루 개수 선택
        self.dcb_spinbox = QSpinBox(self)
        self.dcb_spinbox.setMinimum(0)
        self.dcb_spinbox.setMaximum(20)
        self.dcb_spinbox.valueChanged.connect(self.update_total_price)

        # 돌체콜드블루 버튼 추가
        btn6 = QPushButton('돌체콜드블루', self)
        btn6.setStyleSheet("background-color: #A0522D; color: white;")
        btn6.clicked.connect(self.dcb)

        # 바닐라 아포카토 이미지 추가
        vaff_img = QLabel(self)
        vaff_pixmap = QPixmap('vanillaAffogato.jpg').scaled(300, 300, Qt.KeepAspectRatio)
        vaff_img.setPixmap(vaff_pixmap)

        # 바닐라 아포카토 가격 추가
        self.vaff_price = 5000
        vaff_price_label = QLabel(f'{self.vaff_price}원', self)

        # 바닐라 아포카토 개수 선택
        self.vaff_spinbox = QSpinBox(self)
        self.vaff_spinbox.setMinimum(0)
        self.vaff_spinbox.setMaximum(20)
        self.vaff_spinbox.valueChanged.connect(self.update_total_price)

        # 바닐라 아포카토 버튼 추가
        btn7 = QPushButton('바닐라 아포카토', self)
        btn7.setStyleSheet("background-color: #A0522D; color: white;")
        btn7.clicked.connect(self.vaff)

        # 화이트 초콜릿 모카 이미지 추가
        wcm_img = QLabel(self)
        wcm_pixmap = QPixmap('whiteChocolateMocha.jpg').scaled(300, 300, Qt.KeepAspectRatio)
        wcm_img.setPixmap(wcm_pixmap)

        # 화이트 초콜릿 모카 가격 추가
        self.wcm_price = 4500
        wcm_price_label = QLabel(f'{self.wcm_price}원', self)

        # 화이트 초콜릿 모카 개수 선택
        self.wcm_spinbox = QSpinBox(self)
        self.wcm_spinbox.setMinimum(0)
        self.wcm_spinbox.setMaximum(20)
        self.wcm_spinbox.valueChanged.connect(self.update_total_price)

        # 화이트 초콜릿 모카 버튼 추가
        btn8 = QPushButton('화이트 초콜릿 모카', self)
        btn8.setStyleSheet("background-color: #A0522D; color: white;")
        btn8.clicked.connect(self.wcm)

        # 구매 버튼 추가
        buy_btn = QPushButton('구매', self)
        buy_btn.setStyleSheet("background-color: #A0522D; color: white;")
        buy_btn.clicked.connect(self.buy)

        # 총 가격 레이블 추가
        self.total_price_label = QLabel('총 가격: 0원', self)

        # 주문 내역 테이블 추가
        self.order_table = QTableWidget(self)
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(['메뉴', '수량', '가격', '취소'])
        self.order_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.order_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.order_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.order_table.cellClicked.connect(self.change_quantity)
        self.order_table.setColumnWidth(0, 200)
        self.order_table.setColumnWidth(1, 50)
        self.order_table.setColumnWidth(2, 100)
        self.order_table.setColumnWidth(3, 50)

        # 음성 인식 버튼 추가
        voice_btn = QPushButton('음성 인식', self)
        voice_btn.setStyleSheet("background-color: #A0522D; color: white;")
        voice_btn.clicked.connect(self.voice_recognition)

        # 수직 박스 레이아웃에 위젯 추가
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        vbox.setAlignment(Qt.AlignCenter)
        vbox.addWidget(am_img)
        vbox.addWidget(am_price_label)
        vbox.addWidget(self.am_spinbox)
        vbox.addWidget(btn1)
        self.setCentralWidget(widget)

        vbox.addWidget(latte_img)
        vbox.addWidget(latte_price_label)
        vbox.addWidget(self.latte_spinbox)
        vbox.addWidget(btn2)
        self.setCentralWidget(widget)

        vbox.addWidget(capp_img)
        vbox.addWidget(capp_price_label)
        vbox.addWidget(self.capp_spinbox)
        vbox.addWidget(btn3)
        self.setCentralWidget(widget)

        vbox.addWidget(caramel_img)
        vbox.addWidget(caramel_price_label)
        vbox.addWidget(self.caramel_spinbox)
        vbox.addWidget(btn4)
        self.setCentralWidget(widget)

        vbox.addWidget(am_img)
        vbox.addWidget(am_price_label)
        vbox.addWidget(self.am_spinbox)
        vbox.addWidget(btn1)
        self.setCentralWidget(widget)

        vbox.addWidget(latte_img)
        vbox.addWidget(latte_price_label)
        vbox.addWidget(self.latte_spinbox)
        vbox.addWidget(btn2)
        self.setCentralWidget(widget)

        vbox.addWidget(capp_img)
        vbox.addWidget(capp_price_label)
        vbox.addWidget(self.capp_spinbox)
        vbox.addWidget(btn3)
        self.setCentralWidget(widget)

        vbox.addWidget(caramel_img)
        vbox.addWidget(caramel_price_label)
        vbox.addWidget(self.caramel_spinbox)
        vbox.addWidget(btn4)
        self.setCentralWidget(widget)

        # QGridLayout으로 레이아웃 변경
        grid = QGridLayout(widget)
        vbox.addLayout(grid)

        # 아메리카노 위젯 추가
        grid.addWidget(am_img, 0, 0)
        grid.addWidget(am_price_label, 1, 0)
        grid.addWidget(self.am_spinbox, 2, 0)
        grid.addWidget(btn1, 3, 0)

        # 카라멜마끼야또 위젯 추가
        grid.addWidget(caramel_img, 0, 1)
        grid.addWidget(caramel_price_label, 1, 1)
        grid.addWidget(self.caramel_spinbox, 2, 1)
        grid.addWidget(btn4, 3, 1)

        # 카페라떼 위젯 추가
        grid.addWidget(latte_img, 0, 2)
        grid.addWidget(latte_price_label, 1, 2)
        grid.addWidget(self.latte_spinbox, 2, 2)
        grid.addWidget(btn2, 3, 2)

        # 카푸치노 위젯 추가
        grid.addWidget(capp_img, 0, 3)
        grid.addWidget(capp_price_label, 1, 3)
        grid.addWidget(self.capp_spinbox, 2, 3)
        grid.addWidget(btn3, 3, 3)

        vbox.addWidget(self.total_price_label, alignment=Qt.AlignRight)
        vbox.addWidget(buy_btn, alignment=Qt.AlignRight)
        vbox.addWidget(voice_btn, alignment=Qt.AlignRight)
        vbox.addWidget(self.order_table)
        self.setCentralWidget(widget)

        self.setLayout(vbox)

        self.show()

    def americano(self):
        self.add_order('아메리카노', self.am_spinbox.value(), self.am_price)

    def latte(self):
        self.add_order('카페라떼', self.latte_spinbox.value(), self.latte_price)

    def cappuccino(self):
        self.add_order('카푸치노', self.capp_spinbox.value(), self.capp_price)

    def caramel(self):
        self.add_order('카라멜마끼야또', self.caramel_spinbox.value(), self.caramel_price)

    def add_order(self, coffee, quantity, price):
        if quantity > 0:
            for i in range(len(self.order_list)):
                if self.order_list[i][0] == coffee:
                    self.order_list[i][1] += quantity
                    self.order_list[i][2] = self.order_list[i][1] * price
                    self.update_order_table()
                    return
            self.order_list.append([coffee, quantity, quantity * price])
            self.update_order_table()

    def update_order_table(self):
        self.order_table.setRowCount(len(self.order_list))
        for i in range(len(self.order_list)):
            menu_item = QTableWidgetItem(self.order_list[i][0])
            quantity_item = QTableWidgetItem(str(self.order_list[i][1]))
            price_item = QTableWidgetItem(str(self.order_list[i][2]))
            cancel_btn = QPushButton('X')
            cancel_btn.setStyleSheet("background-color: #A0522D; color: white;")
            cancel_btn.clicked.connect(lambda _, row=i: self.cancel_order(row))
            self.order_table.setItem(i, 0, menu_item)
            self.order_table.setItem(i, 1, quantity_item)
            self.order_table.setItem(i, 2, price_item)
            self.order_table.setCellWidget(i, 3, cancel_btn)
        self.update_total_price()

    def change_quantity(self, row, column):
        if column == 1:
            quantity, ok = QInputDialog.getInt(self, '수량 변경', '수량을 입력하세요.', value=self.order_list[row][1], min=1, max=20)
            if ok:
                self.order_list[row][1] = quantity
                self.order_list[row][2] = quantity * self.get_price(self.order_list[row][0])
                self.update_order_table()

    def cancel_order(self, row):
        self.order_list.pop(row)
        self.update_order_table()

    def get_price(self, coffee):
        if coffee == '아메리카노':
            return self.am_price
        elif coffee == '카페라떼':
            return self.latte_price
        elif coffee == '카푸치노':
            return self.capp_price
        elif coffee == '카라멜마끼야또':
            return self.caramel_price

    def voice_recognition(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        try:
            query = self.recognizer.recognize_google(audio, language='ko-KR')
            self.select_coffee(query)
        except sr.UnknownValueError:
            QMessageBox.warning(self, '음성 인식 실패', '음성 인식 결과가 없습니다.')

    def select_coffee(self, query):
        if '아메리카노' in query:
            quantity = self.get_quantity(query)
            self.add_order('아메리카노', quantity, self.am_price)
        elif '카페라떼' in query:
            quantity = self.get_quantity(query)
            self.add_order('카페라떼', quantity, self.latte_price)
        elif '카푸치노' in query:
            quantity = self.get_quantity(query)
            self.add_order('카푸치노', quantity, self.capp_price)
        elif '카라멜마끼야또' in query:
            quantity = self.get_quantity(query)
            self.add_order('카라멜마끼야또', quantity, self.caramel_price)
        else:
            QMessageBox.warning(self, '음성 인식 실패', '음성 인식 결과에 해당하는 커피가 없습니다.')

    def get_quantity(self, query):
        words = query.split()
        for i in range(len(words)):
            if words[i].isdigit():
                return int(words[i])
        return 1

    def update_total_price(self):
        total_price = sum([order[2] for order in self.order_list])
        self.total_price_label.setText(f'총 가격: {total_price}원')

    def buy(self):
        if not self.order_list:
            QMessageBox.warning(self, '주문 실패', '커피를 선택해주세요.')

        else:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setText('주문하시겠습니까?')
            msg_box.setWindowTitle('주문 확인')
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            result = msg_box.exec_()
            if result == QMessageBox.Yes:
                QMessageBox.information(self, '주문 완료', '주문이 완료되었습니다.')
                self.order_list = []
                self.update_order_table()
                self.update_total_price()
            else:
                return
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeKiosk()
    sys.exit(app.exec_())