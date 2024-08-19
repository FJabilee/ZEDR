from playwright.sync_api import sync_playwright
import random
import requests
import time

def generate_phone_number(country_code='9', number_length=9):
    number = ''.join([str(random.randint(0, 9)) for _ in range(number_length)])
    phone_number = f"{country_code}{number}"
    return phone_number

def generate_otp(number_length=6):
    otp_number = ''.join([str(random.randint(0, 9)) for _ in range(number_length)])
    return otp_number

def fetch_random_data():
    response = requests.get('https://xiaofomation.com/api/?country=ph', headers={"Accept": "application/json"})
    return response.json()

#  INSERT YOUR PROXY DETAILS HERE
proxy = {
    "server": "http://PROXY_IP:PROXY_PORT",
    "username": "PROXY_USER",
    "password": "PROXY_PASS"
}
#  INSERT YOUR REFERRAL HERE
REF_CODE = 'REF_CODE'
def fill_form_and_verify(url, retries=3):
    while retries > 0:
        try:
            # Fetch new random data for each retry
            random_data = fetch_random_data()
            first_name = random_data['person']['first_name']
            last_name = random_data['person']['last_name']
            email = random_data['person']['email']
            tel_nf = random_data['person']['phone']
            tel = tel_nf.split(' ')[1]
            otp = generate_otp()

            # Launch the browser with proxy
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True, 
                    proxy={
                        "server": proxy["server"],
                        "username": proxy["username"],
                        "password": proxy["password"]
                    }
                )
                page = browser.new_page()

                page.goto(url)

                print("Waiting for page to load...")
                page.wait_for_load_state('networkidle')

                print(f"Registering an Account with phone number: {tel}")
                page.fill('input[placeholder="First Name"]', first_name)
                page.fill('input[placeholder="Last Name"]', last_name)
                page.fill('input[placeholder="Email"]', email)
                page.fill('input[type="tel"]', tel)
                page.fill('input[placeholder="Referral code (Optional)"]', REF_CODE)

                page.click('label[for="terms"]')
                page.click('label[for="sms"]')

                page.wait_for_selector('button[type="submit"]:not([disabled])', timeout=10000)
                page.click('button[type="submit"]')

                page.wait_for_selector('input[placeholder="Verification code"]', timeout=10000)
                
                page.wait_for_timeout(3000)
                
                page.fill('input[placeholder="Verification code"]', otp)

                page.wait_for_selector('button[type="submit"]:not([disabled])', timeout=10000)
                page.click('button[type="submit"]')

                page.wait_for_selector('div.signup-success_content__CblSu', timeout=30000)
                page.wait_for_selector('h2:has-text("You\'re on the waitlist!")', timeout=30000)
                page.wait_for_timeout(5000)
                browser.close()
                print("Form submitted successfully and success page detected.")
                break
        except TimeoutError:
            print("TimeoutError encountered. Retrying...")
            retries -= 1
            if retries == 0:
                print("Failed to submit the form after multiple retries.")
                browser.close()
        except Exception as e:
            print(f"An error occurred: {e}. Retrying...")
            retries -= 1
            if retries == 0:
                print("Failed to submit the form after multiple retries.")
                browser.close()


if __name__ == "__main__":
    url = f"https://waitlist.zed.co/sign-up?r={REF_CODE}"

    number_of_runs = 1

    for _ in range(number_of_runs):

        fill_form_and_verify(url)
        time.sleep(300) # 5Minutes
