import time
import undetected_chromedriver as uc
import json
from datetime import datetime, timedelta
from art import *

# ASCII Art
art = text2art("BBB Scraper", font="small")
print(art)


# Prompt the user for inputs
url = input('Enter a url: ').replace("/customer-reviews", "")
no_of_days = int(input('Enter a day no: '))

# Set up the Chrome WebDriver
uc_options = uc.ChromeOptions()
uc_options.headless = False
driver = uc.Chrome(options=uc_options)

# Open a new tab with the specified URL
driver.execute_script(
    f"window.open('https://www.bbb.org/api/businessprofile/customerreviews?page=3"
    f"&pageSize=15&businessId=881071&bbbId=1116&sort=reviewDate%20desc,%20id%20desc', '_blank');")
time.sleep(20)

# Switch to the first tab
driver.switch_to.window(driver.window_handles[0])
time.sleep(5)

# Prepare variables for scraping
page = 1
page_size = 15
business_Id = url.split('-')[-1]
bbb_id = url.split('-')[-2]
all_reviews_data = []


def days_until_date(input_date):
    date_format = "%d-%m-%Y"

    try:
        input_datetime = datetime.strptime(input_date, date_format)

        current_datetime = datetime.now()

        time_difference = current_datetime - input_datetime

        days_difference = time_difference.days

        return int(days_difference)
    except ValueError:
        return "Invalid date format"


keep_running = True

while keep_running:
    page_url = f'https://www.bbb.org/api/businessprofile/customerreviews?page={page}&pageSize={page_size}&businessId={business_Id}&bbbId={bbb_id}&sort=reviewDate%20desc,%20id%20desc'

    driver.get(page_url)

    # Extract relevant data from the page source
    while True:
        try:
            splitting_data = driver.page_source.split('>{')[1].split('}<')[0]
            break
        except:
            time.sleep(0.1)

    json_result = json.loads('{' + splitting_data + '}')
    items = json_result['items']

    if not items:
        break

    for item in items:
        review_stars = item['reviewStarRating']
        user_name = item['displayName']
        date = f"{item['date']['day']}-{item['date']['month']}-{item['date']['year']}"
        details = item['text']

        data = {
            'User': user_name,
            'Stars': review_stars,
            'Date': date,
            'Source_url': page_url,
            'Details': details
        }

        days_difference = days_until_date(date)

        if days_difference <= no_of_days:
            all_reviews_data.append(data)
        else:
            keep_running = False
            break

    if not keep_running:
        break

    page += 1


def create_date_string():
    start_date = datetime.now()
    end_date = start_date - timedelta(days=no_of_days)

    return f"{end_date.strftime('%m%d%y')}_{start_date.strftime('%m%d%y')}"  # Format the start and end dates


# Get the current folder location


# Create a filename based on the current date range
file_name_slug = fr"BBB_reviews_{create_date_string()}"


# Save the scraped data to a JSON file
with open(f"{file_name_slug}.json", "w", encoding="utf-8") as f:
    json.dump(all_reviews_data, f, indent=4)

# Print a completion message
print("Finished Scraping")
driver.quit()