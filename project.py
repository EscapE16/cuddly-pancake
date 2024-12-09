import io
import datetime
import sqlite3
import sys
import csv

from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog, QInputDialog, QListWidgetItem, \
    QPushButton, QLabel, QVBoxLayout, QLayout, QScrollArea, QWidget


template = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1225</width>
    <height>621</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QCalendarWidget" name="calendarWidget">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>50</y>
      <width>451</width>
      <height>401</height>
     </rect>
    </property>
   </widget>
   <widget class="QLineEdit" name="lineEdit">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>470</y>
      <width>441</width>
      <height>22</height>
     </rect>
    </property>
   </widget>
   <widget class="QPushButton" name="addEventBtn">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>510</y>
      <width>441</width>
      <height>28</height>
     </rect>
    </property>
    <property name="text">
     <string>Добавить событие</string>
    </property>
   </widget>
   <widget class="QPushButton" name="editEventBtn">
    <property name="geometry">
     <rect>
      <x>460</x>
      <y>510</y>
      <width>391</width>
      <height>28</height>
     </rect>
    </property>
    <property name="text">
     <string>Редактировать событие</string>
    </property>
   </widget>
   <widget class="QPushButton" name="deleteEventBtn">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>550</y>
      <width>441</width>
      <height>28</height>
     </rect>
    </property>
    <property name="text">
     <string>Удалить событие</string>
    </property>
   </widget>
   <widget class="QTimeEdit" name="timeEdit">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>10</y>
      <width>451</width>
      <height>22</height>
     </rect>
    </property>
   </widget>
   <widget class="QListWidget" name="eventList">
    <property name="geometry">
     <rect>
      <x>470</x>
      <y>46</y>
      <width>381</width>
      <height>450</height>
     </rect>
    </property>
   </widget>
   <widget class="QPushButton" name="saveEventsBtn">
    <property name="geometry">
     <rect>
      <x>460</x>
      <y>550</y>
      <width>190</width>
      <height>28</height>
     </rect>
    </property>
    <property name="text">
     <string>Сохранить события</string>
    </property>
   </widget>
   <widget class="QPushButton" name="loadEventsBtn">
    <property name="geometry">
     <rect>
      <x>660</x>
      <y>550</y>
      <width>190</width>
      <height>28</height>
     </rect>
    </property>
    <property name="text">
     <string>Загрузить события</string>
    </property>
   </widget>
   <widget class="QLabel" name="label">
    <property name="geometry">
     <rect>
      <x>880</x>
      <y>50</y>
      <width>411</width>
      <height>281</height>
     </rect>
    </property>
    <property name="text">
     <string>TextLabel</string>
    </property>
   </widget>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>1225</width>
     <height>26</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <resources/>
 <connections/>
</ui>
"""


class DiaryEvent:

    def __init__(self, datetime, title):
        self.datetime = datetime
        self.title = title

    def __str__(self):
        return f"{self.datetime.strftime('%Y-%m-%d %H:%M')} - {self.title}"


    def to_csv(self):
        return f"{self.datetime.isoformat()},{self.title}"


class SimplePlanner(QMainWindow):
    def __init__(self):
        super().__init__()
        f = io.StringIO(template)
        uic.loadUi(f, self)
        self.events = []
        self.create_database()
        self.load_events_from_db()
        self.addEventBtn.clicked.connect(self.add_event)
        self.editEventBtn.clicked.connect(self.edit_event)
        self.deleteEventBtn.clicked.connect(self.delete_event)
        self.saveEventsBtn.clicked.connect(self.save_events_to_db)
        self.loadEventsBtn.clicked.connect(self.load_events_from_db)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.label = QLabel(self)
        self.layout.addWidget(self.label)

        self.load_image_by_month()

    def load_image_by_month(self):
        month = datetime.datetime.now().month
        image_path = self.get_image_path(month)

        pixmap = QPixmap(image_path)
        self.label.setPixmap(pixmap)
        self.label.setFixedSize(pixmap.size())

    def get_image_path(self):
        images = {
            1: 'winter.jpg',
            2: 'winter.jpg',
            3: 'spring.jpg',
            4: 'spring.jpg',
            5: 'spring.jpg',
            6: 'summer.jpg',
            7: 'summer.jpg',
            8: 'summer.jpg',
            9: 'autumn.jpg',
            10: 'autumn.jpg',
            11: 'autumn.jpg',
            12: 'winter.jpg',
        }
        return images.get(month, 'images')

    def create_database(self):
        self.conn = sqlite3.connect('events.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                datetime TEXT NOT NULL,
                title TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def add_event(self):
        if self.lineEdit.text():
            t = datetime.datetime(
                self.calendarWidget.selectedDate().year(),
                self.calendarWidget.selectedDate().month(),
                self.calendarWidget.selectedDate().day(),
                self.timeEdit.time().hour(),
                self.timeEdit.time().minute()
            )
            event = DiaryEvent(t, self.lineEdit.text())
            self.events.append(event)
            self.insert_event_to_db(event)
            self.events.sort(key=lambda x: x.datetime)
            self.update_event_list()
            self.lineEdit.clear()

    def insert_event_to_db(self, event):
        self.cursor.execute('INSERT INTO events (datetime, title) VALUES (?, ?)',
                            (event.datetime.isoformat(), event.title))
        self.conn.commit()

    def edit_event(self):
        selected_item = self.eventList.currentItem()
        if selected_item:
            index = self.eventList.row(selected_item)
            current_event = self.events[index]

            new_title, ok = QInputDialog.getText(self, "Редактировать событие",
                                                 "Измените название события:",
                                                 text=current_event.title)
            if ok and new_title:
                selected_date = self.calendarWidget.selectedDate()
                selected_time = self.timeEdit.time()
                t = datetime.datetime(
                    selected_date.year(),
                    selected_date.month(),
                    selected_date.day(),
                    selected_time.hour(),
                    selected_time.minute()
                )

                current_event.title = new_title
                current_event.datetime = t

                self.update_event_list()
                self.update_event_in_db(current_event)
                print('Событие обновлено')

    def update_event_in_db(self, event):
        try:
            self.cursor.execute('UPDATE events SET datetime = ?, title = ? WHERE id = ?',
                                (event.datetime.isoformat(), event.title, event.id))
            self.conn.commit()
        except Exception as e:
            print("Ошибка обновления события в базе данных:", e)

    def delete_event(self):
        selected_item = self.eventList.currentItem()
        if selected_item:
            index = self.eventList.row(selected_item)
            event_to_delete = self.events[index]
            self.delete_event_from_db(event_to_delete)
            del self.events[index]
            self.update_event_list()

    def delete_event_from_db(self, event):
        self.cursor.execute('DELETE FROM events WHERE datetime = ? AND title = ?',
                            (event.datetime.isoformat(), event.title))
        self.conn.commit()

    def load_events_from_db(self):
        self.events.clear()
        self.cursor.execute('SELECT datetime, title FROM events')
        for row in self.cursor.fetchall():
            event_datetime, title = row
            event = DiaryEvent(datetime.datetime.fromisoformat(event_datetime), title)
            self.events.append(event)
        self.events.sort(key=lambda x: x.datetime)
        self.update_event_list()

    def save_events_to_db(self):
        self.cursor.execute('DELETE FROM events')
        for event in self.events:
            self.insert_event_to_db(event)
        QMessageBox.information(self, "Успех", "События успешно сохранены в базу данных.")

    def update_event_list(self):
        self.eventList.clear()
        self.eventList.addItems([str(event) for event in self.events])

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SimplePlanner()
    ex.show()
    sys.exit(app.exec())
