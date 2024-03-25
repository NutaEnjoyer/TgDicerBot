import datetime
import requests

TOKEN = "135343:AAUlyxb1hUYZOkixa67zzna2LShjl4fe8O7"

url = 'https://pay.crypt.bot/api/'


class CryptoBot:

	def __init__(self, token: str):
		self.__token = token


	@property
	def headers(self):
		return {
			'Crypto-Pay-API-Token': self.__token
		}

	@staticmethod
	def get_usdt_to_rub_course():
		url = 'https://api.exchangerate-api.com/v4/latest/USD'
		response = requests.get(url)

		if response.status_code == 200:
			data = response.json()
			rub_course = data['rates']['RUB']
			return rub_course
		else:
			return None

	def get_me(self):
		u = url + 'getMe/'
		response = requests.get(u, headers=self.headers)
		return response.json()

	def create_invoice(self, amount):
		"""
		['result']['pay_url']
		['result']['invoice_id']
		['result']['status'] “active”, “paid” or “expired”
		"""
		u = url + 'createInvoice/'
		json = {
			'asset': "USDT",
			'amount': str(amount)
		}
		response = requests.get(u, headers=self.headers, json=json)

		return response.json()

	def get_invoices(self):
		u = url + 'getInvoices/'
		response = requests.get(u, headers=self.headers)
		return response.json()

	def check_invoice(self, id):
		u = url + 'getInvoices/'
		response = requests.get(u, headers=self.headers)
		for i in response.json()['result']['items']:
			if i['invoice_id'] == id:
				return i['status'] == "paid"
		return False

	def get_invoice_price(self, id):
		u = url + 'getInvoices/'
		response = requests.get(u, headers=self.headers)
		for i in response.json()['result']['items']:
			if i['invoice_id'] == id:
				print('Find price')
				print(i)
				return float(i['amount'])
		return 0

	def transfer(self, user_id, amount):
		import time
		u = url + 'transfer/'
		json = {
			"user_id": user_id,
			"asset": "USDT",
			"amount": amount,
			"spend_id": time.time()
		}
		response = requests.post(u, headers=self.headers, json=json)
		print(response)
		print(response.json())
		return response.json()
