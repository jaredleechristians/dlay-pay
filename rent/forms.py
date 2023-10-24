from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

import re


class id_form(forms.Form):
	id_no = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': "text-input",'placeholder':"ID Number"}),label='')
	def clean_id_no(self,*args,**kwargs):
		test = ["0000000000000","1111111111111","2222222222222","3333333333333","4444444444444"]
		id = self.cleaned_data.get("id_no")
		
		pattern = re.compile("(((\d{2}((0[13578]|1[02])(0[1-9]|[12]\d|3[01])|(0[13456789]|1[012])(0[1-9]|[12]\d|30)|02(0[1-9]|1\d|2[0-8])))|([02468][048]|[13579][26])0229))(( |-)(\d{4})( |-)([01]8((( |-)\d{1})|\d{1}))|(\d{4}[01]8\d{1}))")
		if id in test:
			print("Test ID validated")
			return id
		if id == "":
			raise forms.ValidationError("")
		if not pattern.match(id):
			raise forms.ValidationError("*Invalid date of birth. Please enter a valid ID number")
		else:
			if id[0] == "0":
				year = "20"
			else:
				year = "19"
			dob = date(int(year+id[0:2]),int(id[2:4]),int(id[4:6]))
			#print(dob)
			now = date.today()
			age = relativedelta(now, dob).years
			#print(age)
			if age < 18:
				raise forms.ValidationError("*Invalid Age. You need to be at least 18 years or older to apply.")

		return id

