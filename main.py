from fastapi import FastAPI
import uvicorn
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

app = FastAPI()
cred = credentials.ApplicationDefault()

firebase_admin.initialize_app(cred, {
  'projectId' :  os.environ['project_id_py']
})

db = firestore.client()

@app.get("/")
def main_func():
  return {"desc": "Helloworld"}

#user api
@app.get("/users/{user_id}")
def get_user_firebase(user_id: int):
  return {"user_id": user_id, "desc" : "testing is the right thing", "recommendation": [1231231, 123132123, 12312313]}

#book api; non firebase
@app.get("/books/{book_id}")
def get_book_database(book_id: int):
  return { "book_id": book_id, "desc" : { "title": "bias and references"} }

@app.get("/books/all")
def get_feed_all_firebase():
  return { "book_id": book_id, "desc" : [{"title": "yessir"}, {"title": "yessir"}]}

#feed api; 
@app.post("/feeds")
def post_feed_firebase():
  data = {
    u'title': u'great book',
    u'book': u'thinking in bets ',
    u'description': u'this is coool boook'
  }

  db.collection(u'newsfeed').add(data)

  return {"id": 12313, "desc": "sucesss"}

@app.get("/feeds/{feed_id")
def get_feed_firebase(feed_id: int):
  return { "book_id": feed_id, "desc" : [{"title": "goodbook"}, {"title": "not that good book"}]}

#prediction api
@app.get("/predictions/{book_id}")
def get_book_prediction(book_id: int):
  return {"book_id": book_id, "recommendation" : [ 1231231, 123123, 12312313] }



#others; 

uvicorn.run(app,host="0.0.0.0",port=8080)


