import requests

url = "https://juliandev.me/"
resp = requests.get(url)
print(resp.text)

ip = requests.get("https://api.ipify.org?format=json").json()
print("Tu IP pública local es:", ip)

response = requests.get("http://ip-api.com/json/191.156.43.31").json()
print(response)