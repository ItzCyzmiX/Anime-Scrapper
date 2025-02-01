from supabase import create_client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import os

url = "https://sgvkmwnesmllzgmdpddw.supabase.co"
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

user = supabase.auth.sign_in_with_password(
    {"email": "admin@gmail.com", "password": "adminadmin"}
)

def setup_driver():
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    # Set specific window size to ensure consistency
    firefox_options.add_argument("--width=1920")
    firefox_options.add_argument("--height=1080")
    
    # Add timeout settings
    firefox_options.set_preference("network.http.connection-timeout", 60)
    firefox_options.set_preference("network.http.response-timeout", 60)
    
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Remote(
        command_executor='http://localhost:4444/wd/hub',
        options=firefox_options
    )
    # Set page load timeout
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(20)
    
    return driver

characters = []
try:
    cur_page = 1

    driver = setup_driver()
    
    for i in range(1, 21): # where all known characters are located 
        driver.get('https://www.anime-planet.com/characters/all?page=' + str(cur_page))

        driver.implicitly_wait(3)

        characters_table = driver.find_element(By.TAG_NAME, "tbody")
        characters_rows = characters_table.find_elements(By.TAG_NAME, "tr")
        
        for row in characters_rows:
            image = row.find_element(By.TAG_NAME, "img").get_attribute("src").split("?")[0]
            name = row.find_element(By.CSS_SELECTOR, "a.name").text
            animes_in = row.find_element(By.CSS_SELECTOR, "td.tableAnime").find_elements(By.TAG_NAME, "li")
            series = ""
            for anime in animes_in:
                if not series:
                    series = anime.text
                elif series and len(series) > len(anime.text):
                    series = anime.text
            
            character = {
                "name": name,
                "series": series,
                "avatar": image
            }
            
            if character not in characters:
                characters.append(character)
                print(f"Added: {name} from {series}")  

        cur_page += 1
except Exception as e:
    print(f"Fatale Error: {str(e)}")
    raise e
finally:
    print(f"Scraped {len(characters)} characters\nAdding to database...")
    
    response = (
        supabase.table("Characters")
        .insert(characters)
        .execute()
    )
    print(f"{len(characters)} Characters added to database!")

    driver.quit()
    
