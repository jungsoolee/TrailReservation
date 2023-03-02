import telepot
from ticket.trail import *
from lib.def_library import *
import re

class Ticket_Telegram():
    def __init__(self):
        print('Start Telegram Bot.')
        self.bot = telepot.Bot(TELEGRAM_BOT_TOKEN)
        self.bot.sendMessage(TELEGRAM_BOT_ID, "SRT(S)와 KTX(K)중 원하는 기차를 알려주세요.")
        self.bot.message_loop(self.receive_msg)
        while True:
            pass

    def receive_msg(self, msg, result=None):
        _receive_msg = msg['text']

        # 열차선택
        if _receive_msg == 'S': 
            self.ticket = SRT()
            self.bot.sendMessage(TELEGRAM_BOT_ID, "@id를 입력해주세요. (Ex: @id abcd)")
            ## test
            # self.bot.sendMessage(TELEGRAM_BOT_ID, "로그인 중입니다.")
            # self.ticket.login("010-9678-4511", "Wlsqhtkd0!")
            # self.ticket.search('오송', '수서', '2023/03/02/14'.split('/'))
            # self.ticket.reservation('3')
            ##
        elif _receive_msg == 'K': 
            self.ticket = KTX_Korail()
            self.bot.sendMessage(TELEGRAM_BOT_ID, "@id를 입력해주세요. (Ex: @id abcd)")
        elif "@id" in _receive_msg:
            if "#pass" in _receive_msg:
                self.bot.sendMessage(TELEGRAM_BOT_ID, "로그인 중입니다.")
                self.ticket.login("010-9678-4511", "Wlsqhtkd0!")
                self.bot.sendMessage(TELEGRAM_BOT_ID, "로그인 완료!")
                self.bot.sendMessage(TELEGRAM_BOT_ID, "@출발을 입력해주세요. (ex. @출발 abcd")
            else:
                self._user_id = _receive_msg.split(" ")[1]
                self.bot.sendMessage(TELEGRAM_BOT_ID, "@pw를 입력해주세요. (Ex. @pw abcd)")
        elif "@pw" in _receive_msg:
            self._user_pw = _receive_msg.split(" ")[1]
            self.bot.sendMessage(TELEGRAM_BOT_ID, "로그인 중입니다.")
            self.ticket.login(self._user_id, self._user_pw)
            self.bot.sendMessage(TELEGRAM_BOT_ID, "로그인 완료!")
            self.bot.sendMessage(TELEGRAM_BOT_ID, "@출발을 입력해주세요. (ex. @출발 abcd")
        elif "@출발" in _receive_msg:
            self._departure = _receive_msg.split(" ")[1]
            self.bot.sendMessage(TELEGRAM_BOT_ID, "@도착을 입력해주세요. (Ex. @도착 abcd")
        elif "@도착" in _receive_msg:
            self._arrival = _receive_msg.split(" ")[1]
            self.bot.sendMessage(TELEGRAM_BOT_ID, "@시간을 입력해주세요. (Ex. @시간 YYYY/MM/DD/HH")
        elif "@시간" in _receive_msg:
            #[0] = YYYY / [1] = mm / [2] = dd / [3] = HH 
            self._req_datetime = _receive_msg.split(" ")[1].split("/")
            self.bot.sendMessage(TELEGRAM_BOT_ID, "시간표 검색을 시작합니다.")
            self.ticket.search(self._departure, self._arrival, self._req_datetime)
        elif "@예약" in _receive_msg:
            _seq = _receive_msg.split(" ")[1].split("/").pop()
            self.ticket.reservation(_seq)

class KTX_Telegram():
    def __init__(self):
        print('텔레그램 시작합니다.')
        self.token = "6191116773:AAEUFSQBz3AmscKg7005emJy2YCERdmrXCE"
        self.bot = telepot.Bot(self.token)
        #아래 KTX_Korail()은 kor/korail.py 파일의 class명이다. 다음단계에서 생성할 예정이므로 주석처리한다.
        self.korail = KTX_Korail()
        self.bot.message_loop(self.conversation_telegram)
        while True:
            pass

    def conversation_telegram(self, msg, result = None):
        con_text = msg['text']
        chat_id = msg['chat']['id']
        if con_text == '로그인':
            self.bot.sendMessage(chat_id, "로그인중입니다. 잠시만 기다려주세요")
            self.korail.login()
            self.bot.sendMessage(chat_id, "로그인 완료")
        #윗 내용은 이미 전편에서 설정한 내용(추가할 내용의 위치가 헷갈리지 않게 넣어놨어요)

        start_city = re.compile("출발*")
        start_city_find = re.compile("[^출발]") 

        #목적지 설정을 위한 정규표현식
        arrival_city = re.compile("도착*")
        arrival_city_find = re.compile("[^도착]")

        #년을 선택하기 위한 정규표현식
        year_select = re.compile("202\d{1}년")
        year_select_find = re.compile("[^년]")

        #월을 선택하기 위한 정규표현식
        month_select = re.compile("[0-9]+월")
        month_select_find = re.compile("[^월]")

        #일을 선택하기 위한 정규표현식
        day_select = re.compile("[0-9]+일")
        day_select_find = re.compile("[^일]")

        #시간을 선택하기 위한 정규표현식
        hour_select = re.compile("[0-9]+시")
        hour_select_find = re.compile("[^시]")

        if start_city.match(con_text):
            start_city_name = start_city_find.findall(con_text)
            start_city_name = ''.join(start_city_name)
            self.korail.korail_start_city(start_city_name)

        if arrival_city.match(con_text):
            arrival_city_name = arrival_city_find.findall(con_text)
            arrival_city_name = ''.join(arrival_city_name)
            self.korail.korail_arrival_city(arrival_city_name)

        if year_select.match(con_text):
            year_select_name = year_select_find.findall(con_text)
            year_select_name = ''.join(year_select_name)
            self.korail.korail_year_select(year_select_name)

        if month_select.match(con_text):
            month_select_name = month_select_find.findall(con_text)
            month_select_name = ''.join(month_select_name)
            self.korail.korail_month_select(month_select_name)

        if day_select.match(con_text):
            day_select_name = day_select_find.findall(con_text)
            day_select_name = ''.join(day_select_name)
            self.korail.korail_day_select(day_select_name)

        if hour_select.match(con_text):
            hour_select_name = hour_select_find.findall(con_text)
            hour_select_name = ''.join(hour_select_name)
            self.korail.korail_hour_select(hour_select_name)

        if con_text == "검색":
            self.korail.korail_search()

        if con_text == "결과":
            self.token = "6191116773:AAEUFSQBz3AmscKg7005emJy2YCERdmrXCE"
            self.bot = telepot.Bot(self.token)
            self.bot.sendMessage(chat_id, result)

        #예약하기
        ticket_reservation = re.compile("예약[0-9]")
        ticket_reservation_find = re.compile("[^예약]")

        if ticket_reservation.match(con_text):
            index_seq = ticket_reservation_find.findall(con_text)
            index_seq = ''.join(index_seq)
            self.korail.ticket_reservation(index_seq)