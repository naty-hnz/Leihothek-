from app import app
from models import db, Items

with app.app_context():    
    item = Items("Schlosserhammer", None, 750, None, None)

    db.session.add(item)
    db.session.commit()

print("item added")