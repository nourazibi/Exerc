from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['blog_du_moderateur']  # Nom de la base
collection = db['articles']        # Nom de la collection

def save_article_to_mongo(article):
    # On évite les doublons via l'URL
    collection.update_one(
        {'url': article['url']},
        {'$set': article},
        upsert=True
    )
    print(f"✅ Article sauvegardé : {article['title']}")

def save_multiple_articles(articles):
    for article in articles:
        save_article_to_mongo(article)
