import requests
from bs4 import BeautifulSoup
import json
import re
from validation import Validation

def scrape_le_chocolat_urls(base_url):
    # Send a GET request to the website
    response = requests.get(base_url)
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    div = soup.find_all('div',class_="siteMenuItem__wrapper")[1]
    if div:
        li = div.find_all('li', class_='siteMenuItem')
        if li:
            urls = []
            for l in li :
                link = l.find('a', class_='siteMenuItem__link')
                url = link.get('href')
                urls.append(url)
    return urls 

def scrape_specific_ur(url):
    # Send a GET request to the website
    response = requests.get(url)
    product_details = []
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    section = soup.find('section',class_= 'products__list')
    divs = section.find_all('div',class_= 'productMiniature')
    for div in divs:
        product_detail = {}
        product_detail['title'] = div['data-product-name']
        # Convert the string to lowercase
        lowercase_string = product_detail["title"].lower()
        # This can be done using a regular expression to handle both spaces and hyphens
        product_detail["product_id"] = re.sub(r'[ -]+', '-', lowercase_string)
        product_detail["image"] = div.find('img').get('src')
        product_detail["price"] = div.find('span',class_ = "productMiniature__price").text.strip()
        product_detail["sale_prices"] = [product_detail["price"]]
        product_detail["prices"] = [product_detail["price"]]
        product_detail["url"] = div.find('a',class_= "productMiniature__name").get('href')
        product_detail["sale_prices"] = [product_detail["price"]]
        product_detail["prices"] = [product_detail["price"]]
        product_detail["brand"] = "LE CHOCOLAT ALAIN DUCASSE"
        product_detail["models"] = []
        product_detail["description"] = get_project_description(product_detail["url"])
        product_detail["images"] = [product_detail["image"]]
        product_details.append(product_detail)
    errors = validation(product_details)
    print(errors)
    if errors is not None:
        print(errors)
    return product_details

def get_project_description(project_url):
    # Send a GET request to the website
    response = requests.get(project_url)
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    description = soup.find('div',class_= 'productDescription__text').text.strip()
    return description

def convert_list_to_json(data_list):
    # Define the output file path
    output_file = 'output/lechocolat_alainducasse.json'

    # Extract the fieldnames from the first dictionary (assuming all dictionaries have the same keys)
    with open(output_file, 'w') as f:
        json.dump(data_list, f, indent=4)
    print("succesfully created json file")
        
def validation(product_data):
    validator = Validation(product_data)
    validation_errors = validator.validate()
    return validation_errors


def main():
    try:
        project_details = []
        base_url = "https://www.lechocolat-alainducasse.com/uk/"
        urls = scrape_le_chocolat_urls(base_url)
        for url in urls:
            #specific url logic 
            details = scrape_specific_ur(url)
            project_details.append(details)
        projects = [item for sublist in project_details for item in sublist]
        convert_list_to_json(projects)
    except Exception as e:
        raise e 

if __name__ == "__main__":
    main()