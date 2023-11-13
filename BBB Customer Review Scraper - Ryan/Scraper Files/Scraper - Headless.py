import json
from datetime import datetime, timedelta
from art import *
import sys
from requests_html import HTMLSession

# Take url and no_of_days from command line with url (ask for url if not provided)
if len(sys.argv) < 2:
    print("Usage: python myscript.py <url> <no_of_days>")
    quit()
else:
    # Access and print the command-line arguments
    script_name = sys.argv[0]
    url = str(sys.argv[1]).replace("/customer-reviews", "")
    no_of_days = int(sys.argv[2])

    print("Script name:", script_name)
    print("Arguments:", url, no_of_days)

# ASCII Art
art = text2art("BBB Scraper", font="small")
print(art)

# Prepare variables for scraping
page = 1
page_size = 15
business_Id = url.split('-')[-1]
bbb_id = url.split('-')[-2]
all_reviews_data = []


def days_until_date(input_date):
    date_format = "%m-%d-%Y"

    try:
        input_datetime = datetime.strptime(input_date, date_format)

        current_datetime = datetime.now()

        time_difference = current_datetime - input_datetime

        days_difference = time_difference.days

        return int(days_difference)
    except ValueError:
        return "Invalid date format"


keep_running = True
session = HTMLSession()
while keep_running:
    page_url = f'https://www.bbb.org/api/businessprofile/customerreviews?page={page}&pageSize={page_size}&businessId={business_Id}&bbbId={bbb_id}&sort=reviewDate%20desc,%20id%20desc'

    res = session.get(page_url)
    # print(res.text)

    try:
        json_result = res.json()
    except json.decoder.JSONDecodeError:
        print("Please Use Browser Based Scraper, This URL maybe protected by CloudFlare")
        quit()
    items = json_result['items']

    if not items:
        break

    for item in items:
        review_stars = item['reviewStarRating']
        user_name = item['displayName']
        date = f"{item['date']['month']}-{item['date']['day']}-{item['date']['year']}"
        details = item['text']
        if details is None:
            try:
                details = item['extendedText'][0]['text']
            except:
                details = ""

        data = {
            'User': user_name,
            'Stars': review_stars,
            'Date': date,
            'Source_url': url + "/customer-reviews",
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
