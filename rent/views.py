from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from .forms import id_form
import requests
import json

from django.utils.http import urlencode


@csrf_exempt
def index(request):
	if request.method == "POST":
		form = id_form(request.POST)
		if form.is_valid():
			request.session['app_data'] = request.POST
			request.session['url'] = request.POST["api"]
			auth(request)
			return qualify_validate(request)

		context = {
			"form" : form,
			"data" : request.POST
		}
		print(context)
		return render(request,'rent/index.html', context)
	else:
		# error no post data
		context = {
			'description' : "No post data"
		}
		return render(request,'rent/error.html', context)

def member(request):
	product = json.loads(request.session['app_data']['products'])
	request.session['product'] = product[0]
	context = {
		"product_name" : product[0]['product_name'],
		"product_image" : product[0]['product_image'],
		"data" : request.session['app_data'],
		"amount_limit" : "{0:.2f}".format(float(request.session['ammacom_validate']["amount_limit"])),
		"monthly_fee" : request.session['app_data']['monthly_fee']
	}
	return render(request,'rent/member.html',context)

def instalment(request):
	print(request.session["app_data"])
	print(request.session["ammacom_validate"])

	id_no = request.session["app_data"]['id_no']
	full_ammount = request.session["app_data"]['amount']

	# instalment period
	request.session["period"] = float(request.session["app_data"]["period"])

	url = request.session["url"]+"/server/api/membership-check"
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
		# pay now
		monthly = float(full_ammount) / request.session["period"]
		pay_now = float(request.session["membership"]["membership"]["pay_now"])
		membership = float(request.session["membership"]["membership"]["monthly_price"])
		request.session["app_data"]["deposit"] = "{0:.2f}".format(round(monthly + pay_now,2))
		request.session["app_data"]["monthly"] = "{0:.2f}".format(round(monthly,2))
		request.session["app_data"]["total"] = "{0:.2f}".format(round(monthly + membership,2))
		request.session["app_data"]["membership"] = "{0:.2f}".format(membership)

		request.session["app_data"]["instalment"] = "{0:.2f}".format(round(float(request.session["app_data"]["deposit"]) + float(request.session["membership"]["membership"]["monthly_price"]),2))
		context = {
			"product_image" : request.session["product"]["product_image"],
			"app_data" : request.session["app_data"],
			"ammacom_validate" : request.session["ammacom_validate"],
			"ammacom_membership" : request.session["membership"],
			"period" : request.session["period"],
			"monthly" : "{0:.2f}".format(round(monthly,2)),
			"deposit" : "{0:.2f}".format(round(monthly + pay_now,2)),
			"total" : "{0:.2f}".format(round(monthly + membership,2)),
			"membership" : "{0:.2f}".format(membership),
			"monthly_fee" : request.session["app_data"]["monthly_fee"]
		}

		return render(request,'rent/instalment.html',context)
	context = {
			"description" : f"Error code: {response.status_code}"
		}
	return render(request,'rent/error.html',context)

def confirm(request):
	print(request.POST)
	request.session["billing_day"] = request.POST['billing_day']
	url = request.session["url"]+"/server/api/init-sub-setup"
	query = {
			"transaction_id" : request.session["app_data"]["transaction_id"],
			"ammacom_id" : request.session["ammacom_validate"]["ammacom_id"],
			"merchant_code" : request.session["app_data"]["merchant_code"],
			"billing_day" : request.session["billing_day"],
			"full_amount" : float(request.session["app_data"]["amount"]),
			"period" : int(request.session["period"]),
			"email" : request.session["app_data"]["email"],
			"status_callback": request.session["app_data"]["notify_url"],
			"e_commerce_redirect": request.session["app_data"]["return_url"], 
			"products" : request.session["app_data"]["product_codes"],
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
			"monthly_fee" : request.session["app_data"]["monthly_fee"]
		}
		print(request.session["app_data"])
		return render(request,'rent/confirm.html',context)
	context = {
			"description" : f"Error code: {response.status_code}"
		}
	return render(request,'rent/error.html',context)

def checkout(request):
	print("checkout")
	context = {
		"ammacom_id" : request.session["ammacom_validate"]["ammacom_id"]
	}
	return render(request,'rent/checkout.html',context)

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
		request.session['access_token'] = access_token
	else:
		print(response)
		print(response.json())

def qualify_validate(request):
	print("qualify-validate")
	url = request.session["url"]+"/server/api/qualify-validate"
	first_name = request.session['app_data']['first_name']
	query = {
		"first_name" : first_name,
		"last_name" : request.session['app_data']['last_name'],
		"mobile" : request.session['app_data']['mobile'],
		"merchant_code" : request.session['app_data']['merchant_code'],
		"merchant_name" : request.session['app_data']['merchant_name'],
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
				"description" : "You do not meet our criteria. Please try again in 30 days.",
				"reason" : response.json()["declined_reason"]
			}
			return render(request,'rent/error.html',context)

		# cart exeeds approved value
		if float(request.session['app_data']['amount']) >= float(response.json()["amount_limit"]):
			context = {
				"request_status" : response.json()["request_status"],
				"description" : "Your cart value exeeds the approved DLAY amount."
			}
			return render(request,'rent/error.html',context)
		context = {
				"request_status" : response.json()["request_status"],
		}
		return redirect('member/',context)
	else:
		print(response)
		print(response.text)
		context = {
				"description" : f" Error code: {response.status_code}"
		}
		return render(request,'rent/error.html',context)

@csrf_exempt
def conclude(request):
        data = json.loads(request.body.decode("utf-8"))
        auth(request)
        url = data["api"]+"/server/api/conc-sub-setup"
        query = {
                "transaction_id" : data["transaction_id"],
                "ammacom_id" : data["ammacom_id"],
                "merchant_code" : data["merchant_code"],
                "status" : data["status"],
		"serial_no" : data["serial"],
        }
        print(query)
        bearer_token = f"Bearer {request.session['access_token']}"
        headers = {"Authorization": bearer_token, "Content-Type" : "application/json"}
        response = requests.post(url, json=query, headers=headers)
        return JsonResponse(response.json(), status=201)

@csrf_exempt
def complete(request):
        data = json.loads(request.body.decode("utf-8"))
        auth(request)
        url = data["api"]+"/server/api/conc-sub-setup"
        query = {
                "transaction_id" : data["transaction_id"],
                "ammacom_id" : data["ammacom_id"],
                "merchant_code" : data["merchant_code"],
                "status" : data["status"]
        }
        print(query)
        bearer_token = f"Bearer {request.session['access_token']}"
        headers = {"Authorization": bearer_token, "Content-Type" : "application/json"}
        response = requests.post(url, json=query, headers=headers)
        return JsonResponse(response.json(), status=201)
