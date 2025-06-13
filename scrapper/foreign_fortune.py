import requests
from bs4 import BeautifulSoup
import math
import re
import json
from collections import defaultdict
from validation import Validation

def scrape_foreign_fortune_urls(base_url):
    # Send a GET request to the website
    response = requests.get(base_url)
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    nav = soup.find(class_="small--hide border-bottom")
    if nav:
        ul = nav.find('ul', id='SiteNav')
        if ul:
            links = ul.find_all('a', class_='site-nav__link site-nav__link--main')
            # Extract all relevant urls
            urls = []
            for link in links:
                url = link.get('href')
                if url:
                    # Convert relative URLs to absolute URLs if necessary
                    if url.startswith('/'):
                        url = 'https://foreignfortune.com' + url
                    urls.append(url)
                    
    return urls 

def scrape_specific_ur(url):
    
    # Send a GET request to the website
    response = requests.get(url)
    project_details = []
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    product_count = soup.find(class_ = 'filters-toolbar__product-count').text.split()[0]
    if product_count is not None:
        pages = math.ceil(int(product_count) / 8)
        # Scrape each page
        for page in range(1, pages + 1):
            page_url = f"{url}?page={page}"
            links  = scrape_page_links(page_url)
            for link in links:
                product_url = 'https://foreignfortune.com' + link
                product_detail = scrape_product(product_url)
                project_details.append(product_detail)
    errors = validation(project_details)
    if errors is not None:
        print(errors)
    return project_details


def scrape_page_links(page_url):
    # Send a GET request to the website
    response = requests.get(page_url)
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find all <a> elements with class 'hprelink' and extract their href attributes
    links = [link.get('href') for link in soup.find_all('a', class_='product-card__link')]
    
    return links
# Run the scraper

def scrape_product(url):
    
    # Send a GET request to the website
    response = requests.get(url)
    product_details = {}
    images_list = []
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find  <script> elements
    body = soup.find('body', class_ = "template-product")
    product_details["title"] = body.find(class_ = "product-single__title").text
    # Step 1: Convert the string to lowercase
    lowercase_string = product_details["title"].lower()

    # Step 2: Replace spaces and hyphens with a single hyphen
    # This can be done using a regular expression to handle both spaces and hyphens
    product_details["product_id"] = re.sub(r'[ -]+', '-', lowercase_string)
    image_div = body.find(class_ = "product-single__photo js-zoom-enabled product-single__photo--has-thumbnails")
    if image_div is None :
        image_div = body.find(class_ = "product-single__photo js-zoom-enabled")
    product_details["image"] = image_div.find('img').get('src')
    price = body.find('span',id= "ProductPrice-product-template").text
    product_details["price"] = price.split("$")[1].strip()
    product_details["description"] = body.find('div',class_ = "product-single__description rte").text.strip()
    product_details["sale_prices"] = [product_details["price"]]
    product_details["prices"] = [product_details["price"]]
    image_divs = body.find_all('div',class_= "product-single__photo-wrapper js")
    for images_div in image_divs:
        image = images_div.find('img').get('src')
        images_list.append(image)
    
    product_details["images"] = images_list
    product_details["brand"] = "Foreign Fortune Clothing"
    product_details["url"] = url
    product_details["models"] = product_variant_details(body, product_details["image"])
    
    
    return product_details
        
def product_variant_details(body, image):
    script = body.find('script', text=lambda t: t and 'window.KlarnaThemeGlobals.productVariants' in t)
    script = script.string
    
    # # Use regex to find the productVariants array
    match = re.search(r'productVariants\s*=\s*(\[{.*}\])', script, re.DOTALL)
    if match:
        # Extract the array string
        variants_string = match.group(1)
        
        # Replace single quotes with double quotes for valid JSON
        variants_string = variants_string.replace("'", '"')
        
        # Parse the JSON data
        variants_list = json.loads(variants_string)
        selection_dict = selection_product_option(body)
        models = variant_model(variants_list,selection_dict,image)
        return models

def selection_product_option(body):
    form = body.find('form',class_ = "product-form product-form-product-template")
    select_divs = form.find_all('div')
    selection_dict = {}
    if len(select_divs) > 1:
        for div in select_divs:
            # Extract the label text
            label = div.find('label')
            if label:
                    label_text =label.text.strip().lower()

            # Extract the data-index value
            select_element = div.select_one('select')
            if select_element :
                    data_index = select_element['data-index']
            selection_dict[label_text] = data_index
    return selection_dict
    
def variant_model(variants_list,selection_dict,image):
    model = []
    models = []
    if selection_dict is not None:
        color_value = selection_dict.get('color')
        if color_value:
            color_option = selection_dict['color']
        size_value = selection_dict.get('size')
        if size_value:
            size = selection_dict['size']
        style_value = selection_dict.get('style')
        if style_value:
            style = selection_dict['style']
        for values in variants_list:
            variant_dict = {}
            if color_value: 
                variant_dict["color"] = values[color_option]
            else :
                variant_dict["color"] = ""
            variant = {
                "id" : values["id"],
                "price": values["price"]/100,
                "image" : image,
            }
            if size_value :
                variant['size'] = values[size]
            if style_value :
                variant['style'] = values[style]
            variant_dict["variant"] = variant
            model.append(variant_dict)
        color_groups = defaultdict(list)
        for item in model:
            color = item['color']
            variant = item['variant']
            color_groups[color].append(variant)

        # Create the output structure
        for color, variants in color_groups.items():
            models.append({
                "color": color,
                "variant": variants if len(variants) > 1 else variants[0]
            })
    return models

def convert_list_to_json(data_list):
    # Define the output file path
    output_file = 'output/foreign_fortune.json'

    # Extract the fieldnames from the first dictionary (assuming all dictionaries have the same keys)
    with open(output_file, 'w') as f:
        json.dump(data_list, f, indent=4)
        
def validation(product_data):
    validator = Validation(product_data)
    validation_errors = validator.validate()
    return validation_errors

def main():
    try:
        project_details = []
        base_url = "https://foreignfortune.com/"
        urls = scrape_foreign_fortune_urls(base_url)
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