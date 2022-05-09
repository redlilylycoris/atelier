import sys
import sqlite3
import csv

from PyQt5 import uic, QtGui
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QStackedWidget, QTreeWidgetItem, QTreeWidget


class Main(QMainWindow):  # главная
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.initUI()

    def initUI(self):
        self.mainBtnServices.clicked.connect(self.gotoServices)  # кнопка "услуги"
        self.mainBtnActive.clicked.connect(self.gotoActive)  # кнопка "активные заказы"

    def gotoServices(self):  # переход к услугам
        services = Services()
        widget.addWidget(services)
        widget.setCurrentWidget(services)

    def gotoActive(self):  # переход к активным заказам
        active = Active()
        widget.addWidget(active)
        widget.setCurrentWidget(active)


class Services(QDialog):  # усуги
    def __init__(self):
        super().__init__()
        uic.loadUi("services.ui", self)
        self.initUI()

    def initUI(self):
        self.srvcBtnMain.clicked.connect(self.gotoMain)  # кнопка "главная"
        self.srvcBtnActive.clicked.connect(self.gotoActive)  # кнопка "активные заказы"
        self.btnOrder.clicked.connect(self.showOrder)  # кнопка "оформить заказ"

        self.populate()

    def populate(self):
        with open('list_of_fix.csv', 'rt') as f:
            reader = csv.reader(f)
            for row in reader:
                item = QTreeWidgetItem(self.treeWidget_Services.topLevelItem(1), row)
        with open('list_of_todo.csv', 'rt') as f:
            reader = csv.reader(f)
            for row in reader:
                item = QTreeWidgetItem(self.treeWidget_Services.topLevelItem(0), row)


    def gotoMain(self):  # переход к главной
        main = Main()
        widget.addWidget(main)
        widget.setCurrentWidget(main)

    def gotoActive(self):  # переход к активным заказам
        active = Active()
        widget.addWidget(active)
        widget.setCurrentWidget(active)

    def showOrder(self):  # открытие диалога оформления заказа
        orderform = Order()
        orderform.exec()


class Active(QDialog):  # активные заказы
    def __init__(self):
        super().__init__()
        uic.loadUi("active.ui", self)
        self.initUI()

    def initUI(self):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('all.sqlite')
        db.open()

        self.model = QSqlTableModel(self, db)
        self.model.setTable('actives')
        self.model.select()
        self.tableActives.setModel(self.model)

        self.actBtnMain.clicked.connect(self.gotoMain)  # кнопка "главная"
        self.actBtnServices.clicked.connect(self.gotoServices)  # кнопка "услуги"
        self.btnMove.clicked.connect(self.showCD)  # кнопка "перенести"
        self.btnDelete.clicked.connect(self.showDel)  # кнопка "удалить"

    def gotoMain(self):  # переход к главной
        main = Main()
        widget.addWidget(main)
        widget.setCurrentWidget(main)

    def gotoServices(self):  # переход к услугам
        services = Services()
        widget.addWidget(services)
        widget.setCurrentWidget(services)

    def showCD(self):  # открытие диалога переноса заказа
        cd = ChangeDate()
        cd.exec()
        self.model.select()

    def showDel(self):  # открытие диалога удаления заказа
        dq = DeleteYN()
        dq.exec()
        self.model.select()


class ChangeDate(QDialog):  # перенос заказа
    def __init__(self):
        super().__init__()
        uic.loadUi("changedate.ui", self)
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QtGui.QIcon('atelier_icon.png'))
        self.setWindowTitle('Перенос заказа')

        self.lineNewDate.setText(None)
        self.lineReason.setText(None)
        self.lineRemID.setText('0')

        self.cdBtnCancel.clicked.connect(self.cdLeave)
        self.cdBtnOK.clicked.connect(self.cdWrite)

    def cdLeave(self):  # закрытие окна
        self.close()

    def cdWrite(self):  # изменение БД
        self.con = sqlite3.connect("all.sqlite")
        self.cur = self.con.cursor()
        self.remID = self.lineRemID.text()
        self.newDate = self.lineNewDate.text()
        self.deason = self.lineReason.text()
        self.cur.execute(f"UPDATE actives" + f" SET 'Дата прихода' = '{self.newDate}'"
                                            + f" WHERE id = '{self.remID}'").fetchall()
        self.con.commit()
        self.close()


