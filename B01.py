import requests
from bs4 import BeautifulSoup
import csv

# URL de la page produit à scraper
product_page_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

# Effectuer une requête GET pour récupérer le contenu HTML de la page
response = requests.get(product_page_url)

# Vérifier si la requête est réussie
if response.status_code != 200:
    print(f"Erreur: Impossible de récupérer la page. Code d'état: {response.status_code}")
    exit()
soup = BeautifulSoup(response.content, 'html.parser')

# Extraire les informations nécessaires
universal_product_code = soup.find('th', string='UPC').find_next('td').text
title = soup.find('h1').text
price_including_tax = soup.find('th', string='Price (incl. tax)').find_next('td').text
price_excluding_tax = soup.find('th', string='Price (excl. tax)').find_next('td').text
number_available = soup.find('th', string='Availability').find_next('td').text
product_description = soup.find('div', id='product_description').find_next('p').text if soup.find('div', id='product_description') else 'No description available'
category = soup.find('ul', class_='breadcrumb').find_all('li')[2].text.strip()
review_rating = soup.find('p', class_='star-rating')['class'][1]
image_url = "http://books.toscrape.com/" + soup.find('img')['src'].replace('../', '')

# Préparer les données à écrire dans le fichier CSV
data = [{
    'product_page_url': product_page_url,
    'universal_product_code': universal_product_code,
    'title': title,
    'price_including_tax': price_including_tax,
    'price_excluding_tax': price_excluding_tax,
    'number_available': number_available,
    'product_description': product_description,
    'category': category,
    'review_rating': review_rating,
    'image_url': image_url 
}]

# Écrire les données dans un fichier CSV
import os

csv_file = os.path.abspath('e:/2024_Python/BooksOnline/BOBenv/BOBenv/book_data.csv')
csv_columns = [
    'product_page_url', 'universal_product_code', 'title', 'price_including_tax',
    'price_excluding_tax', 'number_available', 'product_description',
    'category', 'review_rating', 'image_url'
]

import os

try:
    with open(csv_file, 'w+', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Données enregistrées dans {csv_file}")
    if os.path.exists(csv_file):
        print(f"Vérification: le fichier CSV a été créé à l'emplacement {csv_file}")
    else:
        print("Erreur: Le fichier CSV n'a pas été créé malgré l'absence d'erreur.")
except IOError as e:
    print(f"Erreur: impossible d'enregistrer les données dans le fichier CSV: {e}")
