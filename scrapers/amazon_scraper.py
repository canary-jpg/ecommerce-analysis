import requests
from bs4 import BeautifulSoup
import pandas as pd 
from datetime import datetime
import time
import random

class AmazonScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept-Language': 'en-US, en;q=0.9'
        }

    def search_products(self, search_term, max_pages=3):
        """Search for products on Amazon """
        all_products = []

        for page in range(1, max_pages + 1):
            print(f"Scraping page {page} for '{search_term}'...")
            url = f"https://www.amazon.com/s?k={search_term.replace(' ', '+')}&page={page}"

            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')

                #find product cards
                products = soup.find_all('div', {'data-component-type': 's-search-result'})

                for product in products:
                    try:
                        title = None
                        title_selectors = [
                            ('h2', 'a-size-mini'),
                            ('h2', 'a-size-medium'),
                            ('span', 'a-size-medium'),
                            ('span', 'a-size=base-plus')
                        ]
                        for tag, class_name in title_selectors:
                            title_elem = product.find('h2', {'class': 'a-size-mini'})
                            if title_elem:
                                link = title_elem.find('a')
                                if link:
                                    title = link.text.strip()
                                else:
                                    title = title_elem.strip()
                                break
                        if not title or title == 'N/A':
                            any_link = product.find('a', {'class': 'a-link-normal'})
                            if any_link:
                                title = any_link.get('aria-label', any_link.strip())
                        #title = title_elem.text.strip() if title_elem else 'N/A'

                        #get ASIN (Amazon product ID)
                        asin = product.get('data-asin', 'N/A')

                        #price
                        price = None
                        price_whole = product.find('span', {'class': 'a-price-whole'})
                        if price_whole:
                            price_fraction = product.find('span', {'class': 'a-price_fraction'})
                            price_text = price_whole.replace(',', '').replace('$', '').strip()
                            if price_fraction:
                                price_text += price_fraction.text.strip()
                            try:
                                price = float(price_text)
                            except:
                                pass
                        # price_elem = product.find('span', {'class': 'a-price-whole'})
                        # price = price_elem.text.replace(',', '').replace('$', '').strip() if price_elem else None


                        #rating
                        rating = None
                        rating_elem = product.find('span', {'class': 'a-icon-alt'})
                        if rating_elem:
                            rating_text = rating_elem.text.split()[0]
                            try:
                                rating = float(rating_text)
                            except:
                                pass
                        #rating = rating_elem.text.split()[0] if rating_elem else None

                        #review count
                        reviews = None
                        review_elem = product.find('span', {'class': 'a-size-base', 'dir': 'auto'})
                        if review_elem:
                            review_text = review_elem.text.replace(',', '').strip()
                            try:
                                reviews = int(review_text)
                            except:
                                pass
                        # reviews = review_elem.text.replace(',', '') if review_elem else None

                        if title and title != 'N/A' and asin != 'N/A':
            

                            all_products.append({
                            'asin': asin,
                            'title': title,
                            'price': float(price) if price else None,
                            'rating': float(rating) if rating else None,
                            'review_count': int(reviews) if reviews and reviews.isdigit() else None,
                            'search_term': search_term,
                            'scraped_at': datetime.now(),
                            'source': 'amazon'
                        })
                    except Exception as e:
                        print(f"Error parsing product: {e}")
                    #random delay
                    time.sleep(random.uniform(2, 4))
            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                continue
        return pd.DataFrame(all_products)


#test it
if __name__ == "__main__":
    scraper = AmazonScraper()

    #search for laptops
    products = scraper.search_products("laptop", max_pages=2)

    print(f"\nScraped {len(products)} products")
    print(products.head())

    #save to CSV
    products.to_csv('../data/amazon_laptops.csv', index=False)
    print("\nData saved to data/amazon_laptops.csv")
