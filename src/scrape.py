from supabase import create_client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import requests
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

def download_image(image_url, save_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.anime-planet.com/'
    }
    
    try:
        response = requests.get(image_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image {image_url}: {str(e)}")
        return False

characters = []
try:
    cur_page = 1

    driver = setup_driver()
    
    for i in range(1, 51): # scraping the entire site 
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
                    
            # Fixing some series names
            if series == "Juju Sanpo":
                series = "Jujutsu Kaisen"
            elif series == "Spoof on Titan":
                series = "Attack on Titan"
            elif series == "Demon Slayer: Kimetsu Academy" or series == "Kimetsu Gakuen: Valentine-hen":
                series = "Demon Slayer"
            elif series == "The Seven Stories":
                series = "Seven Deadly Sins"
            elif series == "Dr. Slump":
                series = "Dragon Ball"
            
            
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-'))
            safe_name = safe_name.replace(" ", "_")
            safe_series = "".join(c for c in series if c.isalnum() or c in (' ', '_', '-'))
            safe_series = safe_series.replace(" ", "_")
            path = f"./assets/avatars/{safe_name}_{safe_series}." + image.split(".")[-1]
            link = ""
            
            
            if download_image(image, path):
                with open(path, 'rb') as f:
                    try:
                        res = supabase.storage.from_("avatars").upload(
                            file=f,
                            path=path,
                            file_options={"cache-control": "3600", "upsert": "false"},
                        )
                    except Exception as e:
                        print(f'{str(e)}')
                
                try:
                    link = supabase.storage.from_("avatars").get_public_url(path)
                except Exception as e:
                    link = ""
                
                # delete the local file
                os.remove(path)

 

                    
            if not link:
                print(f"Error uploading image {image} to Supabase Storage")
                continue
            
            character = {
                "name": name,
                "series": series,
                "avatar": link,
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
    
