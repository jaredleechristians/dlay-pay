from django.urls import path
from . import views

urlpatterns = [
	path('',views.index, name="index"),
	path('member/',views.member,name="member"),
	path('instalment/',views.instalment,name="instalment"),
	path('confirm/',views.confirm,name="confirm"),
	path('checkout/',views.checkout,name="checkout"),
	#path('callback/',views.callback,name="callback"),
]
