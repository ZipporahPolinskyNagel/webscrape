from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import re

driver = webdriver.Chrome()

# Go to the page that we want to scrape
current_url = "https://beerconnoisseur.com/reviews"
driver.get(current_url)

csv_file = open('beer_reviews.csv', 'w')
writer = csv.writer(csv_file)
writer.writerow(["title", "judges_rating", "aroma", "appearance", "flavor", "mouthfeel", "overall", "date",
                 "brewery", "brew_style", "availability", "state", "country", "reviewer", "body"])
# Page index used to keep track of where we are.
page_index = 1

# Initialize two variables refer to the next button on the current page and previous page.
prev_button = None
current_button = None

while True:
    try:

        if prev_button is not None:
            WebDriverWait(driver, 10).until(EC.staleness_of(prev_button))

        print("Scraping Page number " + str(page_index))
        page_index = page_index + 1
        # Find all the reviews. The find_elements function will return a list of selenium select elements.
        # Check the documentation here: http://selenium-python.readthedocs.io/locating-elements.html

        # Find all the reviews on the page
        wait_review = WebDriverWait(driver, 10)

        reviews = wait_review.until(EC.presence_of_all_elements_located((By.XPATH,
                                                                         "//div[@class='content-wrapper']//div[starts-with(@class, 'views-row')]")))

        reviews_size = len(reviews)

        # Iterate through the list and find the details of each review.
        for review_index in range(reviews_size):
            review = driver.find_elements_by_xpath("//div[@class='content-wrapper']//div[starts-with(@class, 'views-row')]")[review_index]

            review_dict = {}
            #title
            try:
                title = review.find_element_by_xpath( './div[@class="views-field views-field-title-field"]').text
                review_dict['title'] = title
            except:
                review_dict['title'] = None

            #judges_rating
            try:
                judges_rating = review.find_element_by_xpath( './div[@class="views-field views-field-field-judges-rating"]/div').text
                review_dict['judges_rating'] = judges_rating
            except:
                review_dict['judges_rating'] = None

            #aroma
            try:
                aroma = review.find_element_by_xpath('./div[@class="views-field views-field-field-judge-aroma"]/div').text
                review_dict['aroma'] = aroma
            except:
                review_dict['aroma'] = None

            #appearance
            try:
                appearance = review.find_element_by_xpath('./div[@class="views-field views-field-field-judge-appearance"]/div').text
                review_dict['appearance'] = appearance
            except:
                review_dict['appearance'] = None

            #flavor
            try:
                flavor = review.find_element_by_xpath('./div[@class="views-field views-field-field-judge-flavor"]/div').text
                review_dict['flavor'] = flavor
            except:
                review_dict['flavor'] = None

            #mouthfeel
            try:
                mouthfeel = review.find_element_by_xpath('./div[@class="views-field views-field-field-judge-mouthfeel"]/div').text
                review_dict['mouthfeel'] = mouthfeel
            except:
                review_dict['mouthfeel'] = None

            #overall
            try:
                overall = review.find_element_by_xpath('./div[@class="views-field views-field-field-overall-impression"]/div').text
                review_dict['overall'] = overall
            except:
                review_dict['overall'] = None

            # drill down to details
            url = review.find_element_by_xpath(
                 './div[@class="views-field views-field-title-field"]/div[@class="field-content"]')
            try:
                 driver.find_element_by_link_text(url.text).click()
            except:
                 element = driver.find_element_by_class_name('padiClose')
                 driver.execute_script("arguments[0].click();", element)
                 driver.find_element_by_link_text(url.text).click()

            #date
            try:
                date = driver.find_element_by_xpath('//div[@class="field field-name-field-date field-type-datetime field-label-hidden"]').text
                review_dict['date'] = date
            except:
                review_dict['date'] = None


            #brewery
            try:
                brewery = driver.find_element_by_xpath('//div[@class="field field-name-field-brewery field-type-entityreference field-label-hidden"]').text
                review_dict['brewery'] = brewery
            except:
                review_dict['brewery'] = None

            #brew style
            try:
                brew_style = driver.find_element_by_xpath('//div[@class="field field-name-field-beer-style field-type-taxonomy-term-reference field-label-hidden"]').text
                review_dict['brew_style'] = brew_style
            except:
                review_dict['brew_style'] = None

            #availability
            try:
                availability = driver.find_element_by_xpath('//div[@class="field field-name-field-availability field-type-taxonomy-term-reference field-label-hidden"]').text
                review_dict['availability'] = availability
            except:
                review_dict['availability'] = None


            #state
            try:
                state = driver.find_element_by_xpath('//div[@class="field field-name-field-state field-type-list-text field-label-hidden"]').text
                review_dict['state'] = state
            except:
                review_dict['state'] = None

            #country
            try:
                country = driver.find_element_by_xpath('//div[@class="field field-name-field-country field-type-list-text field-label-hidden"]').text
                review_dict['country'] = country
            except:
                review_dict['country'] = None

            #reviewer
            try:
                reviewer = driver.find_element_by_xpath('//div[@class="username-wrapper"]/a').text
                review_dict['reviewer'] = reviewer
            except:
                review_dict['reviewer'] = None

            #body
            try:
                body = driver.find_element_by_xpath('//div[@class="field field-name-body field-type-text-with-summary field-label-hidden"]').text
                review_dict['body'] = body
            except:
                review_dict['body'] = None

            #go back - end of detail
            try:
                driver.get(current_url)

            except:
                 element = driver.find_element_by_class_name('padiClose')
                 driver.execute_script("arguments[0].click();", element)
                 driver.get(current_url)


            writer.writerow(review_dict.values())

        # Locate the next button on the page and preserve current_url because back button doesn't work.
        current_button = driver.find_element_by_xpath('//li[@class="pager-next"]')
        current_url = driver.find_element_by_xpath('//li[@class="pager-next"]/a').get_attribute("href")
        prev_button = current_button

        try:
            current_button.click()
        except:
            # add popup needs to be closed to continue the scraping
            element = driver.find_element_by_class_name('padiClose')
            driver.execute_script("arguments[0].click();", element)
            current_button.click()

    except Exception as e:
        print(e)
        csv_file.close()
        driver.close()
        break
