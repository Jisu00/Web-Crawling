from selenium import webdriver # 모듈 불러오기
from selenium.webdriver.common.alert import Alert

from bs4 import BeautifulSoup as bs # html 파싱을 위해
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

#chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--incognito") # 시크릿 모드 관련

driver = webdriver.Chrome('D:/chromedriver')
#, chrome_options=chrome_options # 시크릿 모드 관련
driver.implicitly_wait(3)
url = 'https://portal.sejong.ac.kr/jsp/login/loginSSL.jsp?rtUrl=blackboard.sejong.ac.kr'
driver.get(url)

# 로그인

driver.find_element_by_name('chkNos').click()
da = Alert(driver) # 알림 창 제어
da.accept()
driver.find_element_by_name('id').send_keys('ID') # id 입력하기
driver.find_element_by_name('password').send_keys('PW') # pw 입력하기
driver.find_element_by_xpath('//*[@id="loginBtn"]').click() # 로그인 버튼 클릭

# 코스 과목 가져오기

try: # load 될 때까지 기다리기
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "course-org-list")))
finally:
    pass

body = driver.find_element_by_css_selector('body')
body.click()

for i in range(8):
    body.send_keys(Keys.PAGE_DOWN)
    
time.sleep(2)

course_list_raw = driver.find_elements_by_class_name("course-element-card")
course_list = []
course_detail_base = "https://blackboard.sejong.ac.kr/webapps/blackboard/execute/announcement?method=search&context=course_entry&course_id="
course_detail_list = []

for i in course_list_raw:
    course_each_id = str(i.get_attribute("data-course-id"))
    course_list.append(course_each_id)
    course_each_url = course_detail_base + course_each_id + "&handle=announcements_entry&mode=view";
    course_detail_list.append([course_each_url])
print(course_detail_list)



# 각 과목별 공지 / 과제 페이지 가져오기 - bs4, beautifulSoup 사용

# 공지는 과목 url과 동일

for i in course_detail_list:
    driver.get(i[0])
    try:
        # Page Load 기다리기
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "courseMenuPalette_contents")))

        # 공지 가져오기
        announce_raw = driver.page_source
        soup = bs(announce_raw, 'html.parser')
        announcements = soup.select('li.clearfix')[10:]
        announcements.reverse()
        
        for ann in announcements:
            print(ann.attrs['id'])
            print(ann.text)
            print('---------------')

        # 과제란이 있으면 가져오기, 없으면 에러 발생
        homework_html = driver.find_element_by_xpath('//*[@id="courseMenuPalette_contents"]').get_attribute('innerHTML')
        soup = bs(homework_html, 'html.parser')
        nav_bars = soup.find_all('a')
        for bar in nav_bars:
            if str(bar.find('span').text) == '과제' or str(bar.find('span').text) == 'Assignments':
                homework_url = 'https://blackboard.sejong.ac.kr' + str(bar['href'])
                i.append(homework_url)
                driver.get(homework_url)
                homework_raw = driver.page_source
                soup = bs(homework_raw, 'html.parser')
                homeworks = soup.select('ul.contentList > li')
                
                for home in homeworks:
                    print(home.attrs['id'])
                    print(home.text)
                    print('---------------')

    except Exception as e:
        homework_html = None
        print(e)
        pass


while(True):
    pass