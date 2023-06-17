import sqlite3
from datetime import datetime
import sys
import os
import time
import pyaudio
import wave
from google.cloud import dialogflow
from google.cloud import speech
import speech_recognition as sr
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *




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

class CoffeeShop(QMainWindow):
    def __init__(self):
        super().__init__()

        # UI 초기화
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.setGeometry(10, 10, 720, 960)

        # 데이터베이스에서 커피 정보 가져오기
        self.updateCoffeeInfo()

        # 2초마다 커피 정보 업데이트
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateCoffeeInfo)
        self.timer.start(2000)

    def updateCoffeeInfo(self):
        # Connect to coffee.db
        conn = sqlite3.connect("coffee.db")
        cursor = conn.cursor()

        # Fetch a random coffee from the database
        cursor.execute("SELECT image, name, price FROM coffee ORDER BY RANDOM() LIMIT 1")
        coffee = cursor.fetchone()

        if coffee is not None:
            image, name, price = coffee

            # Load image from file
            pixmap = QPixmap(image)
            self.label.setPixmap(pixmap)
            self.label.setToolTip(f"Name: {name}\nPrice: {price}")

        # Close database connection
        conn.close()

    def mousePressEvent(self, event):
        # 클릭 시 창 닫히고 CoffeeKiosk 클래스 실행
        self.close()
        self.kiosk = CoffeeKiosk()
        self.kiosk.show()


