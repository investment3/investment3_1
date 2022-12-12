import os
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *

from kiwoom import Kiwoom
from Qthread_1 import Thread1
from Qthread_2 import Thread2
from Qthread_3 import Thread3


form_class = uic.loadUiType("ALBA.ui")[0]

class Login_Machnine(QMainWindow, QWidget, form_class):       # QMainWindow : PyQt5에서 윈도우 생성시 필요한 함수

    def __init__(self, *args, **kwargs):

        print("Login Machine 실행합니다.")
        super(Login_Machnine, self).__init__(*args, **kwargs)
        form_class.__init__(self)
        self.setUI()

        ### 초기 셋팅 : 계좌평가잔고내역
        self.label_11.setText(str("총매입금액"))
        self.label_12.setText(str("총평가금액"))
        self.label_13.setText(str("추정예탁자산"))
        self.label_14.setText(str("총평가손익금액"))
        self.label_15.setText(str("총수익률(%)"))

        self.searchItemTextEdit2.setAlignment(Qt.AlignRight)


        self.buy_price.setAlignment(Qt.AlignRight)
        # self.buy_price.setDecimals(0)
        self.n_o_stock.setAlignment(Qt.AlignRight)
        # self.n_o_stock.setDecimals(0)
        self.profit_price.setAlignment(Qt.AlignRight)
        # self.profit_price.setDecimals(0)
        self.loss_price.setAlignment(Qt.AlignRight)
        # self.loss_price.setDecimals(0)



        self.login_event_loop = QEventLoop()  # 이때 QEventLoop()는 block 기능을 가지고 있다.

        ####키움증권 로그인 하기
        self.k = Kiwoom()
        self.set_signal_slot()
        self.signal_login_commConnect()

        self.call_account.clicked.connect(self.c_acc)         # 계좌정보가져오기
        self.acc_manage.clicked.connect(self.a_manage)        # 계좌관리하기
        self.Auto_start.clicked.connect(self.auto)            # 자동매매 시작


        ################# 부가기능 1 : 종목선택하기 새로운 종목 추가 및 삭제
        self.k.kiwoom.OnReceiveTrData.connect(self.trdata_slot)
        self.additmelast.clicked.connect(self.searchItem2)
        self.Deletcode.clicked.connect(self.deltecode)


        ################# 부가기능 2 : 데이터베이스화 하기, 저장, 삭제, 불러오기
        self.Getanal_code = []
        self.Save_Stock.clicked.connect(self.Save_selected_code)               # 종목 저장
        self.Del_Stock.clicked.connect(self.delet_code)                        # 종목 삭제
        self.Load_Stock.clicked.connect(self.Load_code)                        # 종목 불러오기

    def Load_code(self):

        if os.path.exists("dist/Selected_code.txt"):
            f = open("dist/Selected_code.txt", "r", encoding="utf8")
            lines = f.readlines()  # 여러 종목이 저장되어 있다면 모든 항목을 가져온다.
            for line in lines:
                if line != "":                     # 만약에 line이 비어 있지 않다면
                    ls = line.split("\t")          # \t(tap)로 구분을 지어 놓는다.
                    t_code = ls[0]
                    t_name = ls[1]
                    curren_price = ls[2]
                    dept = ls[3]
                    mesu = ls[4]
                    n_o_stock = ls[5]
                    profit = ls[6]
                    loss = ls[7].split("\n")[0]
                    self.Getanal_code.append([t_code, t_name, curren_price, dept, mesu, n_o_stock, profit, loss])
            f.close()

        column_head = ["종목코드", "종목명", "현재가", "신용비율", "매수가", "매수수량", "익절가", "손절가"]
        colCount = len(column_head)
        rowCount = len(self.Getanal_code)
        self.buylast.setColumnCount(colCount)
        self.buylast.setRowCount(rowCount)
        self.buylast.setHorizontalHeaderLabels(column_head)
        self.buylast.setSelectionMode(QAbstractItemView.SingleSelection)

        for index in range(rowCount):
            self.buylast.setItem(index, 0, QTableWidgetItem(str(self.Getanal_code[index][0])))
            self.buylast.setItem(index, 1, QTableWidgetItem(str(self.Getanal_code[index][1])))
            self.buylast.setItem(index, 2, QTableWidgetItem(str(self.Getanal_code[index][2])))
            self.buylast.setItem(index, 3, QTableWidgetItem(str(self.Getanal_code[index][3])))
            self.buylast.setItem(index, 4, QTableWidgetItem(str(self.Getanal_code[index][4])))
            self.buylast.setItem(index, 5, QTableWidgetItem(str(self.Getanal_code[index][5])))
            self.buylast.setItem(index, 6, QTableWidgetItem(str(self.Getanal_code[index][6])))
            self.buylast.setItem(index, 7, QTableWidgetItem(str(self.Getanal_code[index][7])))



    def Save_selected_code(self):

        for row in range(self.buylast.rowCount()):

            code_n = self.buylast.item(row, 0).text()
            name = self.buylast.item(row, 1).text().strip()
            price = self.buylast.item(row, 2).text()
            dept = self.buylast.item(row, 3).text()
            mesu = self.buylast.item(row, 4).text()
            n_o_stock = self.buylast.item(row, 5).text()
            profit = self.buylast.item(row, 6).text()
            loss = self.buylast.item(row, 7).text()

            f = open("dist/Selected_code.txt", "a",encoding="utf8")
            f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (code_n, name, price, dept, mesu, n_o_stock, profit, loss))
            f.close()

    def delet_code(self):

        if os.path.exists("dist/Selected_code.txt"):
            os.remove("dist/Selected_code.txt")

    def deltecode(self):
        x = self.buylast.selectedIndexes()
        self.buylast.removeRow(x[0].row())


    def searchItem2(self):
        itemName = self.searchItemTextEdit2.toPlainText()
        if itemName != "":
            for code in self.k.All_Stock_Code.keys():
                if itemName == self.k.All_Stock_Code[code]['종목명']:
                    self.new_code = code


        column_head = ["종목코드", "종목명", "현재가", "신용비율", "매수 가격", "매수 수량", "익절 가격", "손절 가격"]
        colCount = len(column_head)
        row_count = self.buylast.rowCount()

        self.buylast.setColumnCount(colCount)
        self.buylast.setRowCount(row_count+1)
        self.buylast.setHorizontalHeaderLabels(column_head)

        self.buylast.setItem(row_count, 0, QTableWidgetItem(str(self.new_code)))
        self.buylast.setItem(row_count, 1, QTableWidgetItem(str(itemName)))
        self.buylast.setItem(row_count, 4, QTableWidgetItem(str(int(self.buy_price.value()))))
        self.buylast.setItem(row_count, 5, QTableWidgetItem(str(int(self.n_o_stock.value()))))
        self.buylast.setItem(row_count, 6, QTableWidgetItem(str(int(self.profit_price.value()))))
        self.buylast.setItem(row_count, 7, QTableWidgetItem(str(int(self.loss_price.value()))))


        self.getItemInfo(self.new_code)



    def getItemInfo(self, new_code):
        self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", new_code)
        self.k.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "주식기본정보요청", "opt10001", 0, "100")

    def setUI(self):
        self.setupUi(self)

    def set_signal_slot(self):
        self.k.kiwoom.OnEventConnect.connect(self.login_slot)

    def signal_login_commConnect(self):
        self.k.kiwoom.dynamicCall("CommConnect()")
        self.login_event_loop.exec_()

    def login_slot(self, errCode):
        if errCode == 0:
            print("로그인 성공")
            self.statusbar.showMessage("로그인 성공")
            self.get_account_info()

        elif errCode == 100:
            print("사용자 정보교환 실패")
        elif errCode == 101:
            print("서버접속 실패")
        elif errCode == 102:
            print("버전처리 실패")
        self.login_event_loop.exit()

    def get_account_info(self):
        account_list = self.k.kiwoom.dynamicCall("GetLoginInfo(String)", "ACCNO")

        for n in account_list.split(';'):
            self.accComboBox.addItem(n)

    def c_acc(self):
        print("선택 계좌 정보 가져오기")
        h1 = Thread1(self)
        h1.start()

    def a_manage(self):
        print("계좌 관리")
        h2 = Thread2(self)
        h2.start()


    def auto(self):
        print("자동매매 시작")
        h3 = Thread3(self)
        h3.start()



    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):

        if sTrCode == "opt10001":
            if sRQName == "주식기본정보요청":
                currentPrice = abs(int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "현재가")))
                D_R = (self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "신용비율")).strip()
                row_count = self.buylast.rowCount()
                self.buylast.setItem(row_count - 1, 2, QTableWidgetItem(str(currentPrice)))
                self.buylast.setItem(row_count - 1, 3, QTableWidgetItem(str(D_R)))



if __name__=='__main__':


    app = QApplication(sys.argv)
    CH = Login_Machnine()
    CH.show()
    app.exec_()