from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
import telepot
import time
from lib.def_library import *

class Reserve_Base():
    def __init__(self):
        self.bot = telepot.Bot(TELEGRAM_BOT_TOKEN)

    def login(self, user_id, user_pw):
        ...

    def departure(self, element):
        ...
    
    def arrival(self, ID):
        ...

    def request_time(self, ID):
        ...

    def search_ticket(self):
        ...

    def reserve_ticket(self):
        ...

class SRT(Reserve_Base):
    
    def login(self, user_id, user_pw):
        self.driver = webdriver.Firefox()
        self.driver.get("https://etk.srail.kr/cmc/01/selectLoginForm.do?pageId=TK0701000000")
        time.sleep(1)
        self.driver.find_element(By.ID, "srchDvCd3").click()
        self.driver.find_element(By.ID, "srchDvNm03").send_keys(user_id)
        self.driver.find_element(By.ID, "hmpgPwdCphd03").send_keys(user_pw)
        self.driver.find_elements(By.XPATH, "//input[@class='submit btn_pastel2 loginSubmit']")[-1].click()
        self.driver.implicitly_wait(5)

        # Base Class로 이전
        handle_list = self.driver.window_handles
        for popup in handle_list:
            if popup != handle_list[0]: 
                self.driver.switch_to.window(popup)
                self.driver.close()
        self.driver.implicitly_wait(5)

        # self.driver.find_element(By.ID, "gnb").click() # 승차권
        self.driver.get('https://etk.srail.kr/hpg/hra/01/selectScheduleList.do')
        
    def search(self, departure, arrival, req_datetime):
        # 출발
        _departure = self.driver.find_element(By.ID, "dptRsStnCdNm")
        _departure.clear(); _departure.send_keys(departure)
        # self.driver.implicitly_wait(5)

        # 도착
        _arrival = self.driver.find_element(By.ID, "arvRsStnCdNm")
        _arrival.clear(); _arrival.send_keys(arrival)#; _arrival.send_keys(Keys.RETURN)

        # 달력 Comp
        _yyyymmdd = "".join([req_datetime[idx] for idx in range(3)]) # yyyymmdd
        _req_date = Select(self.driver.find_element(By.XPATH, "//*[@id='dptDt']"))
        _req_date.select_by_value(_yyyymmdd)
        self.driver.implicitly_wait(5)

        _hh = f"{req_datetime[-1]:0<6}" 
        _req_time = Select(self.driver.find_element(By.XPATH, "//*[@id='dptTm']"))
        _req_time.select_by_value(_hh)
        self.driver.implicitly_wait(5)

        # 조회
        self.driver.find_element(By.XPATH, '//*[@id="search_top_tag"]/input').click()
        self.driver.implicitly_wait(5)

        search_result = self.driver.find_elements(By.CSS_SELECTOR, '#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr')

        result = ""
        for i in range(1, len(search_result)+1):
            result += str(i) + '. '
            for j in range(3, 6):
                result += self.driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child({j})").text.replace("\n"," ")
            result += '\n'

        self.bot.sendMessage(TELEGRAM_BOT_ID, result)
    
    def reservation(self, no):
        _seconds = 0
        while True:
            seat = self.driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({no}) > td:nth-child(7)").text
            if "예약하기" in seat:
                try:
                    self.driver.find_element(By.XPATH, f"//*[@id='result-form']/fieldset/div[6]/table/tbody/tr[{no}]/td[7]/a").click()
                except: #ElementClickInterceptedException:
                    self.bot.sendMessage(TELEGRAM_BOT_ID, "예약하기 Click 실패")
                    continue
                self.bot.sendMessage(TELEGRAM_BOT_ID, "예약이 완료됐습니다. 결제까지 꼭 완료해주세요")
                break
            else:
                time.sleep(3)
                _seconds += 3
                if (_seconds % 360) == 0: self.bot.sendMessage(TELEGRAM_BOT_ID, f"{_seconds//60}분 경과")
                submit = self.driver.find_element(By.XPATH, "//input[@value='조회하기']")
                self.driver.execute_script("arguments[0].click();", submit)


