import requests as rq
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import re
from datetime import datetime as dt,timedelta

start_time=( dt.now() + timedelta(days=2))
end_time= (start_time + timedelta(days=2))
start_time_str=start_time.strftime("%m%d%Y")
end_time_str = end_time.strftime("%m%d%Y")
# Envoi d'une requête HTTP GET à l'URL
url = "https://turo.com/fr/fr/search?country=FR&defaultZoomLevel=7&deliveryLocationType=city&endDate=%s&endTime=10:00&isMapSearch=false&itemsPerPage=200&latitude=48.8499198&location=Île-de-France, France&locationType=CITY&longitude=2.637041100000033&pickupType=ALL&placeId=ChIJF4ymA8Th5UcRcCWLaMOCCwE&region=IDF&sortType=RELEVANCE&startDate=%s&startTime=10:00&useDefaultMaximumDistance=true" % (end_time_str,start_time_str)

last_element_attr = 0
df = pd.DataFrame()
# Configuration des options de Selenium pour utiliser Chrome en mode headless
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

driver.get(url)

# Attendre 5 secondes
wait = WebDriverWait(driver, 2)
cookie_dialog_button = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".osano-cm-denyAll"))
)

# Cliquez sur le bouton pour refuser les cookiesf
cookie_dialog_button.click()


driver.execute_script("document.body.style.zoom='10%'")

time.sleep(13) 
def open_tab(url):
    driver.execute_script("window.open('', '_blank');")
    # Passez au nouvel onglet
    driver.switch_to.window(driver.window_handles[-1])
    # Chargez une nouvelle page dans le nouvel onglet
    driver.get(url)

def extract_car_data(car_div):
    # Extraire les données de chaque voiture
    try:
        title = car_div.find(
            "div", class_="css-19qbs56").get_text(strip=True)
    except AttributeError:
        title = None

    try:
        rating = car_div.find(
            "div", class_="css-rs6pyf-StarRatingNumeric-Container"
        ).get_text(strip=True)
    except AttributeError:
        rating = None

    try:
        location = car_div.find(
            "div", class_="css-1cpdnh4").get_text(strip=True)
    except AttributeError:
        location = None

    try:
        price_info = car_div.find(
            "div", class_=lambda value: value and "StyledTotalPriceContainer" in value
        ).get_text(strip=True)
    except AttributeError:
        price_info = None

    try:
        oldPrice = car_div.find(
            "span", class_=lambda value : value and "TotalPrice" in value
        ).get_text(strip=True)
    except AttributeError:
        oldPrice = None

    try:
        savings = car_div.find(
            "p", class_=lambda value : value and "StyledDiscountContainer" in value
        ).get_text(strip=True)
    except AttributeError:
        savings = None
    try:
        travel = car_div.find(
            "p", class_="css-13f4zwe-StyledText").get_text(strip=True)
    except AttributeError:
        travel = None
    try:
        illimKilometer = car_div.find(
            "div", class_="css-bud6ck").get_text(strip=True)
    except AttributeError:
        illimKilometer = None
    try:
        newCar = car_div.find(
            "p", class_="css-xw8x7t-StyledText").get_text(strip=True)
    except AttributeError:
        newCar = None
    first_page_data = {
        "title": title,
        "rating": rating,
        "location": location,
        "price_nfo": price_info,
        "savings": savings,
        "price_without_savings": oldPrice,
        "new_car": newCar,
        "illimted_kilometer": illimKilometer,
        "travels": travel,
    }
    
    # On navige vers la seconde page
    link_elements = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="vehicle-card-link-box"]')

    # Créez une liste pour stocker les liens correspondants
    matching_links = []
    url_detail_list=[]
    # Parcourez les éléments de lien et extrayez les liens
    for link_element in link_elements:
        href = link_element.get_attribute("href")
        if "fr/fr/location-voiture/france" in href:
            matching_links.append(href)
            href_list=str.split(href,"/")
            car_detail={
                "city":href_list[7],
                "brand":href_list[8],
                "detail":href_list[8],
                "user_id":href_list[7]
            }
            url_detail_list.append(car_detail)

    
    second_page_list=[]
    for link in matching_links:
        open_tab(link)
        driver.execute_script("document.body.style.zoom='10%'")

        elmt_html_content = driver.page_source
        elmt_soup = BeautifulSoup(elmt_html_content, "html.parser")

        # click sur le boutton plus pour afficher plus d'informations.
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"seo-pages-hz5ix3-Button-ShowHideButton"))).click()
        
        info_car_owner = elmt_soup.find("div",class_= lambda value : value and "seo-pages-1hmh62h-StyledLineContainer eysspk24" in value).get_text(strip=True)
        conso = elmt_soup.find("div",class_= lambda value : value and "seo-pages-1ic17ug e1qbwl5e0" in value).get_text(strip=True)
        caracteristic = elmt_soup.find("div",attrs={"data-test-id": "first-column"}).get_text(strip=True)
        stars_detail = elmt_soup.find("div",class_= lambda value : value and "seo-pages-ayxcfu e1ax19fq0" in value).get_text(strip=True)
        mileage_include= elmt_soup.find("div",class_= lambda value : value and "seo-pages-152f43h-StyledText" in value).get_text(strip=True)
        cancel= elmt_soup.find("div",class_= lambda value : value and "seo-pages-7fzymt-StyledText" in value).get_text(strip=True)

        second_page_data = {
        "info_car_owner": info_car_owner,
        "conso": conso,
        "caracteristic": caracteristic,
        "stars_detail": stars_detail,
        "mileage_include": mileage_include,
        "cancel": cancel
        }
        second_page_list.append(second_page_data)
        print(second_page_data)
        # Fermez l'onglet actif
        driver.close()

    return first_page_data


def parse_html_to_df(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    car_listings = soup.find_all(
        "div", attrs={"data-testid": "SearchResultWrapper"})

    cars_data = [extract_car_data(car) for car in car_listings]
    return pd.DataFrame(cars_data)


# Exemple d'utilisation

def get_data():
    global last_element_attr
    global df
    while last_element_attr >= 0:
        # Récupérer le HTML de la page après le chargement du JavaScript
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        df = pd.concat([df, parse_html_to_df(html_content)], ignore_index=True)

        # on recupere le dernier élement sur lequelle on effectue un scroll.
        balises = soup.find_all(attrs={"data-index": True})
        # Tant que on a un data-index supérieur au précédent on afffecte la nouvelle valeur a data index.
        new_last_element_attr = int(balises[-1].get("data-index"))
        if new_last_element_attr > last_element_attr:
            last_element_attr = new_last_element_attr
            selector = f'[data-index="{str(last_element_attr)}"]'
            element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )

            # Défiler jusqu'à l'élément
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
        
        else:
            last_element_attr = -1

        print(df)


print(last_element_attr)
get_data()
df.drop_duplicates(inplace=True)
df.to_csv(f"export_location_voiture{start_time_str}.csv",index=False)

# Fermer le navigateur
driver.quit()
