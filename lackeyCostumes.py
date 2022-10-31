from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("./goodkid-c4583-firebase-adminsdk-7k70g-960f6b05c5.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

event_document =  db.collection(u'discordEvents').document(u'lackeyClosets')
users_collection = event_document.collection('users')
item_collection = event_document.collection('items')

positions = {
    "wings": "back",
    "ears": "front"
}

def addToCloset(userId, key, value):
    user_ref = users_collection.document(userId)
    user_closet = getUserCloset(userId)

    if not value in user_closet[key]:
        user_closet[key].append(value)
        user_ref.set(user_closet)

def getUserCloset(userId):
    user_ref = users_collection.document(userId)
    user_record = user_ref.get()

    if not user_record.exists:
        user_ref.set({
            'masks': [],
            'accessories': [],
            'backgrounds': [],
            'paints': ['paint_none']
        })
        user_record = user_ref.get()
    
    return user_record.to_dict()

def getClosetDict():
    item_collection_snapshot = item_collection.get()
    item_data = {}

    for document_snapshot in item_collection_snapshot:
        item_data[document_snapshot.id] = document_snapshot.to_dict()

    return item_data

def generateLackey(userId, params):
    # Params will look like:
    # PARAMS {
    #   hats: [],
    #   accessories: [],
    #   background: "BG",
    #   paint: "PAINT"
    # }

    images = []

    if "backgrounds" in params.keys():
        background = params["backgrounds"][0]
        images.append(f"bg_{background}.png")

    if "paints" in params.keys():
        paint = params["paints"][0]
        images.append(f"{paint}.png")
    else:
        images.append("paint_none.png")

    if "masks" in params.keys():
        mask = params["masks"][0]
        images.append(f"mask_{mask}.png")

    if "accessories" in params.keys():
        for accessory in params["accessories"]:
            if accessory in positions.keys() and positions[accessory]=="back":
                images.insert(1, f"acc_{accessory}.png")
            else:
                images.append(f"acc_{accessory}.png")

    for i, imageName in enumerate(images):
        images[i] = Image.open(f"lackeyImgs/{imageName}")
        if i>0:
            images[0].paste(images[i], (0, 0), images[i])

    return images[0]