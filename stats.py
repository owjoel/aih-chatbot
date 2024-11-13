import pandas
import openpyxl
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(r"./chatbot-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

users = []
admins = ['owjoel', 'jaq_jw', 'e11yn', 'Rey_227', 'charisdavene', 'yyingy']
try:
    users_ref = db.collection('users')
    docs = users_ref.stream()
    users = [{**doc.to_dict(), "id": doc.id} for doc in docs]
except Exception as e:
    print(e)

df = pandas.DataFrame(users)
df = df[~df['id'].isin(admins)]
df['dates'] = df['dates'].apply(lambda x: x if isinstance(x, list) else [])
df['frequency'] = df['dates'].apply(len)

rows_with_frequency_gt_1 = df[df['frequency'] > 1].shape[0]
percentage = (rows_with_frequency_gt_1 / len(df)) * 100
df.to_excel("usage.xlsx",  sheet_name="Users")

print(df)
print(f'% used more than once: {percentage}%')