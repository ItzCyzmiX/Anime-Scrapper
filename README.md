# Anime Character Scraper

This project is a web scraper that collects information about anime characters from [Anime-Planet](https://www.anime-planet.com/) and stores it in a Supabase database.

## Features

- Scrapes character data including name, series, and avatar image
- Uploads avatar images to Supabase storage
- Stores character information in a Supabase database
- Handles pagination to scrape multiple pages

## Prerequisites

- Python 3.x
- Selenium WebDriver
- Firefox browser
- Supabase account and API key

## Setup

1. Clone the repository
2. Install required dependencies:
   ```
   pip install supabase selenium webdriver_manager requests
   ```
3. Set up environment variables:
   - `SUPABASE_KEY`: Your Supabase API key

## Usage

Run the script:

```
python src/scrape.py
```

The script will scrape character data from Anime-Planet, upload images to Supabase storage, and store character information in the Supabase database.

## Note

This scraper is for educational purposes only. Please respect Anime-Planet's terms of service and use their data responsibly.
