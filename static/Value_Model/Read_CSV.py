import csv

with open('../Documentation/Database_Stocks.csv') as fin:
    rows = []
    csvin = csv.DictReader(fin)
    for row in csvin:
        rows.append(row)

print(rows)




