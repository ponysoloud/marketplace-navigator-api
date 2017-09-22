import json
import os

from flask import Flask, request, jsonify, make_response
app = Flask(__name__)

import apilib

UPLOAD_FOLDER = 'images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/signin', methods=['POST'])
def page_sign_in():
	data = json.loads(request.data)
	email = data['email']
	password = data['password']

	result = apilib.sign_in(email, password)
	return jsonify(result)

@app.route('/signup', methods=['POST'])
def page_sign_up_seller():
	data = json.loads(request.data)
	email = data['email']
	password = data['password']
	name = data['name']

	result = apilib.sign_up(email, password)
	return jsonify(result)


##########GET
@app.route('/getAccountInfo', methods=['GET'])
def page_get_info():
	if not 'token' in request.args:
		return jsonify({ 'error' : 'Missing argument' })

	token = request.args['token']
	return jsonify(apilib.get_user_info(token))

@app.route('/getAccountShops', methods=['GET'])
def page_get_shop():
	if not 'token' in request.args:
		return jsonify({ 'error' : 'Missing argument' })

	token = request.args['token']
	return jsonify(apilib.get_user_shops(token))


###########SET
@app.route('/setAccountInfo', methods=['POST'])
def page_set_info():
	if not 'token' in request.args:
		return jsonify({ 'error' : 'Missing argument' })

	token = request.args['token']

	#upload file
	if 'image' not in request.files:
		print('No file part')
		return jsonify({ 'error': 'Not found \'image\' argument'})

	file = request.files['image']

	if file.filename == '':
		return jsonify({ 'error': 'No selected file'})

	if not (file and allowed_file(file.filename)):
		return jsonify({ 'error': 'Invalid file'})

	f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
	file.save(f)

	#get data arguments
	data = request.form
	name = data['name']

	return jsonify(apilib.set_user_info(token, name, f))


@app.route('/setAccountShop', methods=['POST'])
def page_set_shop():
	if not 'token' in request.args:
		return jsonify({ 'error' : 'Missing argument' })

	token = request.args['token']

	data = json.loads(request.data)
	shopid = data['shopId']
	name = data['name']
	longitude = data['longitude']
	latitude = data['latitude']

	return jsonify(apilib.set_user_shop(token, shopid, name, longitude, latitude))

@app.route('/setAccountShopItem', methods=['POST'])
def page_set_shop_item():
	if not 'token' in request.args:
		return jsonify({ 'error' : 'Missing argument' })

	token = request.args['token']

	#upload file
	if 'image' not in request.files:
		print('No file part')
		return jsonify({ 'error': 'Not found \'image\' argument'})

	print("step@1")
	file = request.files['image']

	if file.filename == '':
		return jsonify({ 'error': 'No selected file'})

	if not (file and allowed_file(file.filename)):
		return jsonify({ 'error': 'Invalid file'})

	print("step@2")
	f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
	print("step@3")
	file.save(f)	

	print("step@4")
	#get data arguments
	data = request.form
	shopid = data['shopId']
	itemid = data['itemId']
	category = data['category']
	gender = data['gender']
	name = data['name']
	price = data['price']

	return jsonify(apilib.set_user_shop_item(token, shopid, itemid, name, category, gender, price, f))


"""
@app.route('/addimg', methods=['POST'])
def add_img():
	if not 'token' in request.args:
		return jsonify({ 'error' : 'Missing argument' })

	token = request.args['token']

	if 'image' not in request.files:
		print('No file part')
		return jsonify({ 'error': 'Not found \'image\' argument'})

	file = request.files['image']

	if file.filename == '':
		return jsonify({ 'error': 'No selected file'})

	if file and allowed_file(file.filename):
		f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
		file.save(f)
		return jsonify(apilib.add_img(token, file.filename))

	return jsonify({ 'error': 'Invalid file'})




@app.route('/shops/<int:shop_id>', methods=['POST'])
def add_item():
	data = json.loads(request.data)
	token = data['idToken']
	del data['idToken']

	return jsonify(mylib.add_user_item(token, data))

@app.route('/setlocation', methods=['POST'])
def set_location():
	data = json.loads(request.data)
	token = data['idToken']
	longitude = data['longitude']
	latitude = data['latitude']
	country = data['country']

	info = {
	'latitude' : latitude,
	'longitude': longitude,
	'country': country
	}
	
	return jsonify(mylib.set_user_location(token, info))

@app.route('/likeitem', methods=['POST'])
def like_item():
	data = json.loads(request.data)
	token = data['idToken']
	host = data['hostId']
	item = data['itemId']


	return jsonify(mylib.like_user_item(token, host, item))

@app.route('/getitems', methods=['POST'])
def get_items():
	data = json.loads(request.data)
	token = data['idToken']
	longitude = data['longitude']
	latitude = data['latitude']
	country = data['country']

	location = [float(latitude), float(longitude), country]

	return jsonify(mylib.get_items_byloc(token, location, []))



"""