class KTX_Korail():
    def __init__(self):
        super().__init__()

    def login(self):
        self.driver = webdriver.Firefox()
        self.driver.get("https://www.letskorail.com/korail/com/login.do")
        time.sleep(1)
        self.driver.find_element(By.ID, "radInputFlg2").click()
        self.driver.find_element(By.ID, "txtCpNo2").send_keys("9678")
        self.driver.find_element(By.ID, "txtCpNo3").send_keys("4511")
        self.driver.find_element(By.ID, "txtPwd1").send_keys("Wlsqhtkd0!")
        # 여기서 XPATH 경로에 id 값을 큰따옴표로 묶었기 때문에 해당 XPATH 경로는 작은따옴표로 묶는다.
        self.driver.find_element(By.XPATH, '//*[@id="loginDisplay2"]/ul/li[3]/a/img').click()
        self.driver.find_element(By.CSS_SELECTOR, "#header > div.lnb > div.lnb_m01 > h3 > a > img").click()

        main = self.driver.window_handles
        for popup in main:
            if popup != main[0]: 
                self.driver.switch_to.window(popup)
                self.driver.close()

    #출발지 입력
    def korail_start_city(self, city):
        start_city = self.driver.find_element(By.ID,"start")
        start_city.clear()
        start_city.send_keys(city)
        start_city.send_keys(Keys.RETURN)

    #도착지 입력
    def korail_arrival_city(self, city):
        arrival_city = self.driver.find_element(By.ID,"get")
        arrival_city.clear()
        arrival_city.send_keys(city)
        arrival_city.send_keys(Keys.RETURN)

    #년 선택
    def korail_year_select(self, year):
        year_select = Select(self.driver.find_element(By.ID,"s_year"))
        year_select.select_by_value(year)

    #월 선택
    def korail_month_select(self, month):
        month_select = Select(self.driver.find_element(By.ID,"s_month"))
        month_select.select_by_value(month)

    #일 선택
    def korail_day_select(self, day):
        day_select = Select(self.driver.find_element(By.ID,"s_day"))
        day_select.select_by_value(day)

    #시간 선택
    def korail_hour_select(self, hour):
        hour_select = Select(self.driver.find_element(By.ID,"s_hour"))
        hour_select.select_by_value(hour)

    def korail_search(self):
        self.driver.find_element(By.CSS_SELECTOR, "#center > form > div > p > a > img").click()
        time.sleep(3)
        ktx_list = []
        for index_seq in range(1, 11):
            try:
                ktx_list.append(str(index_seq))
                ktx_list.append(self.driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/div[1]/form[1]/div/div[4]/table[1]/tbody/tr[%s]/td[3]" % index_seq).text)
                ktx_list.append(self.driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/div[1]/form[1]/div/div[4]/table[1]/tbody/tr[%s]/td[4]" % index_seq).text)
                ktx_list.append(self.driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/div[1]/form[1]/div/div[4]/table[1]/tbody/tr[%s]/td[6]/a[1]/img" % index_seq).get_attribute("alt"))
                ktx_list.append("---------------")
            except:
                ktx_list.append("해당시간 이후의 기차표는 없습니다.")
        ktx_info = '\n'.join(ktx_list)
        
        token = "6191116773:AAEUFSQBz3AmscKg7005emJy2YCERdmrXCE"
        bot = telepot.Bot(token)
        bot.sendMessage('5889178609', ktx_info)

    def ticket_reservation(self, index_seq):        
        is_reserve = None
        token = "6191116773:AAEUFSQBz3AmscKg7005emJy2YCERdmrXCE"
        bot = telepot.Bot(token)
        bot.sendMessage('5889178609', '예약을 시작합니다.')
        while True:
            is_reserve = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/div[1]/form[1]/div/div[4]/table[1]/tbody/tr[%s]/td[6]//img" % index_seq).get_attribute("alt")
            if is_reserve == "예약하기":
                self.driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/div[1]/form[1]/div/div[4]/table[1]/tbody/tr[%s]/td[6]/a[1]/img" % index_seq).click()
                time.sleep(2)
                try:
                    sancheon_popup_iframe = self.driver.find_element(By.ID, "embeded-modal-traininfo")
                    self.driver.switch_to.frame(sancheon_popup_iframe)
                    self.driver.find_element(By.XPATH, "/html/body/div/div[2]/p[3]/a").click()
                    time.sleep(2)
                finally:
                    alert = self.driver.switch_to.alert
                    alert.accept()
                    token = "6191116773:AAEUFSQBz3AmscKg7005emJy2YCERdmrXCE"
                    bot = telepot.Bot(token)
                    bot.sendMessage('5889178609', '예약완료')
                    time.sleep(1)
            else:
                self.driver.find_element(By.CSS_SELECTOR, ".btn_inq > a:nth-child(1) > img:nth-child(1)").click()
                time.sleep(2)