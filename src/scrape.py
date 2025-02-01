from supabase import create_client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pprintpp
import os

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
    driver = webdriver.Firefox(
        service=service, 
        options=firefox_options
    )
    
    # Set page load timeout
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(20)
    
    return driver

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

try:
    driver = setup_driver()
    driver.get('https://www.personality-database.com/type/14/entp-anime-characters')

    driver.implicitly_wait(10)

    prev_height = driver.execute_script('return document.body.scrollHeight')
    scrolls = 0
    while scrolls < 50:
        try: 
            wait = WebDriverWait(driver, 20)
            character_cards = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.profile-card-link'))
            )
            for char in character_cards:
                name = char.find_element(By.CSS_SELECTOR, "h2.info-name").text
                series = char.find_element(By.CSS_SELECTOR, "div.info-subcategory").text

                character_data = {
                    "name": name,
                    "series": series
                }

                if not character_data in characters:
                    characters.append(character_data)
                    pprintpp.pprint(f"Added: {name} from {series}")

            
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            driver.implicitly_wait(5)
            new_height = driver.execute_script('return document.body.scrollHeight')
            
            if new_height == prev_height:
                break 
            else:
                prev_height = new_height

            scrolls += 1
        except TimeoutException as e:
            time.sleep(10)
            pprintpp.pprint(e)
            continue 
        except Exception as e:  
            pprintpp.pprint(e)
            break

    new_characters = [char for char in characters if char not in response.data]
    pprintpp.pprint(f"Scraped {len(new_characters)} characters\nAdding to database...")
    if new_characters:
        response = (
            supabase.table("Characters")
            .insert(new_characters)
            .execute()
        )
        pprintpp.pprint(f"{len(new_characters)} Characters added to database!")
        pprintpp.pprint(response)
    else:
        pprintpp.pprint("No new characters to add.")
    
    pprintpp.pprint(response)
except Exception as e:
    pprintpp.pprint(f"Fatale Error: {str(e)}")
    raise e


driver.quit()