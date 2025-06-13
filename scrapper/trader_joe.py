import requests
from bs4 import BeautifulSoup
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def selenium_driver(url):
    # Set up the webdriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Navigate to the Trader Joe's products page
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)
    
    return driver

def scrape_product_urls(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    ul_elements = soup.find('ul',class_ = 'ProductList_productList__list__3-dGs')
    li_elements = ul_elements.find_all('li',class_= "ProductList_productList__item__1EIvq")
    urls = []
    for link in li_elements:
        try:
            element = link.find('a',class_ =  'Link_link__1AZfr ProductCard_card__img_link__2bBqA')
            url =  "https://www.traderjoes.com"+ element.get('href')
            urls.append(url)
        except Exception as e:
            print(f"Error processing element: {e}")
            continue

    return urls

def click_next_page(driver):
    try:
        driver.execute_script("window.scrollBy(0, 1000);")
        wait = WebDriverWait(driver, 10)
        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.Pagination_pagination__arrow__3TJf0.Pagination_pagination__arrow_side_right__9YUGr')))
        # Scroll to the next button
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)

        # Simulate click with JavaScript
        driver.execute_script("arguments[0].click();", next_button)

        time.sleep(2)  # Optional: Wait for 2 seconds after clicking
        driver.refresh()  # Re
        time.sleep(2)
        print("Clicked the next page button",driver)
        return driver
    except Exception as e:
        print(f"Error clicking the next page button: {e}")
        
def url_specific_project_details(url):
    
    project_detail = {}
    driver  = selenium_driver(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    div = soup.find('div',class_="ProductDetails_main__2d9Xq")
    project_detail["title"] = div.find('h1',class_ = "ProductDetails_main__title__14Cnm").text
    lowercase_string = project_detail["title"].lower()
    project_detail["product_id"] = re.sub(r'[ -]+', '-', lowercase_string)
    img_div = div.find("div",class_ = "slick-slide slick-active slick-current")
    project_detail["image"] = img_div.find('img').get('src')
    price_div = div.find("div",class_= "ProductPrice_productPrice__1Rq1r")
    project_detail["price"] = price_div.find("span",class_= "ProductPrice_productPrice__price__3-50j").text
    project_detail["sale_prices"] = [project_detail["price"]]
    project_detail["prices"] = [project_detail["price"]]
    img_divs = div.find("div",class_ = "slick-track")
    img_tags = img_divs.find_all('img')
    project_detail["images"] = [img['src'] for img in img_tags if '.jpeg' in img['src'] or '.jpg' in img['src']]
    project_detail["url"] = url
    project_detail["brand"] = "Trader Joe's",
    description_div = div.find("div",class_="ProductDetails_main__description__2R7nN")
    description_p = description_div.find_all('p')
    project_detail["description"] = ' '.join([para.get_text() for para in description_p])
    project_detail["models"] = []
    print("Complete scraper for these url ",url)
    driver.close()
    
    return project_detail

def convert_list_to_json(data_list):
    # Define the output file path
    output_file = 'output/trader_joe.json'

    # Extract the fieldnames from the first dictionary (assuming all dictionaries have the same keys)
    with open(output_file, 'w') as f:
        json.dump(data_list, f, indent=4)
        
        
def main():
    try:
        project_details = []
        product_urls = []
        base_url = "https://www.traderjoes.com/home/products/category/products-2"
        driver = selenium_driver(base_url)
        product_url = scrape_product_urls(driver)
        for i in range(0,10):
            if product_url:
                product_urls.extend(product_url)
            driver = click_next_page(driver)
        for url in product_urls:
            project_detail = url_specific_project_details(url)
            project_details.append(project_detail)
        convert_list_to_json(project_details)
            
    except Exception as e:
        raise e 

if __name__ == "__main__":
    main()