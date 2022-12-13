import csv

with open('Database_Stocks.csv') as fin:
    rows = []
    csvin = csv.DictReader(fin)
    for row in csvin:
        rows.append(row)

print(rows)




