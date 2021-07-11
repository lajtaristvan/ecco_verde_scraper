import requests
import re
import random
import pandas as pd
from bs4 import BeautifulSoup
from math import ceil
from tqdm import tqdm
from user_agents import user_agent_list


class EccoVerdeScraper():

    def __init__(self, url):
        self.url = url    


    def scraper(self):
        # Pick a random uer agent
        user_agent = random.choice(user_agent_list.user_agent_list)

        # Set the headers
        headers = {
            'User-Agent': user_agent
        }

        # Define the base url
        baseurl = 'https://www.ecco-verde.co.uk'

        # This is the session
        s = requests.Session()

        # Make a request in a session
        r = s.get(self.url, headers=headers)

        # Scrape the content to end page
        soup = BeautifulSoup(r.content, 'lxml')

        # Scrape the end page number
        try:
            end_page_number = int(soup.find('strong', {'id': 'prTotal'}).string.strip())
        except:
            end_page_number = 'no end page'

        # Define the sum page number
        sum_page_number = 30
       
        # Define the end page number
        try:
            end_page = ceil((end_page_number / sum_page_number) + 1)
        except:
            end_page = 0 

        # print(end_page_number)
        # print(sum_page_number)
        # print(end_page)

        # A list to productlinks
        productlinks = []

        # Iterate all productlinks between a range
        for x in range(1, end_page):

            # Make a request in a session                  
            r = s.get(self.url + f'?page={x}')

            # Scrape the content
            soup = BeautifulSoup(r.content, 'lxml')

            # Identify all products
            productlist = soup.find_all('div', class_='product__title')

            # Save all links in productlinks list
            for item in productlist:
                for link in item.find_all('a', href=True):
                    productlinks.append(baseurl + link['href'])
                    #print(baseurl + link['href'])

        # A list to the scraping data
        list = []

        # Iterate all links in productlinks
        for link in tqdm(productlinks):

            # Make requests with headers in one sessions (s)
            r = s.get(link, headers=headers)

            # Scrape the content in the soup variable with 'lxml' parser
            soup = BeautifulSoup(r.content, 'lxml')

            # Scrape name
            try:
                name = str(soup.title.string.strip()[:-25])
            except:
                name = ''

            # Scrape barcode
            try:
                barcode = str(soup.find('span', {'id': 'itemSKU'}).text.strip())
            except:
                barcode = ''

            # Scrape pack size
            pack_size = 1

            # Scrape gross unit price and origi price 
            try:
                try:
                    gross_unit_price_origi_price = float(soup.find('li', class_='main-price').find('span', class_='price instead-price').text.strip()[1:])
                except:
                    gross_unit_price_origi_price = float(soup.find('li', class_='main-price').find('span', class_='price').text.strip()[1:])
            except:
                gross_unit_price_origi_price = float()

            # Scrape VAT 
            try:
                vat = int(soup.find('p', class_='note').find('span', class_='js-vatText').text.strip()[21:-6])
            except:
                vat = int()

            # Define netto unit price and origi price
            netto_unit_price_origi_price = float(round(gross_unit_price_origi_price / (1 + (vat / 100)), ndigits=2))

            # Discount price
            try:
                discount_price = float(soup.find('li', class_='main-price').find('span', class_='price reduced-price ga-price').text.strip()[1:])                
            except:
                discount_price = ''

            # Quantity discount tier 1
            try:
                quantity_discount_tier_1 = int(soup.find('li', class_='bulk-price').find_all('strong')[0].text.strip()[5:])
            except:
                quantity_discount_tier_1 = ''

            # Quantity discount tier 1 price
            try:
                quantity_discount_tier_1_price = float(soup.find('li', class_='bulk-price').find_all('span', class_='price reduced-price')[0].text.strip()[1:])                
            except:
                quantity_discount_tier_1_price = ''

            # Quantity discount tier 2
            try:
                quantity_discount_tier_2 = int(soup.find('li', class_='bulk-price').find_all('strong')[1].text.strip()[5:])
            except:
                quantity_discount_tier_2 = ''

            # Quantity discount tier 2 price
            try:
                quantity_discount_tier_2_price = float(soup.find('li', class_='bulk-price').find_all('span', class_='price reduced-price')[1].text.strip()[1:])                
            except:
                quantity_discount_tier_2_price = ''            

            # Scrape product code
            try:                
                product_code = str(soup.find('span', {'id': 'itemNo'}).text.strip())
            except:
                product_code = ''

            # Scrape availability
            try:
                availability = bool(soup.find('p', class_='stock-state available').text.strip())
            except:
                availability = False

            # Define a dictionary for csv
            ecco_verde = {                 
                'link': link,
                'name': name,
                'barcode': barcode,
                'pack_size': pack_size,
                'netto_unit_price_origi_price': netto_unit_price_origi_price,                
                'gross_unit_price_origi_price': gross_unit_price_origi_price,
                'vat': vat,                
                'discount_price': discount_price,
                'quantity_discount_tier_1': quantity_discount_tier_1,
                'quantity_discount_tier_1_price': quantity_discount_tier_1_price,
                'quantity_discount_tier_2': quantity_discount_tier_2,
                'quantity_discount_tier_2_price': quantity_discount_tier_2_price,                
                'product_code': product_code,        
                'availability': availability
            }

            # Add the dictionary to the list every iteration
            list.append(ecco_verde)

            # Print every iteration        
            # print(
            #     '\n--------- Saving: ---------\n'             
            #     'link: ' + str(ecco_verde['link']) + '\n'
            #     'name: ' + str(ecco_verde['name']) + '\n'
            #     'barcode: ' + str(ecco_verde['barcode']) + '\n'
            #     'pack size: ' + str(ecco_verde['pack_size']) + '\n'
            #     'netto unit price origi price: ' + str(ecco_verde['netto_unit_price_origi_price']) + '\n'                
            #     'gross unit price origi price: ' + str(ecco_verde['gross_unit_price_origi_price']) + '\n'
            #     'vat: ' + str(ecco_verde['vat']) + '\n'                
            #     'discount price: ' + str(ecco_verde['discount_price']) + '\n'
            #     'quantity discount tier 1: ' + str(ecco_verde['quantity_discount_tier_1']) + '\n'
            #     'quantity discount tier 1 price: ' + str(ecco_verde['quantity_discount_tier_1_price']) + '\n'       
            #     'quantity discount tier 2: ' + str(ecco_verde['quantity_discount_tier_2']) + '\n' 
            #     'quantity discount tier 2 price: ' + str(ecco_verde['quantity_discount_tier_2_price']) + '\n'            
            #     'product code: ' + str(ecco_verde['product_code']) + '\n'
            #     'availability: ' + str(ecco_verde['availability']) + '\n'
            # )

        # Make table to list
        df = pd.DataFrame(list)

        # Save to csv      
        df.to_csv(r'C:\WEBDEV\ecco_verde_scraper\exports\ecco_verde.csv', mode='a', index=False, header=True)


get_ecco_verde_face = EccoVerdeScraper('https://www.ecco-verde.co.uk/face')
get_ecco_verde_make_up = EccoVerdeScraper('https://www.ecco-verde.co.uk/natural-makeup')
get_ecco_verde_body = EccoVerdeScraper('https://www.ecco-verde.co.uk/body')
get_ecco_verde_hair = EccoVerdeScraper('https://www.ecco-verde.co.uk/hair')
get_ecco_verde_man = EccoVerdeScraper('https://www.ecco-verde.co.uk/for-men')
get_ecco_verde_babies_kids = EccoVerdeScraper('https://www.ecco-verde.co.uk/babies-kids-1')
get_ecco_verde_accessories = EccoVerdeScraper('https://www.ecco-verde.co.uk/accessories-1')
get_ecco_verde_offers = EccoVerdeScraper('https://www.ecco-verde.co.uk/special-offers')

get_ecco_verde_face.scraper()
get_ecco_verde_make_up.scraper()
get_ecco_verde_body.scraper()
get_ecco_verde_hair.scraper()
get_ecco_verde_man.scraper()
get_ecco_verde_babies_kids.scraper()
get_ecco_verde_accessories.scraper()
get_ecco_verde_offers.scraper()