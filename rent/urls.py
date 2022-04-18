from django.urls import path
from . import views

urlpatterns = [
	path('',views.index, name="index"),
	path('member/',views.member,name="rent_member"),
	path('instalment/',views.instalment,name="rent_instalment"),
	path('confirm/',views.confirm,name="rent_confirm"),
	path('checkout/',views.checkout,name="rent_checkout"),
	path('conclude/',views.conclude,name="rent_conclude"),
]
