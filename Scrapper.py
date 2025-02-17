from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import csv
from bs4 import BeautifulSoup

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

# Function to extract car details from a single car listing
def extract_car_details(car):
    name = car.find('h3', class_='VehicleTile_make__p7ccn').text.strip()
    car_type = car.find('span', class_='VehicleTile_model__t5_Fc').text
    ymt = car.find('div', class_='VehicleTile_labels__7NUyF').text  # yyyym..m milesGasType
    st_ind = ymt.find(' miles')
    mileage = float(ymt[4:st_ind].replace(',', '.'))
    year = int(ymt[:4])
    type = ymt[st_ind + len(' miles'):]
    price = car.find('span',
                     class_='TotalPrice_totalPrice__mFrNf')  # because some cars have a discount; different html element
    if price is None:
        price = float('nan')
    else:
        price = float(price.text.replace(',', '.').replace('£', ''))
    return name, car_type, mileage, year, type, price


# Function to extract car details from a page
def extract_car_details_from_page(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    cars = soup.find_all('div', class_='VehicleTile_content__L07gz')
    car_details = []
    for car in cars:
        car_details.append(extract_car_details(car))
    return car_details


# Main function to extract car details from multiple pages
def extract_car_details_from_pages(base_url, base_url2, num_pages, driver):

    url = f"{base_url}{2}{base_url2}"
    driver.get(url)
    time.sleep(3)  # Let the page load
    blue_button = driver.find_element(By.CLASS_NAME, 'css-47sehv')
    blue_button.click()
    time.sleep(2)

    max_div = driver.find_element(By.CLASS_NAME, 'Default_pagination__3ptDu').text
    max_div = int(max_div[4:])
    if max_div < num_pages:
        num_pages = max_div

    print(f'Max pages: {num_pages}/{max_div}')

    all_car_details = []
    for page_num in range(2, num_pages + 1):
        url = f"{base_url}{page_num}{base_url2}"
        driver.get(url)

        car_details = extract_car_details_from_page(driver.page_source)
        all_car_details.extend(car_details)

    return all_car_details


try:
    # Base URL of the webpage
    base_url = "https://heycar.com/uk/autos/make/audi/page/"
    base_url2 = "?lat=51.518&lon=-0.0784&postcode=E1+7JH&sort=relevance-desc&stock-condition=used"
    num_pages = 564 // 2 # TODO change

    all_car_details = extract_car_details_from_pages(base_url, base_url2, num_pages, driver)

    # save to csv
    with open('dataset.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Type', 'Mileage', 'Year', 'Condition', 'Price'])
        writer.writerows(all_car_details)


except Exception as e:
    print("An error occurred:", e)

finally:
    driver.quit()