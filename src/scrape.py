from supabase import create_client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time 
import pprintpp
import os

url = "https://sgvkmwnesmllzgmdpddw.supabase.co"
key = os.environ.get('SUPABASE_KEY')
supabase = create_client(url, key)

user = supabase.auth.sign_in_with_password(
    {"email": "admin@gmail.com", "password": "adminadmin"}
)

response = supabase.table("Characters").select("*").execute()
characters = []

for char in response.data:  
    characters.append({
        "name": char.get('name'),
        "series": char.get('series')
    })

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.maximize_window()

driver.get('https://www.personality-database.com/type/14/entp-anime-characters')

time.sleep(10)

prev_height = driver.execute_script('return document.body.scrollHeight')

while True:
    character_cards = driver.find_elements(By.CSS_SELECTOR, 'a.profile-card-link')

    for char in character_cards:
        name = char.find_element(By.CSS_SELECTOR, "h2.info-name").text
        series = char.find_element(By.CSS_SELECTOR, "div.info-subcategory").text

        character_data = {
            "name": name,
            "series": series
        }

        if not character_data in characters:
            characters.append(character_data)

    
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    time.sleep(5)
    new_height = driver.execute_script('return document.body.scrollHeight')
    
    if new_height == prev_height:
        break 
    else:
        prev_height = new_height


response = (
    supabase.table("Characters")
    .insert(characters)
    .execute()
)

pprintpp.pprint(response)

driver.close()