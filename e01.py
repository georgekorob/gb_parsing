from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pymongo
from pprint import pprint
import json

# options = webdriver.ChromeOptions()
# options.add_argument('start-maximized')
# driver_file = 'D:/Programming/yandexdriver.exe'  # YandexDriver

driver = webdriver.Chrome(executable_path='./chromedriver.exe')  # , options=options)
driver.get('https://mail.ru/')
driver.find_element(By.CLASS_NAME, 'email-input').send_keys('study.ai_172')
driver.find_element(By.CLASS_NAME, 'button').click()
wait = WebDriverWait(driver, 10)
elem = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'password-input')))
elem.send_keys('NextPassword172???')
driver.find_element(By.CLASS_NAME, 'second-button').click()

# with open('links.json', 'r') as f:
#     all_links = json.load(f)

title_count_mail = wait.until(EC.presence_of_element_located(
    (By.XPATH, "//a[contains(@title,'Входящие')]"))).get_attribute('title')
count_mail = int(title_count_mail.split(' ')[1])
all_links = set()
while len(all_links) < count_mail:
    links = driver.find_elements(By.XPATH, "//div[@class='layout__main-frame']//a[contains(@href,'/inbox/')]")
    for link in links:
        link_href = link.get_attribute('href')
        all_links.add(link_href)
    actions = ActionChains(driver)
    actions.move_to_element(links[-1])
    actions.perform()

# with open('links.json', 'w') as f:
#     json.dump(list(all_links), f)

client = pymongo.MongoClient('localhost', 27017)
db = client['mail_database']
mails = db.mails
for link in all_links:
    driver.get(link)
    mail = {'link': link,
            'sender': wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'letter-contact'))).get_attribute('title'),
            'date': wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'letter__date'))).text,
            'theme': wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'thread__subject'))).text,
            'text': wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'letter-body'))).text}
    mails.insert_one(mail)
    pprint(mail)

driver.close()
