import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(r"./chatbot-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

data = {
    'task': 'wash the dishes',
    'status': 'TODO'
}

def set_user(username: str, thread_id: str):
    doc = db.collection('users').document(username)
    doc.set({ 'thread_id': thread_id })



def get_user(username: str):
    doc_ref = db.collection('users').document(username)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({ 'access': firestore.Increment(1) })
        return doc.to_dict()
    else:
        return None