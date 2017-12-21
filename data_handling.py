from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

# for restaurant in session.query(MenuItem).all():
#     print(restaurant.name)

urban_veggie_burger = session.query(MenuItem).filter_by(id=9).one()

urban_veggie_burger.price = '$2.99'
session.add(urban_veggie_burger)
session.commit()

urban_veggie_burger = session.query(MenuItem).filter_by(name='Veggie Burger').one()

print(urban_veggie_burger.name)
print(urban_veggie_burger.price)
