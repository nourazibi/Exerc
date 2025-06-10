import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_text(text):
    return ' '.join(text.strip().split())

def scrape_article(url):
    print(f"Scraping: {url}")
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.content, 'html.parser')

    try:
        title = soup.find('h3', class_='entry-title').text.strip()
        thumbnail = soup.find('meta', property='og:image')['content']
        sub_category_tag = soup.find('span', class_='single-cat')
        sub_category = sub_category_tag.text.strip() if sub_category_tag else None
        summary_tag = soup.find('p', class_='excerpt')
        summary = summary_tag.text.strip() if summary_tag else None
        date_tag = soup.find('time', class_='entry-date')
        date_str = date_tag['datetime'] if date_tag else None
        date_formatted = datetime.strptime(date_str[:10], '%Y-%m-%d').strftime('%Y-%m-%d') if date_str else None
        author_tag = soup.find('span', class_='byline')
        author = author_tag.text.strip() if author_tag else None
        content_section = soup.find('div', class_='entry-content')
        content_paragraphs = content_section.find_all(['p', 'h2', 'h3']) if content_section else []
        content = '\n'.join(clean_text(p.get_text()) for p in content_paragraphs)
        images = {}
        if content_section:
            for img in content_section.find_all('img'):
                src = img.get('src') or img.get('data-src')
                alt = img.get('alt', '').strip()
                if src:
                    images[src] = alt

        article_data = {
            'url': url,
            'title': title,
            'thumbnail': thumbnail,
            'sub_category': sub_category,
            'summary': summary,
            'date': date_formatted,
            'author': author,
            'content': content,
            'images': images
        }

        return article_data

    except Exception as e:
        print(f"Erreur avec l'article {url}: {e}")
        return None

def scrape_homepage_articles():
    base_url = "https://www.blogdumoderateur.com"
    res = requests.get(base_url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.content, 'html.parser')

    # Trouver les articles sur la page d'accueil
    articles = soup.find_all('article')
    urls = []
    for article in articles:
        a_tag = article.find('a', href=True)
        if a_tag:
            urls.append(a_tag['href'])

    all_articles = []
    for url in urls:
        article = scrape_article(url)
        if article:
            all_articles.append(article)

    return all_articles

if __name__ == "__main__":
    articles = scrape_homepage_articles()

    for art in articles:
        print(f"✅ {art['title']} — {art['sub_category']} ({art['date']})")

    with open('articles_bdm.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
