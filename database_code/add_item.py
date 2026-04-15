from app import app
from models import db, Items

with app.app_context():
    item1 = Items("Bohrmaschine","boormachine.jpg", 103701245, 500, 400, 600)
    item2 = Items("UNO","uno.jpg", 91141454, 200, 150, 250)

    db.session.add(item1)
    db.session.add(item2)
    db.session.commit()

print("Items toegevoegd!")
