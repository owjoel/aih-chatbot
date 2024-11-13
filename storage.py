import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date

cred = credentials.Certificate(r"./chatbot-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def set_user(username: str, thread_id: str):
    doc_ref = db.collection('users').document(username)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({'thread_id': thread_id})
    else:
        doc_ref.set({ 'thread_id': thread_id, 'demo': "general user", 'vibe': "any" })

def update_demographic(username: str, demo: str) -> None:
    doc_ref = db.collection('users').document(username)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({'demo': demo})
    else:
        doc_ref.set({ 'demo': demo, 'vibe': "any" }) 

def update_vibe(username: str, vibe: str) -> None:
    doc_ref = db.collection('users').document(username)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({'vibe': vibe})
    else:
        doc_ref.set({ 'vibe': vibe, 'demo': "general user" })    


def get_user(username: str):
    doc_ref = db.collection('users').document(username)
    doc = doc_ref.get()
    if doc.exists:
        dates = doc.to_dict().get('dates', [])
        today = str(date.today())
        if today not in dates:
            dates.append(today)
        doc_ref.update({ 'access': firestore.Increment(1), 'dates': dates })
        data = doc.to_dict()
        data['username'] = doc.id
        return data
    else:
        return None