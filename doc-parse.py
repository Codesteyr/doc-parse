from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# Browser settings
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

# Automatically install ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Base URL
base_url = "https://prodoctorov.ru/krasnodar/oftalmolog/?page="

# List to store doctor data
doctors_data = []

# Maximum number of pages to prevent infinite loop
MAX_PAGES = 50  

# Loop through pages
page = 1
while page <= MAX_PAGES:
    url = base_url + str(page)
    driver.get(url)
    time.sleep(3)  # Allow page to fully load
    
    # Parse the page
    soup = BeautifulSoup(driver.page_source, "html.parser")
    doctors = soup.find_all("div", class_="b-doctor-card")

    # Stop parsing if there are too few doctors or none on the page
    if not doctors or len(doctors) <= 8:
        print(f"📌 Parsing stopped on page {page} (total doctors found: {len(doctors)})")
        break
    
    # Extract doctor data
    for doctor in doctors:
        # Full name
        name_tag = doctor.find("span", class_="b-doctor-card__name-surname")
        name = name_tag.get_text(strip=True) if name_tag else "No data"

        # Experience
        experience_tag = doctor.find("div", class_="b-doctor-card__experience")
        experience = "No data"
        if experience_tag:
            exp_text = experience_tag.find("div", class_="ui-text ui-text_subtitle-1")
            if exp_text:
                experience = exp_text.get_text(strip=True)

        # Rating
        rating_tag = doctor.find("div", class_="b-stars-rate__progress")
        rating = "No data"
        if rating_tag:
            match = re.search(r'width:\s*(\d+)px', rating_tag["style"])
            if match:
                rating_value = int(match.group(1)) / 27  # Approximate rating calculation
                rating = f"{round(rating_value, 1)}"

        # Save data
        doctors_data.append({"Full Name": name, "Experience": experience, "Rating ⭐": rating})

    print(f"✅ Collected {len(doctors)} doctors from page {page}")
    page += 1

# Close browser
driver.quit()

# Create DataFrame and save to Excel
df = pd.DataFrame(doctors_data)
df.to_excel("doctors.xlsx", index=False, engine="openpyxl")

print("\n✅ Data successfully saved to doctors.xlsx!")
