# Web-Crawling
Python 패키지인 `Selenium`을 이용한 '세종대학교 블랙보드' 크롤링

- [참고 링크](https://taebbong.github.io/categories/%EA%B0%9C%EB%B0%9C/Web-Scraping-Crawling/)
- [Selenium 사용법](https://greeksharifa.github.io/references/2020/10/30/python-selenium-usage/)

<br/>

## Selenium 기반 크롤링 엔진 제작
> 1. [페이지 불러오기](#1-페이지-불러오기)
> 2. [블랙보드 로그인](#2-블랙보드-로그인)
> 3. [코스 과목 가져오기](#3-코스-과목-가져오기)
> 4. [각 과목별 공지 / 과제 페이지 가져오기](#4-각-과목별-공지--과제-페이지-가져오기)
> 5. [각 과목별 공지 / 과제 포스트 가져오기](#5-각-과목별-공지--과제-포스트-가져오기)
> 6. [최종 코드](#6-최종-코드)


<br/>


## 1. 페이지 불러오기

```py
from selenium import webdriver # 모듈 불러오기

driver = webdriver.Chrome('크롬 드라이버의 절대 경로')
url = 'https://portal.sejong.ac.kr/jsp/login/loginSSL.jsp?rtUrl=blackboard.sejong.ac.kr'
driver.get(url)

while(True):
    pass
```

이렇게 코드를 작성하고 실행시키면 블랙보드 로그인 화면이 뜨게 된다.  
*(마지막 `while`문은 chrome창이 자동 종료되는 오류를 결하는 코드이다. - 발생 이유를 잘 모르겠다 😥)*

<br/>

## 2. 블랙보드 로그인

`<F12>` 개발자 도구를 사용 !

<br/>

![image](https://user-images.githubusercontent.com/62230430/108622255-da2ac400-747a-11eb-8905-93b5601efe56.png)



- 키보드 보안 해제

세종대학교는 참고한 사이트와는 다르게 보안 키보드 보안이 있어서 해제를 해줘야 한다.
이 때, 키보드 보안 체크를 해제하면 알림창이 뜨기 때문에 확인을 눌러줘야 제대로 실행이 된다.

```py
from selenium.webdriver.common.alert import Alert # 알림창을 제어하기 위해 import

driver.find_element_by_name('chkNos').click()
da = Alert(driver) # da에 Alert 객체 할당
da.accept() # 확인
```

<br/>


- 아이디, 비밀번호 key 입력

```py
driver.find_element_by_name('input의 name').send_keys('아이디, 비밀번호 입력')
```

<br/>

- 로그인 버튼 클릭 

로그인 버튼을 찾아서, **오른쪽 마우스 > copy > copy by xpath**를 통해 복사한 뒤,  
`click()` 함수를 호출

```py
driver.find_element_by_xpath('XPATH 입력').click()
```

<br/>

- 전체 코드

```py
from selenium import webdriver
from selenium.webdriver.common.alert import Alert

# 페이지 불러오기
driver = webdriver.Chrome('크롬 드라이버의 절대 경로')
url = 'https://portal.sejong.ac.kr/jsp/login/loginSSL.jsp?rtUrl=blackboard.sejong.ac.kr'
driver.get(url)

# 로그인
driver.find_element_by_name('chkNos').click()
da = Alert(driver) # 알림 창 제어
da.accept()
driver.find_element_by_name('id').send_keys('') # id 입력하기
driver.find_element_by_name('password').send_keys('') # pw 입력하기
driver.find_element_by_xpath('//*[@id="loginBtn"]').click() # 로그인 버튼 클릭
```

<br/>

## 3. 코스 과목 가져오기

- 코스 리스트가 load 될 때까지 기다리기

```py
try: # load 될 때까지 기다리기
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "course-org-list")))
finally:
    pass
```

클래스 이름이 `corse-org-list`인 element가 load될 때까지 20초간 기다려준다.  
하지만 세종대학교 블랙보드 코스는 보이는 과목만 load되기 때문에 스크롤 다운을 해줘야 한다.

<br/>

```py
body = driver.find_element_by_css_selector('body')
body.click()

for i in range(8):
    body.send_keys(Keys.PAGE_DOWN)
    
time.sleep(2) # 스크롤 후에 load 될 때까지 2초 기다리기
```

<br/>

- 각 코스의 ID 값 알아내기

```py
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
```


모든 과목의 링크가 `https://blackboard.sejong.ac.kr/webapps/blackboard/execute/announcement?method=search&context=course_entry&course_id=*ID 값*&handle=announcements_entry&mode=view`의 형식으로 되어있기 때문에 각 코스의 ID 값을 알아내야 한다.  
<br/>
ID 값은 `course-element-card` 클래스를 가진 element의 id 값이다 !  
알아낸 값으로 url을 만들어 list에 넣으면 된다.

<br/>

- 전체 코드

```py
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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
```

<br/>

## 4. 각 과목별 공지 / 과제 페이지 가져오기

`bs4`, `beautifulSoup` 사용

- 공지 페이지 가져오기

공지는 과목 url과 동일하다 !

<br/>

- 과제 페이지 가져오기

```py
from selenium import webdriver # 모듈 불러오기
from bs4 import BeautifulSoup as bs # html 파싱을 위해
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

for i in course_detail_list:
    driver.get(i[0])
    try:
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "courseMenuPalette_contents")))
                      
        homework_html = driver.find_element_by_xpath('//*[@id="courseMenuPalette_contents"]').get_attribute('innerHTML')
        soup = bs(homework_html, 'html.parser') # html의 관점으로 문자열 이해시키기 위한 코드
        nav_bars = soup.find_all('a')
        for bar in nav_bars:
            if str(bar.find('span').text) == '과제' or str(bar.find('span').text) == 'Assignments':
                homework_url = 'https://blackboard.sejong.ac.kr' + str(bar['href'])
                i.append(homework_url)

    except Exception as e:
        homework_html = None
        print(e)
        pass
print(course_detail_list)
```

공지와 달리 과제는 없는 과목도 존재하기 때문에 예외 처리한다.  

<br/>

## 5. 각 과목별 공지 / 과제 포스트 가져오기


```py
from selenium import webdriver # 모듈 불러오기
from bs4 import BeautifulSoup as bs # html 파싱을 위해
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

for i in course_detail_list:
    driver.get(i[0])
    try:
        # Page Load 기다리기
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "courseMenuPalette_contents")))

        # 공지 가져오기
        announce_raw = driver.page_source
        soup = bs(announce_raw, 'html.parser')
        announcements = soup.select('li.clearfix')[10:] # select(css selector)
        announcements.reverse() # 오래된 것부터 차례로 보여줌
        
        for ann in announcements:
            print(ann.attrs['id'])
            print(ann.text)
            print('---------------')

        # 과제란이 있으면 가져오기
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
```

이런 식으로 다른 메뉴의 정보도 가져올 수 있다 !

<br/>

## 6. 최종 코드

```py
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

        # 과제란이 있으면 가져오기, 없으면 에러발생 -> except
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
```


