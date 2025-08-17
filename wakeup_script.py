import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- URL ứng dụng của bạn ---
# URL cho dự án mới
APP_URL = "https://vqgfnjwpybwjtqrh6senci.streamlit.app/"
# -----------------------------

print("--- Setting up headless Chrome browser ---")
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    print(f"--- Navigating to {APP_URL} ---")
    driver.get(APP_URL)

    # Logic kiểm tra ứng dụng có đang "ngủ" hay không
    try:
        print("--- Checking if app is asleep (short wait)... ---")
        short_wait = WebDriverWait(driver, 5)
        wakeup_button = short_wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Yes, get this app back up!')]"))
        )
        
        print("--- App is asleep. Clicking wakeup button. ---")
        wakeup_button.click()

    except TimeoutException:
        print("--- Wakeup button not found, assuming app is already awake or waking up. ---")
        pass 

    # Chờ và chuyển vào iframe chứa ứng dụng Streamlit
    print("--- Switching to the Streamlit iframe... ---")
    wait = WebDriverWait(driver, 60)
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
    print("--- Successfully switched to iframe. ---")

    # Bước xác minh cuối cùng (bên trong iframe)
    print("--- Verifying app has fully loaded (long wait)... ---")
    long_wait = WebDriverWait(driver, 120)
    long_wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='stAppViewContainer']"))
    )
    
    print("--- Verification successful! App is ready. ---")

except Exception as e:
    print("--- An unexpected error occurred. ---")
    print(f"Details: {e}")
    driver.save_screenshot("debug_screenshot.png")
    raise e

finally:
    print("--- Closing browser ---")
    driver.quit()
