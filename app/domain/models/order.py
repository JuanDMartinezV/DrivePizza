from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from app.database import Base
import json

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    client = Column(String(100))
    items = Column(Text)
    total = Column(Float)
    status = Column(String(20), default="pending")

    def set_items(self, items):
        self.items = json.dumps(items)

    def get_items(self):
        return json.loads(self.items) if self.items else []