class CoffeeKiosk(QMainWindow):
    def __init__(self):
        super().__init__()

        self.order_items = []
        self.total_price = 0
        self.initUI()

        # # Dialogflow 인증 정보 설정
        # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'test2-388310-65b7d7dfa68e.json'
        # self.project_id = 'PROJECT_ID'
        # self.session_id = 'SESSION_ID'
        # self.language_code = 'ko-KR'

        # # Dialogflow 세션 생성
        # self.session_client = dialogflow.SessionsClient()
        # self.session = self.session_client.session_path(self.project_id, self.session_id)

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

            # Create QPushButton for menu item
            btn = QPushButton(name, self)
            btn.setStyleSheet("background-color: #A0522D; color: white;")
            btn.clicked.connect(lambda _, name=name: self.menu_item_clicked(name))

            # Connect the click event of the image_label to menu_item_clicked
            image_label.mousePressEvent = lambda _, name=name: self.menu_item_clicked(name)

            # Add the widgets to the layout
            layout.addWidget(image_label, index // 4 * 4, index % 4)
            layout.addWidget(price_label, index // 4 * 4 + 1, index % 4)
            # layout.addWidget(spinbox, index // 4 * 4 + 2, index % 4)
            layout.addWidget(btn, index // 4 * 4 + 2, index % 4)

            # Limit the number of menu items to 12 (3 rows x 4 columns)
            if index >= 11:
                break

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
        # purchase_button.clicked.connect(self.purchase_items)
        purchase_button.clicked.connect(self.show_purchase_confirmation)
        order_layout.addWidget(purchase_button)

        # Create QPushButton for cancel
        cancel_button = QPushButton('취소', self)
        cancel_button.setStyleSheet("background-color: #FF0000; color: white;")
        cancel_button.clicked.connect(self.cancel_clicked)
        order_layout.addWidget(cancel_button)


        voice_button = QPushButton('음성 인식', self)
        voice_button.setStyleSheet("background-color: #FF0000; color: white;")
        voice_button.clicked.connect(self.voice_recognition_clicked)
        order_layout.addWidget(voice_button)






        # Add the order_layout to the main layout
        layout.addLayout(order_layout, (index // 4) * 4 + 4, 0, 1, 4)

        # Create a layout for the order table
        order_table_layout = QVBoxLayout()
        order_table_layout.addWidget(self.order_table)

        # Add the order_table_layout to the main layout
        layout.addLayout(order_table_layout, (index // 4) * 4 + 5, 0, 1, 4)

        # Create a QLabel for total price
        self.total_price_label = QLabel()
        layout.addWidget(self.total_price_label, (index // 4) * 4 + 5, 3, 1, 4)

        # 창의 크기를 설정
        window_width = 818
        window_height = 1038

        # 현재 화면의 가운데 위치를 계산
        screen_geometry = QDesktopWidget().availableGeometry()
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2

        # 창의 위치와 크기 설정
        self.setGeometry(x, y, window_width, window_height)
        self.show()
        # Close the database connection
        conn.close()

    


    def voice_recognition_clicked(self):
        # Handle the voice recognition button clicked event
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Speak now...")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language="ko-KR")
            print("You said: " + text)
            self.menu_item_clicked(text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

        # Measure the time taken for voice recognition
        start_time = time.time()
        end_time = time.time()
        duration = end_time - start_time
        if duration < 2:
            # If the voice recognition is too short, assume it is a static noise and skip it
            print("Voice recognition is too short, assuming it is a static noise and skipping it")
        else:
            # If the voice recognition is long enough, add it to the order table
            self.menu_item_clicked(text)




    def menu_item_clicked(self, name):
        
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
    
    def show_purchase_confirmation(self):

        conn = sqlite3.connect('purchaseLog.db')
        cursor = conn.cursor()

        # Create a new window for purchase confirmation
        self.purchase_dialog = QDialog(self)
        self.purchase_dialog.setWindowTitle("구매 확인")

        # Get the coffee names and quantities from the order_table
        purchase_info = []
        for row in range(self.order_table.rowCount()):
            coffee_name = self.order_table.item(row, 0).text()
            quantity = self.order_table.cellWidget(row, 1).value()
            purchase_info.append(coffee_name + " (수량: " + str(quantity) + ")")

        # Create QLabel for purchase information
        purchase_info_label = QLabel()
        purchase_info_label.setText("구매 정보: " + "\n".join(purchase_info))
        purchase_info_label.setStyleSheet("font-size: 14pt")  # Adjust the font size as desired

        # Update the total price
        self.update_total_price()

        # Create QLabel for total price
        total_price_label = QLabel()
        total_price_label.setText(self.total_price_label.text())
        total_price_label.setStyleSheet("font-size: 14pt")  # Adjust the font size as desired

        # Create QPushButton for purchase confirmation
        confirm_button = QPushButton("구매 확정")
        confirm_button.clicked.connect(self.confirm_purchase)

        # Create QVBoxLayout for the purchase confirmation window
        layout = QVBoxLayout()
        layout.addWidget(purchase_info_label)
        layout.addWidget(total_price_label)
        layout.addWidget(confirm_button)

        # Set the layout for the purchase dialog
        self.purchase_dialog.setLayout(layout)

        # Get the current date and time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Iterate over the rows in the order table
        for row in range(self.order_table.rowCount()):
            # Get the coffee name, quantity, and price from the table
            coffee_name = self.order_table.item(row, 0).text()
            quantity = self.order_table.cellWidget(row, 1).value()
            price = self.order_table.item(row, 2).text()

            # Calculate the total price
            total_price = int(price)

            # Insert the purchase information into the purchaseLog table
            cursor.execute("INSERT INTO purchaseLog (purchase_date, coffee_name, quantity, total_price) VALUES (?, ?, ?, ?)",
                        (current_time, coffee_name, quantity, total_price))

        # Commit the changes to the database
        conn.commit()
        # Close the database connection
        conn.close()

        # Show the purchase confirmation dialog
        self.purchase_dialog.exec_()
    
    def confirm_purchase(self):
        # Close the purchase dialog
        self.purchase_dialog.close()

        # Clear the order table
        self.order_table.clearContents()
        self.order_table.setRowCount(0)

        # Reset the total price label
        self.total_price_label.setText("총 가격: 0 원")

        # Show the main window again
        self.show()

    def close_purchase_window(self):
        if hasattr(self, 'purchase_window'):
            self.purchase_window.close()

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

    def show_new_window(self):
        self.new_window = QMainWindow()
        self.new_window.setWindowTitle('관리자 창')


        label = QLabel("새로운 창")
        layout = QVBoxLayout()
        layout.addWidget(label)
        widget = QWidget()
        widget.setLayout(layout)
        self.new_window.setCentralWidget(widget)
        self.new_window.show()

    def closeEvent(self, event):
        if self.new_window is not None:
            self.new_window.close()
        event.accept()



if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    coffeeShop = CoffeeShop()
    # 창의 크기를 설정
    window_width = 818
    window_height = 1038

    # 현재 화면의 가운데 위치를 계산
    screen_geometry = QDesktopWidget().availableGeometry()
    x = (screen_geometry.width() - window_width) // 2
    y = (screen_geometry.height() - window_height) // 2

    # 창의 위치와 크기 설정
    coffeeShop.setGeometry(x, y, window_width, window_height)
    coffeeShop.show()
    sys.exit(app.exec_())

