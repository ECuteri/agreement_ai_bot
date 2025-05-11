from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time

app = Flask(__name__)



@app.route('/get_company_info', methods=['POST'])
def get_company_info():
    print("\n--- New Request ---")
    data = request.get_json()

    if data and 'debug_url' in data:
        debug_target_url = data['debug_url']
        print(f"[DEBUG_MODE] Received request to fetch source for URL: {debug_target_url}")

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        driver = webdriver.Chrome(options=options)
        
        try:
            print(f"[DEBUG_MODE] Navigating to {debug_target_url}")
            driver.get(debug_target_url)
            time.sleep(3) # Allow some time for dynamic content to load, adjust if needed
            page_source = driver.page_source
            debug_file_name = "debug_specific_page.html"
            with open(debug_file_name, "w", encoding="utf-8") as f:
                f.write(page_source)
            print(f"[DEBUG_MODE] Page source saved to {debug_file_name}")
            driver.quit()
            return jsonify({
                'message': f'Successfully fetched and saved HTML from {debug_target_url}',
                'output_file': debug_file_name,
                'size': len(page_source)
            })
        except Exception as e:
            print(f"[DEBUG_MODE] Error fetching debug URL: {e}")
            if 'driver' in locals() and driver:
                driver.quit()
            return jsonify({'error': f'Failed to fetch {debug_target_url}: {str(e)}'}), 500

    if not data or 'vat_id' not in data:
        print("[ERROR] VAT ID not provided in request.")
        return jsonify({'error': 'VAT ID not provided'}), 400

    vat_id = data['vat_id']
    print(f"[INFO] Received VAT ID: {vat_id}")
    target_url = 'https://www.ufficiocamerale.it/'

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no browser UI)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    print("[INFO] Initializing WebDriver (Selenium Manager should handle driver download if needed)...")
    
    # Selenium Manager will automatically find or download the correct ChromeDriver
    driver = webdriver.Chrome(options=options)
    print("[INFO] WebDriver initialized.")

    company_info = {
        'business_name': None,
        'address': None,
        'zip_code': None,
        'city': None,
        'state': None, # Provincia
        'error': None
    }

    try:
        print(f"[INFO] Navigating to URL: {target_url}")
        driver.get(target_url)
        print("[INFO] Page loaded.")

        # --- Save page source for debugging ---
        page_source_file = "ufficiocamerale_source.html"
        try:
            print(f"[INFO] Saving page source to {page_source_file}...")
            with open(page_source_file, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"[INFO] Page source saved successfully to {page_source_file}.")
        except Exception as e_save:
            print(f"[ERROR] Could not save page source: {e_save}")
        # --- End save page source ---

        # --- STEP 1: Find VAT ID input and Cerca button ---
        # IMPORTANT: These selectors are educated guesses and will likely need to be updated.
        # You need to inspect the website https://www.ufficiocamerale.it/ to find the correct ones.
        
        # Correct selectors based on saved HTML
        vat_input_selector_type = By.ID
        vat_input_selector_value = "search_input"

        # Even more specific selector for the search button
        search_button_selector_type = By.XPATH
        search_button_selector_value = "//button[@type='submit' and normalize-space(.)='Cerca' and contains(@class, 'btn-primary') and contains(@class, 'text-uppercase')]"

        wait = WebDriverWait(driver, 10) # Wait up to 10 seconds

        print(f"[INFO] Attempting to find VAT input field with selector: {vat_input_selector_type}, {vat_input_selector_value}")
        vat_input_field = wait.until(EC.presence_of_element_located((vat_input_selector_type, vat_input_selector_value)))
        print("[INFO] VAT input field found.")
        vat_input_field.send_keys(vat_id)
        print(f"[INFO] Sent keys '{vat_id}' to VAT input field.")
        
        # Give a small buffer for any JS or to make interaction more human-like
        time.sleep(0.5) 

        print(f"[INFO] Attempting to find search button with selector: {search_button_selector_type}, {search_button_selector_value}")
        search_button = wait.until(EC.element_to_be_clickable((search_button_selector_type, search_button_selector_value)))
        print("[INFO] Search button found.")
        search_button.click()
        print("[INFO] Search button clicked.")

        # --- Add more diagnostics post-click ---
        time.sleep(2) # Give a couple of seconds for any immediate redirects or JS to start.
        current_url_post_click = "Unknown_URL_Post_Click"
        current_title_post_click = "Unknown_Title_Post_Click"
        try:
            current_url_post_click = driver.current_url
            current_title_post_click = driver.title
        except Exception as e_diag:
            print(f"[DEBUG_ERROR] Could not retrieve URL/title post-click: {e_diag}")
        
        print(f"[DEBUG_POST_CLICK] URL: {current_url_post_click}")
        print(f"[DEBUG_POST_CLICK] Title: {current_title_post_click}")

        # Save page source immediately after click for detailed inspection
        timestamp_post_click = time.strftime("%Y%m%d-%H%M%S")
        debug_filename_html_post_click = f"post_click_source_{timestamp_post_click}.html"
        try:
            with open(debug_filename_html_post_click, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"[DEBUG_POST_CLICK] Page source saved to: {debug_filename_html_post_click}")
        except Exception as e_save_html_post_click:
            print(f"[DEBUG_ERROR] Could not save post-click page source: {e_save_html_post_click}")
        # --- End added diagnostics ---