'''import os                                   # 현재 디렉토리 확인 기능
from PyQt5.QtCore import *                  # 쓰레드 함수를 불러온다.
from kiwoom import Kiwoom                   # 로그인을 위한 클래스
from kiwoomType import *


class Thread3(QThread):
    def __init__(self, parent):   # 부모의 윈도우 창을 가져올 수 있다.
        super().__init__(parent)  # 부모의 윈도우 창을 초기화 한다.
        self.parent = parent      # 부모의 윈도우를 사용하기 위한 조건

        ################## 키움서버 함수를 사용하기 위해서 kiwoom의 능력을 상속 받는다.
        self.k = Kiwoom()
        ##################

        ################## 사용되는 변수
        account = self.parent.accComboBox.currentText()  # 콤보박스 안에서 가져오는 부분
        self.account_num = account
        # 계좌번호 가져오는 부분은 Qthread_3 분리 시 로그인 후 계좌번호를 가져오는 함수로 교체된다. Lecture_0529.py'''
import os                                   # 현재 디렉토리 확인 기능
from PyQt5.QtCore import *                  # 쓰레드 함수를 불러온다.
from kiwoom import Kiwoom                   # 로그인을 위한 클래스
#from kiwoomType import *
import KiwoomType

class Thread3(QThread):
    def __init__(self, parent):   # 부모의 윈도우 창을 가져올 수 있다.
        super().__init__(parent)  # 부모의 윈도우 창을 초기화 한다.
        self.parent = parent      # 부모의 윈도우를 사용하기 위한 조건

        ################## 키움서버 함수를 사용하기 위해서 kiwoom의 능력을 상속 받는다.
        self.k = Kiwoom()
        ##################

        ################## 사용되는 변수
        account = self.parent.accComboBox.currentText()  # 콤보박스 안에서 가져오는 부분
        self.account_num = account
        # 계좌번호 가져오는 부분은 Qthread_3 분리 시 로그인 후 계좌번호를 가져오는 함수로 교체된다. Lecture_0529.py

        ################# 매수관련 변수
        self.Load_code()         # 매수 종목/금액/수량 가져오기
        self.orderitmelist_1 = []  # 중복 매수 금지
        self.orderitmelist_2 = []  # 중복 익절 금지
        self.orderitmelist_3 = []  # 중복 손절 금지

        ####### 주문 전송 시 필요한 FID 번호
        self.realType = KiwoomType.RealType()  # 실시간 FID 번호를 모아두는 곳, 원래 코드는 self.realType = RealType()

        ######################################################################
        ###### 등록된 계좌 전체 해제하기(작동 정지 되었을 때 등록 정보를 다 끊어야 한다.)
        self.k.kiwoom.dynamicCall("SetRealRemove(QString, QString)", ["ALL", "ALL"])
        ######################################################################

        ######################################################################
        ###### 선정된 종목 등록하기 : 키움서버에 리얼 데이터 등록하기

        self.screen_num = 5000

        for code in self.k.portfolio_stock_dict.keys():  # 포트폴리오에 저장된 코드들을 실시간 등록
            fids = self.realType.REALTYPE['주식체결']['체결시간']  # 주식체결에 대한 모든 데이터를 로드할 수 있다.
            self.k.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_num, code, fids,
                                      "1")  # 실시간 데이터를 받아오기 위해 각 코드들을 서버에 등록(틱 변화가 있으면 데이터 송신)
            self.screen_num += 1

            # print("실시간 등록 : %s, 스크린번호 : %s, FID  번호 : %s" % (code, screen_num, fids))
        print("종목등록 완료")
        print(self.k.portfolio_stock_dict.keys())

        ######################################################################
        ###### 현재 장 상태 알아보기 (장 시작 / 장 마감 등)
        self.screen_start_stop_real = "300"  # 장시 시작 전/후 상태 확인용 스크린 번호
        self.k.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '',
                                  self.realType.REALTYPE['장시작시간']['장운영구분'], "0")  # 장의 시작인지, 장 외인지등에 대한 정보 수신

        ###### 실시간 슬롯 (데이터를 받아오는 슬롯을 설정한다)
        self.k.kiwoom.OnReceiveRealData.connect(self.realdata_slot)  # 실시간 데이터를 받아오는 곳


    def Load_code(self):

        if os.path.exists("dist/Selected_code.txt"):
            f = open("dist/Selected_code.txt", "r", encoding="utf8")
            lines = f.readlines()  # 여러 종목이 저장되어 있다면 모든 항목을 가져온다.
            screen = 4000
            for line in lines:
                if line != "":                     # 만약에 line이 비어 있지 않다면
                    ls = line.split("\t")  # \t(tap)로 구분을 지어 놓는다.
                    t_code = ls[0]
                    t_name = ls[1]
                    curren_price = ls[2]
                    dept = ls[3]
                    mesu = ls[4]
                    n_o_stock = ls[5]
                    profit = ls[6]
                    loss = ls[7].split("\n")[0]

                    self.k.portfolio_stock_dict.update({t_code: {"종목명": t_name}})
                    self.k.portfolio_stock_dict[t_code].update({"현재가": int(curren_price)})
                    self.k.portfolio_stock_dict[t_code].update({"신용비율": dept})
                    self.k.portfolio_stock_dict[t_code].update({"매수가": int(mesu)})
                    self.k.portfolio_stock_dict[t_code].update({"매수수량": int(n_o_stock)})
                    self.k.portfolio_stock_dict[t_code].update({"익절가": int(profit)})
                    self.k.portfolio_stock_dict[t_code].update({"손절가": int(loss)})
                    self.k.portfolio_stock_dict[t_code].update({"주문용스크린번호": screen})  # 아래 내용을 업데이트
                    screen += 1
            f.close()

    def realdata_slot(self, sCode, sRealType, sRealData):  # 실시간으로 서버에서 데이터들이 날라온다.

        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']

            # 실시간시세 데이터 수신 이벤트인 OnReceiveRealData() 가 발생될때 실시간데이터를 얻어오는 함수
            value = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid)

            if value == '0':
                print("장 시작 전")

            elif value == '3':
                print("장 시작")

            elif value == '2':
                print("장 종료, 동시호가로 넘어감감")

            elif value == '4':
                print("장 마감했습니다.")


        elif sRealType == "주식체결" and sCode in self.k.portfolio_stock_dict:

            fid1 = self.realType.REALTYPE[sRealType]['체결시간']  # 체결시간은 string으로 나온다. HHMMSS
            a = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid1)

            fid2 = self.realType.REALTYPE[sRealType]['현재가']  # 현재가는 +/-로 나온다.
            b = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid2)
            b = abs(int(b))

            fid3 = self.realType.REALTYPE[sRealType]['전일대비']  # 전달 대비 오르거나/내린 가격
            c = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid3)
            c = abs(int(c))

            fid4 = self.realType.REALTYPE[sRealType]['등락율']  # 전달 대비 오르거나/내린 퍼센테이지
            d = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid4)
            d = float(d)

            fid5 = self.realType.REALTYPE[sRealType]['(최우선)매도호가']  # 매도쪽에 첫번재 부분(시장가)
            e = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid5)
            e = abs(int(e))

            fid6 = self.realType.REALTYPE[sRealType]['(최우선)매수호가']  # 매수쪽에 첫번재 부분(시장가)
            f = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid6)
            f = abs(int(f))

            fid7 = self.realType.REALTYPE[sRealType]['거래량']  # 틱봉의 현재 거래량 (아주 작으 단위)
            g = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid7)
            g = abs(int(g))

            fid8 = self.realType.REALTYPE[sRealType]['누적거래량']
            h = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid8)
            h = abs(int(h))

            fid9 = self.realType.REALTYPE[sRealType]['고가']  # 오늘자 재일 높은 가격
            i = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid9)
            i = abs(int(i))

            fid10 = self.realType.REALTYPE[sRealType]['시가']  # 시가
            j = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid10)
            j = abs(int(j))

            fid11 = self.realType.REALTYPE[sRealType]['저가']  # 전체 재일 낮은 가격
            k = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid11)
            k = abs(int(k))

            fid12 = self.realType.REALTYPE[sRealType]['거래회전율']  # 누적 거래회전율
            l = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid12)
            l = abs(float(l))

            if sCode not in self.k.portfolio_stock_dict:  # 만약 서버에 등록된 코드가 포트폴리오에 없다면 코드를 등록
                self.k.portfolio_stock_dict.update({sCode: {}})

            # 포트폴리오 종목코드마다 아래 실시간 데이터를 입력
            self.k.portfolio_stock_dict[sCode].update({"채결시간": a})  # 아래 내용을 업데이트
            self.k.portfolio_stock_dict[sCode].update({"현재가": b})
            self.k.portfolio_stock_dict[sCode].update({"전일대비": c})
            self.k.portfolio_stock_dict[sCode].update({"등락율": d})
            self.k.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
            self.k.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
            self.k.portfolio_stock_dict[sCode].update({"거래량": g})
            self.k.portfolio_stock_dict[sCode].update({"누적거래량": h})
            self.k.portfolio_stock_dict[sCode].update({"고가": i})
            self.k.portfolio_stock_dict[sCode].update({"시가": j})
            self.k.portfolio_stock_dict[sCode].update({"저가": k})
            self.k.portfolio_stock_dict[sCode].update({"거래회전율": l})

            ###############################################################
            ############# 실시간을 위한 조건문 구성하기 ########################
            ###############################################################

            # 1. 매수 알고리즘 가동

            # 1차#############################################################################################
            if self.k.portfolio_stock_dict[sCode]["현재가"] <= self.k.portfolio_stock_dict[sCode]["매수가"]:
                if sCode not in self.orderitmelist_1:

                    wa = []
                    wa.append(sCode)

                    if len(wa) > 1:
                        wa.clear()
                        pass
                    else:
                        print("매수 시작 %s" % sCode)

                        self.orderitmelist_1.append(sCode)  # 이 기법을 더이상 사용하지 못하게 하기
                        order_success1 = self.k.kiwoom.dynamicCall(
                            "SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)",
                            ["신규매수", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1, sCode,
                             self.k.portfolio_stock_dict[sCode]["매수수량"], self.k.portfolio_stock_dict[sCode]["현재가"],
                             self.realType.SENDTYPE['거래구분']['지정가'], ""])

                        wf2 = open("dist/mesu_database.txt", "a",
                                   encoding="utf8")  # "a" 달아 쓴다. "w" 덮어 쓴다. files라느 파이썬 페키지 볼더를 만든다.
                        wf2.write("%s\t%s\t%s\t%s\n" % ("1매수정보", self.k.portfolio_stock_dict[sCode]["종목명"], b,
                                                        self.k.portfolio_stock_dict[sCode]["채결시간"]))  # t는 tap을 의미한다.
                        wf2.close()

                        if order_success1 == 0:
                            print("최우선매수호가로 주문 전달 성공")
                        else:
                            print("최우선매수호가로 주문 전달 실패")

                        # 2. 매도 알고리즘 가동

                        # 1차 익절 #############################################################################################
                        if self.k.portfolio_stock_dict[sCode]["현재가"] >= self.k.portfolio_stock_dict[sCode]["익절가"]:
                            if sCode not in self.orderitmelist_2:

                                wa = []
                                wa.append(sCode)

                                if len(wa) > 1:
                                    wa.clear()
                                    pass
                                else:
                                    print("익절 시작 %s" % sCode)

                                    self.orderitmelist_2.append(sCode)  # 이 기법을 더이상 사용하지 못하게 하기
                                    order_success2 = self.k.kiwoom.dynamicCall(
                                        "SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)",
                                        ["신규익절", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                         sCode,
                                         self.k.portfolio_stock_dict[sCode]["매수수량"],
                                         self.k.portfolio_stock_dict[sCode]["현재가"],
                                         self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    wf2 = open("dist/mesu_database.txt", "a",
                                               encoding="utf8")  # "a" 달아 쓴다. "w" 덮어 쓴다. files라느 파이썬 페키지 볼더를 만든다.
                                    wf2.write("%s\t%s\t%s\t%s\n" % (
                                    "1익절정보", self.k.portfolio_stock_dict[sCode]["종목명"], b,
                                    self.k.portfolio_stock_dict[sCode]["채결시간"]))  # t는 tap을 의미한다.
                                    wf2.close()

                                    if order_success2 == 0:
                                        print("익절가로 주문 전달 성공")
                                    else:
                                        print("익절가로 주문 전달 실패")

                        # 1차 손절 #############################################################################################
                        if self.k.portfolio_stock_dict[sCode]["현재가"] <= self.k.portfolio_stock_dict[sCode]["손절가"]:
                            if sCode not in self.orderitmelist_3:

                                wa = []
                                wa.append(sCode)

                                if len(wa) > 1:
                                    wa.clear()
                                    pass
                                else:
                                    print("손절 시작 %s" % sCode)

                                    self.orderitmelist_3.append(sCode)  # 이 기법을 더이상 사용하지 못하게 하기
                                    order_success3 = self.k.kiwoom.dynamicCall(
                                        "SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)",
                                        ["신규손절", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                         sCode,
                                         self.k.portfolio_stock_dict[sCode]["매수수량"],
                                         self.k.portfolio_stock_dict[sCode]["현재가"],
                                         self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                    wf2 = open("dist/mesu_database.txt", "a",
                                               encoding="utf8")  # "a" 달아 쓴다. "w" 덮어 쓴다. files라느 파이썬 페키지 볼더를 만든다.
                                    wf2.write("%s\t%s\t%s\t%s\n" % (
                                    "1손절정보", self.k.portfolio_stock_dict[sCode]["종목명"], b,
                                    self.k.portfolio_stock_dict[sCode]["채결시간"]))  # t는 tap을 의미한다.
                                    wf2.close()

                                    if order_success3 == 0:
                                        print("손절가로 주문 전달 성공")
                                    else:
                                        print("손절가로 주문 전달 실패")


                                    # 2. 매도 알고리즘 가동

                                    # 1차 익절 #############################################################################################
                                if self.k.portfolio_stock_dict[sCode]["현재가"] >= self.k.portfolio_stock_dict[sCode][
                                    "익절가"]:
                                    if sCode not in self.orderitmelist_2:

                                        wa = []
                                        wa.append(sCode)

                                        if len(wa) > 1:
                                            wa.clear()
                                            pass
                                        else:
                                            print("익절 시작 %s" % sCode)

                                            self.orderitmelist_2.append(sCode)  # 이 기법을 더이상 사용하지 못하게 하기
                                            order_success2 = self.k.kiwoom.dynamicCall(
                                                "SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)",
                                                ["신규익절", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'],
                                                 self.account_num, 2, sCode,
                                                 self.k.portfolio_stock_dict[sCode]["매수수량"],
                                                 self.k.portfolio_stock_dict[sCode]["현재가"],
                                                 self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                            wf2 = open("dist/mesu_database.txt", "a",
                                                       encoding="utf8")  # "a" 달아 쓴다. "w" 덮어 쓴다. files라느 파이썬 페키지 볼더를 만든다.
                                            wf2.write("%s\t%s\t%s\t%s\n" % (
                                            "1익절정보", self.k.portfolio_stock_dict[sCode]["종목명"], b,
                                            self.k.portfolio_stock_dict[sCode]["채결시간"]))  # t는 tap을 의미한다.
                                            wf2.close()

                                            if order_success2 == 0:
                                                print("익절가로 주문 전달 성공")
                                            else:
                                                print("익절가로 주문 전달 실패")

                                    # 1차 손절 #############################################################################################
                                if self.k.portfolio_stock_dict[sCode]["현재가"] <= self.k.portfolio_stock_dict[sCode][
                                    "손절가"]:
                                    if sCode not in self.orderitmelist_3:

                                        wa = []
                                        wa.append(sCode)

                                        if len(wa) > 1:
                                            wa.clear()
                                            pass
                                        else:
                                            print("손절 시작 %s" % sCode)

                                            self.orderitmelist_3.append(sCode)  # 이 기법을 더이상 사용하지 못하게 하기
                                            order_success3 = self.k.kiwoom.dynamicCall(
                                                "SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)",
                                                ["신규손절", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'],
                                                 self.account_num, 2, sCode,
                                                 self.k.portfolio_stock_dict[sCode]["매수수량"],
                                                 self.k.portfolio_stock_dict[sCode]["현재가"],
                                                 self.realType.SENDTYPE['거래구분']['지정가'], ""])

                                            wf2 = open("dist/mesu_database.txt", "a",
                                                       encoding="utf8")  # "a" 달아 쓴다. "w" 덮어 쓴다. files라느 파이썬 페키지 볼더를 만든다.
                                            wf2.write("%s\t%s\t%s\t%s\n" % (
                                            "1손절정보", self.k.portfolio_stock_dict[sCode]["종목명"], b,
                                            self.k.portfolio_stock_dict[sCode]["채결시간"]))  # t는 tap을 의미한다.
                                            wf2.close()

                                            if order_success3 == 0:
                                                print("손절가로 주문 전달 성공")
                                            else:
                                                print("손절가로 주문 전달 실패")