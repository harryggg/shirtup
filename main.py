#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import datetime
import jinja2

import os
import json

from google.appengine.ext import db
import google.appengine.ext.db
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
																			 loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
																			 extensions=['jinja2.ext.autoescape'],
																			 autoescape=True)
measurementOrder = ["chest","shoulder","length"]

class Supplier(db.Expando):
	name = db.StringProperty()
	measurementS = db.StringListProperty()
	measurementM = db.StringListProperty()

class User(db.Expando):
	userid = db.StringProperty()
	name = db.StringProperty()
	email = db.EmailProperty()
	chest = db.IntegerProperty()
	shoulder = db.IntegerProperty()
	length = db.IntegerProperty()

class Sale(db.Expando):
	sellerid = db.StringProperty(User)
	name = db.StringProperty()
	image = db.BlobProperty()
	price = db.FloatProperty()
	description = db.StringProperty()
	buyersList = db.StringListProperty()
	sizeList = db.StringListProperty()
	supplier = db.ReferenceProperty(Supplier)
	quantityList = db.StringListProperty()

class AddSalePage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			
			template_values = {
					'suppliers':Supplier.all()
			}		
			template = JINJA_ENVIRONMENT.get_template('addSale.html')
			self.response.write(template.render(template_values))
			
		else:
			self.redirect("/")
