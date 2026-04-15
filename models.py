from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()

class Items(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    image: Mapped[str | None] = mapped_column(nullable=True)
    rfid: Mapped[int | None] = mapped_column(nullable=True)
    weight: Mapped[float | None] = mapped_column(nullable=True)
    weight_min: Mapped[float | None] = mapped_column(nullable=True)
    weight_max: Mapped[float | None] = mapped_column(nullable=True)

    def __init__(self, name, image, rfid, weight, weight_min, weight_max):
        self.name = name
        self.image = image
        self.rfid = rfid
        self.weight = weight
        self.weight_min = weight_min
        self.weight_max = weight_max