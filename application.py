from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
application = Flask(__name__)
application.debug=True
application.secret_key='super_secret_key'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('mysql+pymysql://admin:Monk-ey23@restaurantdb-2.cvppggmvkxiq.us-east-1.rds.amazonaws.com:3306/restaurantdb')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


@application.route('/')
@application.route('/restaurants')
def restaurantHome():
	session = DBSession()
	restaurants = session.query(Restaurant).all()
	return render_template('restaurants.html', restaurants=restaurants)

@application.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
	if request.method == 'POST':
		newRestaurant = Restaurant(name = request.form['name'])
		session.add(newRestaurant)
		session.commit()
		flash('New Restaurant Created')
		return redirect(url_for('restaurantHome'))
	else:
		return render_template('newRestaurant.html')
	
@application.route('/restaurant/<int:restaurant_id>/edit', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
	session = DBSession()
	restaurantToEdit = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		if request.form['name']:
			restaurantToEdit.name = request.form['name']
			session.add(restaurantToEdit)
			session.commit()
			flash('Restaurant Successfully Modified')
			return redirect(url_for('restaurantHome'))
	else:
		return render_template('editRestaurant.html', restaurant = restaurantToEdit)
	
	
@application.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	session = DBSession()
	restaurantToDelete = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		session.delete(restaurantToDelete)
		session.commit()
		flash('Restaurant Successfully Deleted')
		return redirect(url_for('restaurantHome'))
	else:
		return render_template('deleteRestaurant.html', restaurant = restaurantToDelete)


@application.route('/')
@application.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
	session = DBSession()
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	appetizers = session.query(MenuItem).filter_by(restaurant_id=restaurant.id, course='Appetizer')
	entrees = session.query(MenuItem).filter_by(restaurant_id=restaurant.id, course='Entree')
	desserts = session.query(MenuItem).filter_by(restaurant_id=restaurant.id, course='Dessert')
	beverages = session.query(MenuItem).filter_by(restaurant_id=restaurant.id, course='Beverage')
	courses = [appetizers, entrees, desserts, beverages]
	headers = ['Appetizers', 'Entrees', 'Desserts', 'Beverages']
	return render_template('menu.html', restaurant=restaurant, courses=courses, headers=headers)

	
@application.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
	if request.method == 'POST':
		newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], course = request.form['course'], restaurant_id = restaurant_id)
		session.add(newItem)
		session.commit()
		flash('New Menu Item Created')
		return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
	else:
		return render_template('newMenuItem.html', restaurant_id=restaurant_id)


@application.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	session = DBSession()
	editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		if request.form['description']:
			editedItem.description = request.form['description']
		if request.form['price']:
			editedItem.price = request.form['price']
		if request.form['course']:
			editedItem.course = request.form['course']
		session.add(editedItem)
		session.commit()
		flash('Menu Item Successfully Edited')
		return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
	else:
		return render_template('editMenuItem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)


@application.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	session = DBSession()
	itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		flash('Menu Item Successfully Deleted')
		return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
	else:
		return render_template('deleteMenuItem.html', item = itemToDelete)
		
@application.route('/restaurants/JSON')
def restaurantJSON():
	restaurants = session.query(Restaurant).all()
	return jsonify(Restaurants=[restaurant.serialize for restaurant in restaurants])		

@application.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
	return jsonify(MenuItems=[i.serialize for i in items])
	
@application.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
	item = session.query(MenuItem).filter_by(restaurant_id=restaurant_id, id=menu_id).one()
	return jsonify(MenuItem=[item.serialize])
	
if __name__ == '__main__':
	application.secret_key = 'super_secret_key'
	application.debug = True
	application.run(host = '0.0.0.0')
