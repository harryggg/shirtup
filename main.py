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

from google.appengine.api import mail

from google.appengine.ext import db
import google.appengine.ext.db
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
		loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
		extensions=['jinja2.ext.autoescape'],
		autoescape=True)
measurementOrder = ["chest","shoulder","length"]
sizeOrder = ["XS","S","M","L","XL"]

def sendEmail(receiverEmail):
	sender = 'matanghao@hotmail.com'
	receiver = receiverEmail
	subject = 'python email test'
	smtpserver = 'smtp.live.com'
	username = 'matanghao@hotmail.com'
	password = '199484ha'
	msg = MIMEText('''</pre>
	<h1>helloWorld</h1>
	<pre>''','html','utf-8') 
	msg['Subject'] = subject 
	smtp = smtplib.SMTP('smtp.live.com:587')
	smtp.ehlo()
	smtp.starttls()
	smtp.login(username, password)
	smtp.sendmail(sender, receiver, msg.as_string())
	smtp.quit()
	print('done')

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
	quantityList = db.StringListProperty()
	measurementList = db.StringListProperty() #xs,s,m,l,xl

class AddSalePage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			
			template_values = {
					
			}		
			template = JINJA_ENVIRONMENT.get_template('addSale.html')
			self.response.write(template.render(template_values))
			
		else:
			self.redirect("/")
class AddSale(webapp2.RequestHandler):
	def post(self):
		try:
			user = users.get_current_user()
			new_sale = Sale()
			new_sale.sellerid = user.user_id()
			new_sale.name = self.request.get("saleName")
			new_sale.image = self.request.get("img")
			new_sale.price = float(self.request.get("price"))
			new_sale.description = self.request.get("description")
			XSlist = [self.request.get("XSchest"),self.request.get("XSshoulder"),self.request.get("XSlength")]
			Slist = [self.request.get("Schest"),self.request.get("Sshoulder"),self.request.get("Slength")]
			Mlist = [self.request.get("Mchest"),self.request.get("Mshoulder"),self.request.get("Mlength")]
			Llist = [self.request.get("Lchest"),self.request.get("Lshoulder"),self.request.get("Llength")]
			XLlist = [self.request.get("XLchest"),self.request.get("XLshoulder"),self.request.get("XLlength")]
			new_sale.measurementList = XSlist+Slist+Mlist+Llist+XLlist

			new_sale.put()
			self.redirect("/Sells")
		except:
			self.response.write("something is wrong with your input.Please check.")
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

class CheckMeasurementPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			sale = db.get(self.request.get("key"))
			measurement = sale.measurementList
			template_values = {
					'measurement':measurement,
					'key':self.request.get("key"),
					'canEdit':user.user_id() == sale.sellerid
				}
			
			#for sale in sales:
			#	self.response.out.write(sale.image)
			template = JINJA_ENVIRONMENT.get_template('checkMeasurement.html')
			self.response.write(template.render(template_values))
			
		else:
			self.redirect("/")

class EditSaleMeasurement(webapp2.RequestHandler):
	def post(self):
		sale = db.get(self.request.get("key"))
		XSlist = [self.request.get("XSchest"),self.request.get("XSshoulder"),self.request.get("XSlength")]
		Slist = [self.request.get("Schest"),self.request.get("Sshoulder"),self.request.get("Slength")]
		Mlist = [self.request.get("Mchest"),self.request.get("Mshoulder"),self.request.get("Mlength")]
		Llist = [self.request.get("Lchest"),self.request.get("Lshoulder"),self.request.get("Llength")]
		XLlist = [self.request.get("XLchest"),self.request.get("XLshoulder"),self.request.get("XLlength")]
		sale.measurementList = XSlist+Slist+Mlist+Llist+XLlist
		sale.put()
		self.redirect("/Sells")

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
	def get(self):
		user = users.get_current_user()
		if user:
			sale = db.get(self.request.get("key"))
			currentUser = User.gql("WHERE userid = '%s'"%(user.user_id())).get()
			found = False
			for i in range(5):
				if sale.measurementList[i*3]:
					chest = int(sale.measurementList[i*3])
				else:
					chest = 0
				if sale.measurementList[i*3+1]:
					shoulder = int(sale.measurementList[i*3+1])
				else:
					shoulder = 0
				if sale.measurementList[i*3+2]:
					length = int(sale.measurementList[i*3+2])
				else:
					length = 0
				if chest>currentUser.chest and shoulder>currentUser.shoulder and length>currentUser.length:
					found = True
					break
			if found:
				recommendation = sizeOrder[i]
			else:
				recommendation = "Cannot find suitable size.."
			template_values = {
					'sale':sale,
					'sizeOrder':sizeOrder,
					'recommendation':recommendation
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
			sizeDic = {"XS":0,"S":0,"M":0,"L":0,"XL":0}
			for i in range(len(sale.buyersList)):
				temp_user = User.gql("WHERE userid = '%s'"%(sale.buyersList[i])).get()
				emailList.append(temp_user.email)
				nameList.append(temp_user.name)
				sizeDic[sale.sizeList[i]] += 1

			template_values = {
					'sale':sale,
					'emailList':emailList,
					'nameList':nameList,
					'sizeDic':sizeDic,
					'sizeOrder':sizeOrder

				}
			
			
			template = JINJA_ENVIRONMENT.get_template('buyersList.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect("/")	

class EmailBuyers(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		if user:
			sale = db.get(self.request.get("key"))
			sellerName = User.gql("WHERE userid = '%s'"%(sale.sellerid)).get().name
			numberOfEmail = 0
			numberOfFails = 0
			for i in range(len(sale.buyersList)):
				userEmail = User.gql("WHERE userid = '%s'"%(sale.buyersList[i])).get().email
				userName = User.gql("WHERE userid = '%s'"%(sale.buyersList[i])).get().name
				if not mail.is_email_valid(userEmail):
					numberOfFails+=1
				else:
					sender_address = "shirt-up Support <support@example.com>"
					subject = "Your shirt is ready for collection"
					body = """
						Hi,%s:
							Your shirt is currently with %s.Please collect it soon.
							Thank you for using shirt-up!"""%(userName,sellerName)

					mail.send_mail(sender_address, userEmail, subject, body)
					numberOfEmail+=1
			self.response.write("%s emails sent. %s emails failed to send"%(numberOfEmail,numberOfFails))


app = webapp2.WSGIApplication([
		('/',Welcome),
    ('/main', MainPage),
    	('/checkMeasurement',CheckMeasurementPage),
		('/checkSize',CheckSize),
		('/measurement',EditMeasurement),
		('/updateMeasurement',UpdateMeasurement),
		('/accountInfo',AccountInfo),
		('/updateAccount',UpdateAccount),
		('/Sells',ListSalePage),
		('/addSalePage',AddSalePage),
		('/addSale',AddSale),
		('/checkSaleImage',CheckSaleImage),
		('/Buys',ListSaleForBuyer),
		('/buyShirt',BuyShirt),
		('/updateBuy',UpdateBuy),
		('/checkBuyers',ListBuyersPage),
		('/editSaleMeasurement',EditSaleMeasurement),
		('/emailBuyers',EmailBuyers)
														
], debug=True)