class DeleteYN(QDialog):  # удаление заказа
    def __init__(self):
        super().__init__()
        uic.loadUi("delete.ui", self)
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QtGui.QIcon('atelier_icon.png'))
        self.setWindowTitle('Удаление заказа')

        self.delLineID.setText(None)

        self.delBtnNo.clicked.connect(self.delLeave)  # кнопка "нет"
        self.delBtnYes.clicked.connect(self.delWrite)  # кнопка "да"

    def delLeave(self):  # закрытие окна
        self.close()

    def delWrite(self):  # удаление из БД
        self.con = sqlite3.connect("all.sqlite")
        self.cur = self.con.cursor()
        self.delID = self.delLineID.text()
        self.cur.execute(f"DELETE from actives" + f" WHERE id = '{self.delID}'").fetchall()
        self.con.commit()
        self.close()


class Order(QDialog):  # оформление заказа
    def __init__(self):
        super().__init__()
        uic.loadUi("order.ui", self)
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QtGui.QIcon('atelier_icon.png'))
        self.setWindowTitle('Оформление заказа')

        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('all.sqlite')
        db.open()

        self.model = QSqlTableModel(self, db)  # таблица sql
        self.model.setTable('services')
        self.model.select()
        self.list_of_services.setModel(self.model)
        self.working()

    def working(self):
        self.lineService.setText(None)
        self.lineFIO.setText(None)
        self.lineSpine.setText(None)
        self.lineChest.setText(None)
        self.lineThing.setText(None)
        self.lineWaist.setText(None)
        self.lineNumber.setText(None)
        self.lineHip.setText(None)
        self.lineDate.setText(None)
        self.lineID.setText('0')

        self.ordBtnCancel.clicked.connect(self.ordLeave)  # кнопка "отмена"
        self.ordBtnOK.clicked.connect(self.ordWrite)  # кнопка "ок"

    def ordLeave(self):  # закрытие окна
        self.close()

    def ordWrite(self):  # запись в БД
        self.con = sqlite3.connect("all.sqlite")
        self.cur = self.con.cursor()
        self.services = self.lineService.text()
        self.fio = self.lineFIO.text()
        self.spine = self.lineSpine.text()
        self.chest = self.lineChest.text()
        self.thing = self.lineThing.text()
        self.waist = self.lineWaist.text()
        self.number = self.lineNumber.text()
        self.hip = self.lineHip.text()
        self.date = self.lineDate.text()
        self.id = self.lineID.text()
        q = f"'{self.id}', '{self.fio}', '{self.services}',"\
            f"'{self.chest}', '{self.waist}', '{self.hip}', '{self.thing}',"\
            f"'{self.spine}', '{self.date}', '{self.number}'"
        try:  # перехват ошибки
            self.cur.execute(f"INSERT INTO actives VALUES({q})").fetchall()
            self.con.commit()
            self.close()
        except BaseException:
            e = Error()
            e.exec()



class Error(QDialog):  # ошибка
    def __init__(self):
        super().__init__()
        uic.loadUi("error.ui", self)
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QtGui.QIcon('atelier_icon.png'))
        self.setWindowTitle('Ошибка')
        self.erBtnOK.clicked.connect(self.leave)

    def leave(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QStackedWidget()  # многооконность
    widget.setFixedWidth(761)
    widget.setFixedHeight(578)
    main = Main()  # главное окно
    widget.addWidget(main)
    widget.setWindowTitle('Ателье')  # название окна
    widget.setWindowIcon(QtGui.QIcon('atelier_icon.png'))  # иконка окна
    widget.show()
    sys.exit(app.exec_())
