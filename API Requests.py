# import requests
# import json
# # Earnings per share
#
# url = 'https://www.alphavantage.co/query?function=EARNINGS&symbol=IBM&apikey=M9YDWDBER8VD0BTV'
# r = requests.get(url)
# data = r.content
# data_json = json.loads(data)
#
# list2 = []
# list3 = []
#
# daten2 = data_json["annualEarnings"]
#
# print(daten2)
#
# for i in range(10):
#     list2.append(data_json["annualEarnings"][i]["reportedEPS"])
#     list3.append(data_json["annualEarnings"][i]["fiscalDateEnding"])
#
#
#
# dictionary = dict(zip(list3, list2))
#
# #print(dictionary)
#
# url2 = 'https://www.alphavantage.co/query?function=CPI&interval=monthly&apikey=M9YDWDBER8VD0BTV'
# r2 = requests.get(url2)
# data2 = r2.content
# data_json2 = json.loads(data2)
#
# data_json2_clean = data_json2["data"]
#
# list_date = []
# list_value = []
#
# print(data_json2_clean)

# for i in range(10):
#     list_date.append(data_json[i]["date"])
#     list_value.append(data_json[i]["value"])
#
#
# dictionary2 = dict(zip(list_date, list_value))
#
# print(dictionary2)

