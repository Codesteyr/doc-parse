from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

chrome_options = Options()
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

base_url = "https://prodoctorov.ru/krasnodar/oftalmolog/?page="

all_doctors = []

MAX_PAGES = 50  

page = 1
while page <= MAX_PAGES:
    url = base_url + str(page)
    driver.get(url)
    time.sleep(3)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    doctors = soup.find_all("div", class_="b-doctor-card")

    if not doctors or len(doctors) <= 8:
        print(f"📌 Парсинг остановлен на странице {page} (всего врачей: {len(doctors)})")
        break
    
    for doctor in doctors:
        name_tag = doctor.find("span", class_="b-doctor-card__name-surname")
        if name_tag:
            all_doctors.append(name_tag.get_text(strip=True))

    print(f"✅ Собрано {len(doctors)} докторов с страницы {page}")
    page += 1

driver.quit()

df = pd.DataFrame({"ФИО": all_doctors})
df.to_excel("doctors.xlsx", index=False, engine="openpyxl")

print("\n✅ Данные успешно сохранены в doctors.xlsx!")
