from fastapi import FastAPI
import uvicorn
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from typing import Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from tensorflow import keras
import numpy as np
import pandas as pd

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cred = credentials.ApplicationDefault()
# cred = credentials.Certificate('charaka-kapi.json')
firebase_admin.initialize_app(cred, {
    'projectId':  'charaka'
})

db = firestore.client()


class Feed(BaseModel):
    userid: str
    title: str
    desc: Optional[str] = None
    book_id: Optional[str] = None


@app.get("/")
def main_func():
    return {"desc": "This is Api for charaka deploy in cloud function"}

# user api
# @app.get("/users/{user_id}")
# def get_user_firebase(user_id: str):
#   docs = db.collection(u'users').document(user_id).get()
#   return {"user_id": user_id, "docs": docs }

# book api; non firebase
@app.get("/books/2767052")
def get_book_database():
  docs = {
      "id": 1,
      "book_id": 2767052,
      "best_book_id": 2767052,
      "work_id": 2792775,
      "books_count": 272,
      "isbn": "439023483",
      "isbn13": 9780439023480,
      "authors": "Suzanne Collins",
      "original_publication_year": 2008,
      "original_title": "The Hunger Games",
      "title": "The Hunger Games (The Hunger Games, #1)",
      "language_code": "eng",
      "average_rating": 4.34,
      "ratings_count": 4780653,
      "work_ratings_count": 4942365,
      "work_text_reviews_count": 155254,
      "ratings_1": 66715,
      "ratings_2": 127936,
      "ratings_3": 560092,
      "ratings_4": 1481305,
      "ratings_5": 2706317,
      "image_url": "https://images.gr-assets.com/books/1447303603m/2767052.jpg",
      "small_image_url": "https://images.gr-assets.com/books/1447303603s/2767052.jpg"
  },
  return {"book_id": '2767052', "doc": docs}


@app.get("/books")
def get_feed_all_firebase():
  
  url_books = './books.csv'
  books = pd.read_csv(url_books)
  bb = books.head()
  bi = bb.to_dict('index')
  lit = []
  for key, value in bi.items():
      lit.append(value)

  return {"status": 200, "docs": lit}

# # # feed api; done

@app.post("/feeds")
def post_feed_firebase(feed: Feed):
    data = {
        u'title': feed.title,
        u'description': feed.desc,
        u'user_id': feed.userid,
        u'book_id':  feed.book_id,
    }

    db.collection(u'newsfeed').add(data)
    return {"code": 202, "data": feed}


@app.get("/feeds")
def get_feed_firebase():
    docs = db.collection(u'newsfeed').limit(3).get()
    lis = []
    for doc in docs:
        bookdoc = db.collection(u'books').where(
            u'book_id', u'==', u'25663888').get()
        bookdoc = bookdoc[0]
        # for doc1 in bookdoc:
        # print(f'{doc1.id} => {doc1.to_dict()}')
    lis.append({
        "id": doc.id,
        "doc": doc.to_dict(),
        "bookdoc": bookdoc.to_dict()
    })

    return {"status": 200, "docs": lis}

# @app.get("/feedbyid")
# def get_feed_firebase():
#   # docs = db.collection(u'newsfeed').document(u'4JH3zzZ3ji9QuZp1ThFV').get()
#   # bookdoc = db.collection(u'books').where(u'book_id', u'==', u'25663888').get()
#   # bookdoc = bookdoc[0]


#   return {
#     "status": 200,
#     "docs": docs,
#   # "bookdoc": bookdocss
#   }


# # prediction api
@app.get("/predictions")
def get_book_prediction():

    url_rating = './ratings.csv'
    url_books = './books.csv'
    rating = pd.read_csv(url_rating)

    books = pd.read_csv(url_books)
    book_data = np.array(list(set(rating.book_id)))
    user = np.array([100 for i in range(len(book_data))])
    model = keras.models.load_model('../bangkit-api-backend')
    model.summary()

    predictions = model.predict([[user], [book_data]])
    predictions = np.array([a[0] for a in predictions])
    recommended_book_ids = (-predictions).argsort()[:5]

    bb = books[books['id'].isin(recommended_book_ids)]

    bi = bb.to_dict('index')
    lit = []
    for key, value in bi.items():
        lit.append(value)

    return {
        "status": 200,
        "docs": lit
    }


uvicorn.run(app, host="0.0.0.0", port=8080)