class AddSale(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		new_sale = Sale()
		new_sale.sellerid = user.user_id()
		new_sale.name = self.request.get("saleName")
		new_sale.image = self.request.get("img")
		new_sale.price = float(self.request.get("price"))
		new_sale.description = self.request.get("description")
		new_sale.supplier = db.get(self.request.get("supplier"))
		new_sale.put()
		self.redirect("/Sells")
class ListSalePage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			
			sales = Sale.all()
			sales.filter("sellerid = ",user.user_id())
			template_values = {
					'sales':sales
				}
			
			#for sale in sales:
			#	self.response.out.write(sale.image)
			template = JINJA_ENVIRONMENT.get_template('listSales.html')
			self.response.write(template.render(template_values))
			
		else:
			self.redirect("/")
class AddNewSupplierPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			if users.is_current_user_admin():
				template_values = {
				}		
				template = JINJA_ENVIRONMENT.get_template('addNewSupplier.html')
				self.response.write(template.render(template_values))
			else:
				self.redirect("/main")
		else:
			self.redirect("/")




class AddSupplier(webapp2.RequestHandler):
	def post(self):
		Slist = [self.request.get("Schest"),self.request.get("Sshoulder"),self.request.get("Slength")]
		Mlist = [self.request.get("Mchest"),self.request.get("Mshoulder"),self.request.get("Mlength")]
		new_supplier = Supplier()
		new_supplier.name = self.request.get("supplier")
		new_supplier.measurementS = Slist
		new_supplier.measurementM = Mlist
		new_supplier.put()

		
		self.redirect("/listSuppliers")

class EditSupplier(webapp2.RequestHandler):
	def post(self):
		currentSupplier = db.get(self.request.get("key"))
		

		Slist = [self.request.get("Schest"),self.request.get("Sshoulder"),self.request.get("Slength")]
		Mlist = [self.request.get("Mchest"),self.request.get("Mshoulder"),self.request.get("Mlength")]
		
		currentSupplier.name = self.request.get("name")
		currentSupplier.measurementS = Slist
		currentSupplier.measurementM = Mlist
		currentSupplier.put()
		self.redirect("/listSuppliers")
class DeleteSupplier(webapp2.RequestHandler):
	def post(self):
		db.delete(self.request.get("key"))
		self.redirect("/listSuppliers")


class ListSuppliersPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			
			template_values = {
					'suppliers':Supplier.all(),
					'isadmin':users.is_current_user_admin()
				}		
			template = JINJA_ENVIRONMENT.get_template('listSuppliers.html')
			self.response.write(template.render(template_values))
			
		else:
			self.redirect("/")
class Welcome(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			self.redirect("/main")
		template_values={'urllink':users.create_login_url(self.request.uri)}
		template = JINJA_ENVIRONMENT.get_template('welcome.html')
		self.response.write(template.render(template_values))

class MainPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			url_link = users.create_logout_url(self.request.uri)
			linktext = 'Logout'
			currentUser = User.gql("WHERE userid = '%s'"%(user.user_id())).get()
			if not currentUser: #firsttime
				newUser = User()
				newUser.userid = user.user_id()
				newUser.name = user.nickname()
				newUser.email = user.email()
				newUser.put()
				currentUser = User.gql("WHERE userid = '%s'"%(user.user_id())).get()
			template_values = {
				'user':currentUser,
				'urllink':url_link,
				'linktext':linktext,
					'isadmin':users.is_current_user_admin()
					}
			template = JINJA_ENVIRONMENT.get_template('index.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect("/")
			
			
	#suppliers = Supplier.all()
		

		

class EditMeasurement(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		currentUser = User.gql("WHERE userid = '%s'"%(user.user_id())).get()
		
		template_values = {
			'user':currentUser,

		}
		template = JINJA_ENVIRONMENT.get_template('measurement.html')
		self.response.write(template.render(template_values))
class UpdateMeasurement(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		currentUser = User.gql("WHERE userid = '%s'"%(user.user_id())).get()
		currentUser.chest = int(self.request.get("chest"))
		currentUser.shoulder = int(self.request.get("shoulder"))
		currentUser.length = int(self.request.get("length"))
		currentUser.put()
		self.redirect("/main")

class CheckSize(webapp2.RequestHandler):
	def post(self):
#check small
		supplier = Supplier.gql("WHERE name = '%s'"%(self.request.get("name"))).get()
		isfit = True
		for i in range(3):
			if (int(supplier.measurementS[i])<int(self.request.get(measurementOrder[i]))):
				isfit = False
				break
		if isfit:
			self.response.write("S")
		else:
			isfit = True
			for i in range(3):
				if (int(supplier.measurementM[i])<int(self.request.get(measurementOrder[i]))):
					isfit = False
					breakussh
			if isfit:
				self.response.write("M")
			else:
				self.response.write("L")

class AccountInfo(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		currentUser = User.gql("WHERE userid = '%s'"%(user.user_id())).get()
		template_values = {
			'user':currentUser,

		}
		template = JINJA_ENVIRONMENT.get_template('accountinfo.html')
		self.response.write(template.render(template_values))

class UpdateAccount(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		currentUser = User.gql("WHERE userid = '%s'"%(user.user_id())).get()
		currentUser.name = (self.request.get("name"))
		currentUser.email = (self.request.get("email"))
		currentUser.put()
		self.redirect("/main")

class CheckSaleImage(webapp2.RequestHandler):
	def post(self):
		sale = db.get(self.request.get("key"))
		self.response.headers['Content-Type'] = 'image/png'
		self.response.out.write(sale.image)

class ListSaleForBuyer(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			
			sales = Sale.all()
			template_values = {
					'sales':sales
				}
			
			#for sale in sales:
			#	self.response.out.write(sale.image)
			template = JINJA_ENVIRONMENT.get_template('listSalesForBuyer.html')
			self.response.write(template.render(template_values))
			
		else:
			self.redirect("/") 
class BuyShirt(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		if user:
			sale = db.get(self.request.get("key"))
			template_values = {
					'sale':sale
				}
			
			
			template = JINJA_ENVIRONMENT.get_template('buyShirt.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect("/")

class UpdateBuy(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		if user:
			sale = db.get(self.request.get("key"))
			sale.buyersList.append(user.user_id())
			sale.quantityList.append(self.request.get("quantity"))
			sale.sizeList.append(self.request.get("size"))
			sale.put()
			self.redirect("/Buys")
		else:
			self.redirect("/")

class ListBuyersPage(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		if user:
			sale = db.get(self.request.get("key"))
			emailList = []
			nameList = []
			for i in range(len(sale.buyersList)):
				temp_user = User.gql("WHERE userid = '%s'"%(sale.buyersList[i])).get()
				emailList.append(temp_user.email)
				nameList.append(temp_user.name)

			template_values = {
					'sale':sale,
					'emailList':emailList,
					'nameList':nameList

				}
			
			
			template = JINJA_ENVIRONMENT.get_template('buyersList.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect("/")				

app = webapp2.WSGIApplication([
		('/',Welcome),
    ('/main', MainPage),
		('/addSupplier',AddSupplier),
		('/checkSize',CheckSize),
		('/measurement',EditMeasurement),
		('/updateMeasurement',UpdateMeasurement),
		('/accountInfo',AccountInfo),
		('/updateAccount',UpdateAccount),
		('/editSupplier',EditSupplier),
		('/addNewSupplier',AddNewSupplierPage),
		('/listSuppliers',ListSuppliersPage),
		('/deleteSupplier',DeleteSupplier),
		('/Sells',ListSalePage),
		('/addSalePage',AddSalePage),
		('/addSale',AddSale),
		('/checkSaleImage',CheckSaleImage),
		('/Buys',ListSaleForBuyer),
		('/buyShirt',BuyShirt),
		('/updateBuy',UpdateBuy),
		('/checkBuyers',ListBuyersPage)
														
], debug=True)
