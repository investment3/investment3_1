from PyQt5.QtWidgets import *                 # GUI의 그래픽적 요소를 제어       하단의 terminal 선택, activate py37_32,  pip install pyqt5,   전부다 y
from PyQt5.QAxContainer import *              # 키움증권의 클레스를 사용할 수 있게 한다.(QAxWidget)
from PyQt5Singleton import Singleton

class Kiwoom(QWidget, metaclass=Singleton):       # QMainWindow : PyQt5에서 윈도우 생성시 필요한 함수

    def __init__(self, parent=None, **kwargs):                    # Main class의 self를 초기화 한다.

        print("로그인 프로그램을 실행합니다.")

        super().__init__(parent, **kwargs)

        ################ 로그인 관련 정보

        self.kiwoom = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')       # CLSID

        ################# 전체 공유 데이터
        self.All_Stock_Code = {}            # 코스피, 코스닥 전체 코드넘버 입력
        self.acc_portfolio = {}             # 계좌에 들어있는 종목의 코드, 수익률 등등 입력
        self.portfolio_stock_dict = {}      # 매매에 관한 모든 종목(현재계좌 종ㅁ고/금일 등록종목)등이 들어간다.

        self.today_meme = []
        self.not_account_stock_dict = {}

        self.jango_dict = {}
        self.buy_jogon = {}                 #미체결 잔고
