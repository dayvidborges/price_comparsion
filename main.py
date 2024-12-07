import requests
import pandas as pd
from bs4 import BeautifulSoup 
import re

pd.set_option('display.max_rows', None) 
pd.set_option('display.max_columns', None)

cols = []
tables = pd.read_html("products_list.html")
df = tables[0]
cols = [item[-2] for item in df.columns]
df.columns = cols

def clear_string(string):
    pattern = r"\(.*\)"
    return re.sub(pattern, "", string)


products = [clear_string(product).replace("  ", " ").strip() for product in df["DESCRIPCION DEL PRODUCTO"].tolist() if type(product) == str and "total" not in product.lower() and "todos" not in product.lower()]



for product in products:
    print(product)
    
    URL_TEMPLATE = "https://www.comprasparaguai.com.br/busca/?q={QUERY}"


products_data = [] 


for index, product in enumerate(products):
    response = requests.get(URL_TEMPLATE.format(QUERY=product.replace(" ", "+")))
    product_data = {}

    if index == 0:
        product_data["has_prime"] = True
    
    product_data["query"] = product
    product_data["status_code"] = response.status_code
    if response.status_code == 200:  
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.select("div.promocao-item-preco-oferta.flex.column a")
        price_box = soup.select_one(".preco-dolar strong")
        if price_box:
            product_data["price"] = price_box.text.strip()
        else:
            price_box = soup.select_one(".price-model strong")
            if price_box:
                product_data["price"] = price_box.text.strip()
            else:
                product_data["price"] = ""
        product_data["items"] = items
        product_data["items_count"] = len(items)
        for item in items:
            if item.select_one("button"):
                href = item.get("href")  
                if href:  
                    product_data["link"] = href
                    break
                else:
                    product_data["link"] = None
            else:
                href = item.get("href")  
                if href:  
                    product_data["link"] = href
                product_data["link"] = href
                print(f"Erro ao buscar o produto '{product}': {response.status_code}")
                
        products_data.append(product_data)
    else:
        print(f"Erro ao buscar o produto '{product}': {response.status_code}")


BASE_URL = "https://www.comprasparaguai.com.br"

for index, data in enumerate(products_data):
    print("="*100)
    try:
        if data["link"]:
            print(BASE_URL + data["link"])
            response = requests.get(BASE_URL + data["link"])
            soup = BeautifulSoup(response.text, "lxml")
            listed_items = soup.select(".promocao-produtos-item")
            for item in listed_items:
                store = item.select_one("img.lozad.store-image").get("alt").lower().strip().replace(" ", "_")
                price = item.select_one(".promocao-item-preco-oferta.flex.column strong").text.strip()
                products_data[index][f"{store}_name"] = store
                products_data[index][f"{store}_price"] = price
                store_link = item.select_one(".btn.btn-blue.btn-store-redirect").get("href")
                print(data["query"])
                print(store, price)
                print(store_link)
                # if store_link:
                #     products_data[index][f"{store}_link"] = store_link
                # else:
                #     products_data[index][f"{store}_link"] = None
                
    except Exception as e:
        continue
    
    print("="*100)
    


df = pd.DataFrame(products_data)
df.drop(columns=["items", "items_count", "link", "status_code", "has_prime"], inplace=True)
df.to_csv("products_data1.csv", index=False)