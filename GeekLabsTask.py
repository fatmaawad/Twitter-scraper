import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import schedule
import time
import re 

# Setup logging
logging.basicConfig(filename='twitter_scraper.log', level=logging.INFO)

# Define the Twitter accounts and the stock symbol to look for
twitter_accounts = [
 "https://twitter.com/Mr_Derivatives ",
"https://twitter.com/warrior_0719",
"https://twitter.com/ChartingProdigy",
"https://twitter.com/allstarcharts",
"https://twitter.com/yuriymatso",
"https://twitter.com/TriggerTrades",
"https://twitter.com/AdamMancini4 ",
"https://twitter.com/CordovaTrades" ,
"https://twitter.com/Barchart",
"https://twitter.com/RoyLMattox"
   
]

ticker = "$TSLA"  # Stock symbol to look for
interval = 1 # Time interval in minutes

#scrape a single account
def scrape_account(account):
    mention_count = 0

    # Setup Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    # Pretend to be a desktop browser
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")

    # Setup WebDriver
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=options)

    try:
        logging.info(f"Scraping {account}")
        
        #go to account
        driver.get(account)
        
        #scroll to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for 10 seconds to ensure page loads completely
        time.sleep(10)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        ticker_a = soup.find_all('a', attrs={'class': 'css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3 r-1loqt21'},   string=lambda t: t and t.startswith('$'))

        # Check if any tickers were found using <a> tags
        if ticker_a:
            # Filter ticks based on the regex pattern
            filtered_ticker_a = [tick.get_text(strip=True) for tick in ticker_a if re.match(r'^\$\w{3,4}$',tick.get_text(strip=True))]
            
            # Save the filtered ticks to the file
            with open('found_tickers_a.txt', 'w', encoding='utf-8') as file:
                for tick in filtered_ticker_a:
                    file.write(tick + '\n')
        else:
            # If no tickers were found using <a> tags, try with <span> tags
            ticks_span = soup.find_all('span', {'class': 'css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3'})
            
            # Filter ticks based on the regex pattern
            filtered_ticks_span = [tick.get_text(strip=True) for tick in ticks_span if re.match(r'^\$\w{3,4}$'
                                     , tick.get_text(strip=True))]
            with open('found_spans_span.txt', 'w', encoding='utf-8') as file:
                for tick in filtered_ticks_span:
                    file.write(tick + '\n')
            
        for tick in filtered_ticker_a +filtered_ticks_span:
            if ticker == tick:
                mention_count += 1
                
        logging.info(f"Found {mention_count} mentions of '{ticker}' in the filtered ticks.")

                
        with open(f"{account.replace('https://twitter.com/', '')}_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        driver.quit()  # Close the browser window

    logging.info(
        f"'{ticker}' was mentioned '{mention_count}' times in the last '{interval}' minutes.")


def scrape_twitter():
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(scrape_account, twitter_accounts)


# Initial run
scrape_twitter()

# Schedule the scraper to run periodically
schedule.every(interval).minutes.do(scrape_twitter)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)