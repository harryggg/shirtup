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

class MainPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			urllink = users.create_logout_url(self.request.uri)
			linktext = 'Logout'
		else:
			urllink = users.create_login_url(self.request.uri)
			linktext = 'Login'

		suppliers = Supplier.all()
		template_values = {'suppliers':suppliers,
												'user':user,
												'urllink':urllink,
												'linktext':linktext,
												'isadmin':users.is_current_user_admin()
											}
	
		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))

class Add(webapp2.RequestHandler):
	def post(self):
		Slist = [self.request.get("Schest"),self.request.get("Sshoulder"),self.request.get("Slength")]
		Mlist = [self.request.get("Mchest"),self.request.get("Mshoulder"),self.request.get("Mlength")]
		new_supplier = Supplier()
		new_supplier.name = self.request.get("supplier")
		new_supplier.measurementS = Slist
		new_supplier.measurementM = Mlist
		new_supplier.put()
		
		self.redirect("/")
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
					break
			if isfit:
				self.response.write("M")
			else:
				self.response.write("L")

app = webapp2.WSGIApplication([
    ('/', MainPage),
		('/addMeasurement',Add),
		('/checkSize',CheckSize)
														
], debug=True)
