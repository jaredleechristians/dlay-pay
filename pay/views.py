from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from .forms import id_form
import requests

from django.utils.http import urlencode

# Create your views here.

@csrf_exempt
def index(request):
	if request.method == "POST":			
		form = id_form(request.POST)
		if form.is_valid():
			request.session['app_data'] = request.POST
			auth(request)
			return qualify_validate(request)
			
		context = {
			"form" : form,
			"data" : request.POST
		}
		
		return render(request,'pay/index.html', context)
	else:
		# error no post data
		context = {
			'message' : "no post data"
		}
		return render(request,'pay/error.html', context)

def member(request):
	# some logic over here

	context = {
		"data" : request.session['app_data']
	}
	return render(request,'pay/member.html',context)

def instalment(request):
	print(request.session["app_data"])
	print(request.session["ammacom_validate"])

	id_no = request.session["app_data"]['id_no']
	full_ammount = request.session["app_data"]['amount']

	# calculate instalment period
	request.session["period"] = 3
	deposit = float(full_ammount) / request.session["period"]
	instalment = deposit

	url = "https://app-uat.dlay.co.za/server/api/membership-check"
	query = {
		"id_no" : id_no,
		"full_amount" : float(full_ammount)
	}
	print(query)
	bearer_token = f"Bearer {request.session['access_token']}"
	headers = {"Authorization": bearer_token, "Content-Type" : "application/json"}
	response = requests.post(url, json=query, headers=headers)
	if response.status_code == 200:
		print(response.json())
		request.session["membership"] = response.json()
		context = {
			"app_data" : request.session["app_data"],
			"ammacom_validate" : request.session["ammacom_validate"],
			"ammacom_membership" : request.session["membership"],
			"period" : request.session["period"],
			"deposit" : round(deposit,2),
			"instalment" : round(instalment,2),
		}
		return render(request,'pay/instalment.html',context)
	context = {
			"description" : f"Error code: {response.status_code}"
		}
	return render(request,'pay/error.html',context)

def confirm(request):
	print(request.POST)
	request.session["billing_day"] = request.POST['billing_day']
	url = "https://app-uat.dlay.co.za/server/api/init-sub-setup"
	query = {
			"transaction_id" : request.session["app_data"]["transaction_id"],
			"ammacom_id" : request.session["ammacom_validate"]["ammacom_id"],
			"merchant_code" : request.session["app_data"]["merchant_code"],
			"billing_day" : request.session["billing_day"],
			"full_amount" : float(request.session["app_data"]["amount"]),
			"period" : int(request.session["period"]),
			"email" : request.session["app_data"]["email"],
			"status_callback": request.session["app_data"]["notify_url"],
			"e_commerce_redirect": request.session["app_data"]["return_url"]
	}
	print(query)
	bearer_token = f"Bearer {request.session['access_token']}"
	headers = {"Authorization": bearer_token, "Content-Type" : "application/json"}
	response = requests.post(url, json=query, headers=headers)
	if response.status_code == 200:
		request.session["ammacom_initiate"] = response.json()
		print(response.json())
		context = {
			"app_data" : request.session["app_data"],
			"ammacom_validate" : request.session["ammacom_validate"],
			"ammacom_initiate" : request.session["ammacom_initiate"],
			"period" : int(request.session["period"]),
			"billing_day" : request.session["billing_day"],
		}
		return render(request,'pay/confirm.html',context)
	context = {
			"description" : f"Error code: {response.status_code}"
		}
	return render(request,'pay/error.html',context)

def checkout(request):
	print("checkout")
	context = {
		"ammacom_id" : request.session["ammacom_validate"]["ammacom_id"]
	}
	return render(request,'pay/checkout.html',context)

def callback(request):
	print(request.GET)
	url = "https://test.oppwa.com/v1/checkouts/"+ request.GET['id'] +"/payment"+"?entityId=8a8294174e735d0c014e78cf26461790"
	bearer_token = "Bearer OGE4Mjk0MTc0ZTczNWQwYzAxNGU3OGNmMjY2YjE3OTR8cXl5ZkhDTjgzZQ=="
	headers = {"Authorization": bearer_token, "Content-Type" : "application/json"}
	response = requests.get(url, headers=headers)
	if response.status_code == 200:
		print("validate checkout success")
		print(response.json())
		context = {
			"response" : response.json()
		}
		return render(request,'pay/callback.html',context)
	context = {
		"response" : response.json(),
		"description" : "payment error"
	}
	return render(request,'pay/error.html',context)

def auth(request):
	print("trying auth...")
	url = "https://accounts.zoho.com/oauth/v2/token"
	query = {
		"refresh_token" : "1000.21e70c4a38374e274f90b58a10b35824.d80a5fc6901dc1ccbb8341839db3a36d",
		"client_id" : "1000.8NSD2AMPHBOHLX93P2HU0C39PZ6W9D",
		"client_secret" : "a4ad9eaa83c30663d30ab2cf9d688d3082083307cb",
		"grant_type" : "refresh_token"

	}
	response = requests.post(url, data=query)
	if response.status_code == 200:
		print("auth successful!")
		access_token = response.json()["access_token"]
		#print("access_token:", access_token)
		request.session['access_token'] = access_token
	else:
		print(response)
		print(response.json())

def qualify_validate(request):
	print("qualify-validate")
	url = "https://app-uat.dlay.co.za/server/api/qualify-validate"
	#print(request.session['app_data'])
	first_name = request.session['app_data']['first_name']
	query = {
		"first_name" : first_name,
		"last_name" : request.session['app_data']['last_name'],
		"mobile" : request.session['app_data']['mobile'],
		"merchant_code" : request.session['app_data']['merchant_code'],
		"transaction_id" : request.session['app_data']['transaction_id'],
		"id_no" : request.session['app_data']['id_no'],
	}
	print(query)
	bearer_token = f"Bearer {request.session['access_token']}"
	headers = {"Authorization": bearer_token, "Content-Type" : "application/json"}
	response = requests.post(url, json=query, headers=headers)
	if response.status_code == 200:
		print(response.json())
		request.session['ammacom_validate'] = response.json()

		# membership declined
		if response.json()["vetting_status"] == "DECLINED":
			context = {
				"request_status" : response.json()["request_status"],
				"description" : "You do not meet our criteria. Please try again in 30 days."
			}
			return render(request,'pay/error.html',context)

		# cart exeeds approved value
		if float(request.session['app_data']['amount']) >= float(response.json()["amount_limit"]):
			context = {
				"request_status" : response.json()["request_status"],
				"description" : "Your cart value exeeds the approved DLAY amount."
			}
			return render(request,'pay/error.html',context)
		context = {
				"request_status" : response.json()["request_status"],
		}
		return redirect('/pay/member/',context)
	else:
		print(response)
		print(response.text)
		context = {
				"description" : f" Error code: {response.status_code}"
		}
		return render(request,'pay/error.html',context)
		
		

