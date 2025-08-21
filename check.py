from time import sleep
import requests
import json
from btcaddr import Wallet
from time import sleep
from itertools import cycle

def generate_addresses(count):
	addresses = {}
	for i in range(count):
		wallet = Wallet()
		pub = wallet.address.__dict__["mainnet"].__dict__["pubaddr1"]
		prv = wallet.key.__dict__["mainnet"].__dict__["wif"]
		addresses[pub] = prv
	return addresses

def check_balance_btc(data=generate_addresses(100)):
	"""Проверяет балансы адресов, распределяя запросы по нескольким API и батчам."""

	def _headers():
		return {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Firefox/116.0",
			"Accept": "application/json",
		}

	def fetch_blockchain_info(batch):
		url = f"https://blockchain.info/multiaddr?active={'|'.join(batch)}"
		resp = requests.get(url, headers=_headers(), timeout=15)
		resp.raise_for_status()
		js = resp.json()
		out = {}
		for item in js.get("addresses", []):
			addr = item.get("address")
			bal = item.get("final_balance", 0)
			if addr is not None:
				out[addr] = int(bal)
		return out

	def fetch_blockcypher(batch):
		# Разрешает несколько адресов через ';'
		url = f"https://api.blockcypher.com/v1/btc/main/addrs/{';'.join(batch)}/balance"
		resp = requests.get(url, headers=_headers(), timeout=15)
		resp.raise_for_status()
		js = resp.json()
		items = js if isinstance(js, list) else [js]
		out = {}
		for item in items:
			addr = item.get("address")
			bal = item.get("final_balance", item.get("balance", 0))
			if addr is not None:
				out[addr] = int(bal)
		return out

	def fetch_blockchair(batch):
		# Принимает адреса через ','
		url = f"https://api.blockchair.com/bitcoin/dashboards/addresses/{','.join(batch)}"
		resp = requests.get(url, headers=_headers(), timeout=15)
		resp.raise_for_status()
		js = resp.json()
		out = {}
		for addr, payload in js.get("data", {}).items():
			addr_info = payload.get("address", {})
			bal = addr_info.get("balance", 0)
			out[addr] = int(bal)
		return out

	providers = [
		{"id": 1, "name": "blockchain.info", "fn": fetch_blockchain_info, "max": 50},
		{"id": 2, "name": "blockcypher", "fn": fetch_blockcypher, "max": 100},
		{"id": 3, "name": "blockchair", "fn": fetch_blockchair, "max": 50},
	]

	addresses_all = list(data.keys())
	results = []
	idx = 0
	provider_index = 0  # Индекс текущего провайдера для ротации
	
	while idx < len(addresses_all):
		batch = addresses_all[idx: idx + 50]  # Нормальный размер батча для production
		
		# Берем следующий провайдер по кругу
		provider = providers[provider_index % len(providers)]
		provider_index += 1
		
		# Пробуем текущий провайдер
		success = False
		try:
			balances = provider["fn"](batch)
			
			for addr in batch:
				bal = int(balances.get(addr, 0))
				results.append({
					"address": addr,
					"balance": bal,
					"private": data[addr],
					"provider": provider["id"],
				})
			success = True
			sleep(0.2)
		except Exception as e:
			# Если провайдер упал, помечаем как нули
			for addr in batch:
				results.append({
					"address": addr,
					"balance": 0,
					"private": data[addr],
					"provider": provider["id"],  # Показываем какой провайдер упал
				})
		
		idx += len(batch)

	return results

"""def last_seen_bc(address):

	try:
		address = address
		reading_state = 1
		while reading_state:
			try:
				htmlfile = urlopen(
					f"https://blockchain.info/q/addressfirstseen/{address}?format=json",
					timeout=10,
				)
				htmltext = htmlfile.read().decode("utf-8")
				reading_state = 0
			except:
				reading_state += 1
				sleep(60 * reading_state)
		ts = int(htmltext)
		if ts == 0:
			return 0
		return str(datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"))
	except:
		return None
"""