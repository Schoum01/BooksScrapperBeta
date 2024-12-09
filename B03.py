import requests
from bs4 import BeautifulSoup
import csv
import os

# URL de la page principale à scraper
base_url = "http://books.toscrape.com/catalogue/category/books/"
site_url = "http://books.toscrape.com/"

# Fonction pour obtenir toutes les catégories disponibles
def get_all_categories():
    response = requests.get(site_url)
    if response.status_code != 200:
        print(f"Erreur: Impossible de récupérer la page principale. Code d'état: {response.status_code}")
        return [] 
    
    soup = BeautifulSoup(response.content, 'html.parser')
    category_links = soup.find('div', class_='side_categories').find_all('a')[1:]
    categories = {link.text.strip(): site_url + link['href'] for link in category_links}
    return categories

# Fonction pour obtenir toutes les pages d'une catégorie
def get_all_product_urls(category_url):
    product_urls = []
    while category_url:
        response = requests.get(category_url)
        if response.status_code != 200:
            print(f"Erreur: Impossible de récupérer la page. Code d'état: {response.status_code}")
            return product_urls
        
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('h3'):
            product_urls.append("http://books.toscrape.com/catalogue/" + link.find('a')['href'].replace('../', ''))
        
        # Pagination: Vérifier s'il y a une page suivante
        next_page = soup.find('li', class_='next')
        if next_page:
            next_page_url = next_page.find('a')['href']
            category_url = category_url.rsplit('/', 1)[0] + '/' + next_page_url
        else:
            category_url = None
    
    return product_urls

# Fonction pour extraire les informations d'un livre
def scrape_book_data(product_page_url):
    response = requests.get(product_page_url)
    if response.status_code != 200:
        print(f"Erreur: Impossible de récupérer la page {product_page_url}. Code d'état: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    universal_product_code = soup.find('th', string='UPC').find_next('td').text
    title = soup.find('h1').text
    price_including_tax = soup.find('th', string='Price (incl. tax)').find_next('td').text
    price_excluding_tax = soup.find('th', string='Price (excl. tax)').find_next('td').text
    number_available = soup.find('th', string='Availability').find_next('td').text
    product_description = soup.find('div', id='product_description').find_next('p').text if soup.find('div', id='product_description') else 'No description available'
    category = soup.find('ul', class_='breadcrumb').find_all('li')[2].text.strip()
    review_rating = soup.find('p', class_='star-rating')['class'][1]
    image_url = site_url + soup.find('img')['src'].replace('../', '')

    return {
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
    }

# Scraper toutes les informations des livres d'une catégorie
def scrape_category(category_name, category_url):
    product_urls = get_all_product_urls(category_url)
    all_data = []
    for url in product_urls:
        book_data = scrape_book_data(url)
        if book_data:
            all_data.append(book_data)
    return all_data

# Récupérer toutes les catégories
categories = get_all_categories()

# Pour chaque catégorie, récupérer les données des livres et les écrire dans un fichier CSV distinct
for category_name, category_url in categories.items():
    all_books_data = scrape_category(category_name, category_url)
    csv_file = os.path.abspath(f'e:/2024_Python/BooksOnline/BOBenv/BOBenv/{category_name.replace(" ", "_").lower()}_books_data.csv')
    csv_columns = [
        'product_page_url', 'universal_product_code', 'title', 'price_including_tax',
        'price_excluding_tax', 'number_available', 'product_description',
        'category', 'review_rating', 'image_url'
    ]

    try:
        with open(csv_file, 'w+', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for row in all_books_data:
                writer.writerow(row)
        print(f"Données enregistrées dans {csv_file}")
        if os.path.exists(csv_file):
            print(f"Vérification: le fichier CSV a été créé à l'emplacement {csv_file}")
        else:
            print("Erreur: Le fichier CSV n'a pas été créé malgré l'absence d'erreur.")
    except IOError as e:
        print(f"Erreur: impossible d'enregistrer les données dans le fichier CSV: {e}")
