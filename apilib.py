#import pyre
import os
import requests
import pyre
from math import radians, cos, sin, asin, sqrt
from requests.exceptions import HTTPError

config = {
	"apiKey": "AIzaSyDhoRcbsJdJONg6aDpBYmNwuByH2x8IHKQ",
    "authDomain": "marketplace-navigator.firebaseapp.com",
    "databaseURL": "https://marketplace-navigator.firebaseio.com",
    "projectId": "marketplace-navigator",
    "storageBucket": "marketplace-navigator.appspot.com",
    "messagingSenderId": "599850847305"
  }

firebase = pyre.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

UPLOAD_FOLDER = 'images/'

def add_img(idToken, filename):
	f = os.path.join(UPLOAD_FOLDER, filename)
	storage.child(f).put(f, idToken)
	print(storage.child(f).get_url())

	return { 'status' : 'OK' }

def sign_in(email, password):
	if not (check_if_string([email, password])):
		return { 'error': 'Invalid argument'}

	temp = auth.sign_in_with_email_and_password(email, password)
	#print(temp)
	return temp
	#data = {"name": "ya admin bleat"}
	#db.child("users").child(user['localId']).set(data, user['idToken'])

def sign_up(email, password):
	if not (check_if_string([email, password])):
		return { 'error': 'Invalid argument'}

	temp = auth.create_user_with_email_and_password(email, password)
	#print(temp)
	return temp

def get_uid(idToken):
	res = auth.get_account_info(idToken)
	if not 'users' in res:
		return None
	if len(res['users']) < 1:
		return None
	return res['users'][0]['localId']

def get_user_info(idToken):
	if not (check_if_string([idToken])):
		return { 'error': 'Invalid argument'}

	uid = get_uid(idToken)
	if uid == None:
		return { 'error' : 'Invalid token' }

	res = db.child("users").child("sellers").get(idToken)
	if uid in res.val():
		user = db.child("users").child("sellers").child(uid).get(idToken)
		#return JSON
		return { 'userId': uid, 'user': user.val() }

	return { 'error' : 'Server internal failure'}

def get_user_shops(idToken):
	if not (check_if_string([idToken])):
		return { 'error': 'Invalid argument'}

	uid = get_uid(idToken)
	if uid == None:
		return { 'error' : 'Invalid token' }

	res = db.child("users").child("sellers").get(idToken)
	if uid in res.val():
		shops = db.child("users").child("sellers").child(uid).child("shops").get(idToken)
		#return JSON
		return { 'shops': shops.val() }

	return { 'error' : 'Server internal failure'}

def set_user_info(idToken, name, imagepath):
	if not (check_if_string([idToken, name])):
		return { 'error': 'Invalid argument'}

	uid = get_uid(idToken)
	if uid == None:
		return { 'error' : 'Invalid token' }

	stimagepath = UPLOAD_FOLDER + str(uid) + imagepath.rsplit('.', 1)[1].lower()
	storage.child(stimagepath).put(imagepath, idToken)
	path = storage.child(stimagepath).get_url()

	db.child("users").child("sellers").child(uid).update({ 'name' : name, 'image' : path }, idToken)
	user = db.child("users").child("sellers").child(uid).get(idToken)

	return { 'userId': uid, 'user': user.val() }

def set_user_shop(idToken, shopid, name, lon, lat):
	if not (check_if_string([idToken, shopid, name]) and check_if_double([lon, lat])):
		return { 'error': 'Invalid argument'}

	uid = get_uid(idToken)
	if uid == None:
		return { 'error' : 'Invalid token' }

	res = db.child("users").child("sellers").get(idToken)
	if uid in res.val():
		db.child("users").child("sellers").child(uid).child("shops").update({ shopid: { "location" : { "longitude": lon, "latitude": lat }, "name" : name } }, idToken)
		shop = db.child("users").child("sellers").child(uid).child("shops").child(shopid).get(idToken)

		return { 'shopId': shopid, 'shop': shop.val() }

	return { 'error' : 'Server internal failure'}

def set_user_shop_item(idToken, shopid, itemId, name, category, gender, price, imagepath):
	if not (check_if_string([idToken, shopid, itemId, name]) and check_if_gender(gender) and check_if_category(category) and check_if_double([price])):
		return { 'error': 'Invalid argument'}

	uid = get_uid(idToken)
	if uid == None:
		return { 'error' : 'Invalid token' }

	print("step#1")
	res = db.child("users").child("sellers").get(idToken)
	if uid in res.val():
		res2 = db.child("users").child("sellers").child(uid).child("shops").get(idToken)
		if not res2:
			return { 'error' : 'No shops in list'}
		if shopid in res2.val():
			res3 = db.child("users").child("sellers").child(uid).child("shops").child(shopid).get(idToken)	
			if itemId in res3.val():
				gid = db.child("users").child("sellers").child(uid).child("shops").child(shopid).child("goods").child(itemId).child(key).get(idToken)

				#upload file
				stimagepath = UPLOAD_FOLDER + str(gid) + imagepath.rsplit('.', 1)[1].lower()
				storage.child(stimagepath).put(imagepath, idToken)
				path = storage.child(stimagepath).get_url()

				#update info
				db.child("users").child("sellers").child(uid).child("shops").child(shopid).child("goods").child(itemId).update({ 
				'name' : name,
				'category' : category, 
				'gender': gender, 
				'price' : price,
				'image' : path 
				}, idToken)
			else:
				#set new info
				gid = db.generate_key()

				print("step#2")
				#upload file
				stimagepath = UPLOAD_FOLDER + str(gid) + imagepath.rsplit('.', 1)[1].lower()
				print("step#3")
				storage.child(stimagepath).put(imagepath, idToken)
				print("step#4")
				path = storage.child(stimagepath).get_url()

				db.child("users").child("sellers").child(uid).child("shops").child(shopid).child("goods").update({ itemId: { 
				'name' : name,
				'category' : category, 
				'gender': gender, 
				'price' : price,
				'image' : path, 
				'key' : gid 
				}}, idToken)

			item = db.child("users").child("sellers").child(uid).child("shops").child(shopid).child("goods").child(itemId).get(idToken)

			return { 'itemId': itemId, 'item': item.val() }

		return { 'error' : 'Invalid shopId'}

	return { 'error' : 'Server internal failure'}


