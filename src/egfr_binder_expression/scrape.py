import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
import pandas as pd

# necessary to do this because deposited datasets only contain sequences screened for binding ie lack ones that didn't express

def setup_and_load_page(url='https://foundry.adaptyvbio.com/egfr_design_competition', visible=False):
    chrome_options = Options()
    if not visible:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)

    time.sleep(3)
    print("Page loaded successfully")
    
    total_height = driver.execute_script("return document.body.scrollHeight")
    scroll_height = total_height // 2
    driver.execute_script(f"window.scrollTo(0, {scroll_height});")
    time.sleep(2)

    return driver


def expand_rows(driver):
    table_body = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#radix-\\:r6\\:-content-results > div > div.rounded-md.mt-4.border-slate-100.bg-white.border > div > table > tbody"))
    )
    # print("Table body found")

    rows = table_body.find_elements(By.TAG_NAME, "tr")

    for row in rows:
        
        try:
            # Find the clickable element within the row (the chevron icon)
            clickable_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(1) > div.font-medium.flex.items-center.whitespace-nowrap")


            # Click the element using JavaScript executor for better reliability
            driver.execute_script("arguments[0].click();", clickable_element)
            # print("Clicked the chevron icon successfully")

            # Wait for any potential changes after clicking (adjust time if needed)
            time.sleep(0.2)
            # Find the close button in the popup
            close_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.absolute.right-4.top-4"))
            )
            # print("Close button found")

            # Click the close button
            driver.execute_script("arguments[0].click();", close_button)
            # print("Clicked close button")
        except Exception as e:
            pass
        
    return True

def extract_data(driver):
    
    table_body = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#radix-\\:r6\\:-content-results > div > div.rounded-md.mt-4.border-slate-100.bg-white.border > div > table > tbody"))
    )

    
    # Define a mapping of column numbers to keys
    column_mapping = {
        2: 'designer',
        3: 'design_name',
        4: 'binding',
        5: 'expression',
        6: 'replicates',
        7: 'KD_M_Mean',
        8: 'KD_M_STD_log10',
        9: 'Kon_1_Ms_Mean',
        10: 'Kon_1_Ms_STD_log10',
        11: 'Koff_1_s_Mean',
        12: 'Koff_1_s_STD_log10',
        13: 'sequence'
    }

    expanded_rows = table_body.find_elements(By.TAG_NAME, "tr")

    datas = []
    for row in expanded_rows:   
        # Create a dictionary to map the data
        data_dict = {}


        # Loop through the columns and extract data
        for col_num, key in column_mapping.items():
            cell = row.find_element(By.CSS_SELECTOR, f"td:nth-child({col_num}) > div")
            data_dict[key] = cell.text

        if data_dict['designer'] != '':
            current_designer = data_dict['designer']
        data_dict['propagated_designer'] = current_designer
        datas.append(data_dict)
    return datas

def next_page(driver):
    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    try:
        # Find and click the "Next" button
        next_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))
        )
        next_button.click()
        time.sleep(3)  # Wait for the page to load
        return True
    except:
        return False

def scrape_all_pages(visible=False):
    driver = setup_and_load_page(visible=visible)
    
    all_data = []
    page = 0
    with tqdm(desc="Scraping pages", unit="page") as pbar:
        while True:
            expand_rows(driver)
            all_data.extend(extract_data(driver))
            
            if not next_page(driver):
                break
            
            page += 1
            pbar.update(1)
            
            if page >= 20:  # Limit to 20 pages
                break
    
    driver.quit()
    return all_data

if __name__ == '__main__':
    visible_browser = input("Do you want to see the browser while scraping? (y/n): ").lower() == 'y'
    data = scrape_all_pages(visible=visible_browser)
    df = pd.DataFrame(data)
    df.to_csv('data/scraped_egfr_binder_expression.csv', index=False)
    print(f"Scraped {len(data)} rows of data.")