def check_if_double(param):
	for i in param:
		try:
			float(i)
		except ValueError:
			return False
	return True

def check_if_gender(param):
	if param != 'male' and param != 'female' and param != 'unisex':
		return False

	return True

def check_if_category(param):	
	return True

def check_if_string(param):
	for i in param:
		if not isinstance(i, str):
			return False
	return True

"""
def get_user_info_with_path(idToken, path):
	uid = get_uid(idToken)
	if uid == None:
		print('Error : can\'t get localId to write user info','Info:',info)
		return

	res = db.child("users").child("sellers").get(idToken)
	if uid in res.val():
		temp = db.child("users").child("sellers").child(uid).child(path).get(idToken)
		#return JSON
		return { 'userId': uid, temp.key() : temp.val() }

	return error_response_template("Can\'t find user with given idToken: " + idToken)

def set_user_info_with_path(idToken, path, info):
	uid = get_uid(idToken)
	if uid == None:
		print('Error : can\'t get localId to write user info','Info:',info)
		return

	temp = db.child("users").child("sellers").child(uid).child(path).get(idToken)
	return temp.val()


def add_user_item(idToken, info):
	uid = get_uid(idToken)
	if uid == None:
		print('Error : can\'t get localId to write user info','Info:',info)
		return

	gid = db.generate_key()

	db.child("users").child("sellers").child(uid).child("goods").child(gid).set(info, idToken)

	item = db.child("users").child("sellers").child(uid).child("goods").child(gid).get(idToken)

	#return JSON
	return item_response_template(info)

def like_user_item(idToken, hostId, itemId):
	uid = get_uid(idToken)
	if uid == None:
		print('Error : can\'t get localId to write user info','Info:',info)
		return

	item = db.child("users").child("sellers").child(hostId).child("goods").child(itemId).get(idToken)
	user = db.child("users").child("sellers").child(hostId).get(idToken)

	db.child("users").child("customers").child(uid).child("liked").child(item.key()).set(searching_item_template(user, item), idToken)

	#return JSON
	return empty_response_template()


def set_user_location(idToken, info):
	uid = get_uid(idToken)
	if uid == None:
		print('Error : can\'t get localId to write user info','Info:',info)
		return

	country = info["country"]

	#if user is seller
	res = db.child("users").child("sellers").get(idToken)
	if uid in res.val():
		db.child("users").child("sellers").child(uid).child("location").set(info, idToken)
		db.child("users").child("sellers").child(uid).child("country").set(country, idToken)
		return loc_response_template(info)

	#if user is customer
	res = db.child("users").child("customers").get(idToken)
	if uid in res.val():
		db.child("users").child("customers").child(uid).child("location").set(info, idToken)
		db.child("users").child("customers").child(uid).child("country").set(country, idToken)
		return loc_response_template(info)

	return error_response_template("Can\'t find user with given idToken: " + idToken)

def get_items_byloc(idToken, location, params):

	users_by_country = db.child("users").child("sellers").order_by_child("country").equal_to(location[2]).get(idToken)

	dic = {}

	for user in users_by_country.each():
		uloc = get_formatted_location(user.val()["location"])
		dist = evaluate_distance(uloc[0], uloc[1], location[0], location[1])

		if (dist < 1):
			dic.update(get_user_items(idToken, user, params))

	return searching_response_template(dic)

def get_formatted_location(data):
	lon = data['longitude']
	lat = data['latitude']

	return [float(lat), float(lon)]

def evaluate_distance(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def get_user_items(idToken, user, params):
	token = get_uid(idToken)

	items_by_param = db.child("users").child("sellers").child(user.key()).child("goods").get(idToken)

	dic = {}

	for item in items_by_param.each():
		obj = searching_item_template(user, item)
		dic[item.key()] = obj

	return dic

def searching_item_template(user, item):
	info = {'item': item.val(),
			'hostKey': user.key(),
			'hostName': user.val()["name"]
			}
	return info

def searching_response_template(items):

	JSON = {'infoType': 'searching',
			'info' : items }

	return JSON

def user_response_template(usertype, idToken, id, info):
	infoJSON = {'idToken': idToken, 
				'id': id,
				'usertype' : usertype
				}

	temp = dict(infoJSON)
	temp.update(info)

	JSON = {'infoType': 'user', 
			'info': temp
			}

	return JSON

def item_response_template(info):

	JSON = {'infoType': 'item', 
			'info': info
			}

	return JSON

def loc_response_template(location):
	JSON = {'infoType': 'location', 
			'info': location
			}

	return JSON

def empty_response_template():

	JSON = {'infoType': 'empty'}

	return JSON

def error_response_template(info):

	JSON = {'infoType': 'error', 
			'info': info
			}

	return JSON
"""

