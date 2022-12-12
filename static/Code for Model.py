import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


df=pd.read_excel("Dow 30 Stocks.xlsx")
df1=pd.read_excel("List_CPI_2.xlsx")
df2=pd.read_excel("ValueInvestingSheet.xlsx")
df3=pd.read_excel("List_Treasury_Yield_10J.xlsx")

#input(start_date/end_date)="1996-03"-"2012-09" für 10 Jahres Intervalle

def adj_func(start_date,end_date):
    list=[]
    for i in range(len(df["Unnamed: 0"])):
        if df["Unnamed: 0"][i][:7]==start_date:
            list.append(i)
        elif df["Unnamed: 0"][i][:7]==end_date:
            list.append(i)

    cpi_index=[]
    for i in range(len(df1["Unnamed: 0"])):
        if df1["Unnamed: 0"][i][:7] == end_date:
            cpi_index.append(i)


    liste=[]
    for i in range(list[0],list[1]):
        for j in range(len(df1)):
            if df["Unnamed: 0"][i][:7] == df1["Unnamed: 0"][j][:7]:
                liste.append(df["IBM"][i]/df1["CPI"][j]*df1["CPI"][cpi_index[0]])
    return (sum(liste))/(int(end_date[0:4])-int(start_date[0:4])) #->E10 needed for ShillerKGV=infl.adj.stockprice/avg(infl.adj.EPS_TrailingTenYears)

# ab hier is Gewurstl, hab die closing values von Hand eingetragen um mal zu sehen....
risk=[]
for i in range(len(df3["Unnamed: 0"])):
    if df3["Unnamed: 0"][i][:4]=="2004":
        risk.append(df3["Treasury Yield 10 Years"][i])
print(np.mean(risk))



liste=[]
for i in range(66, 106):
    for j in range(len(df1)):
        if df["Unnamed: 0"][i][:7] == df1["Unnamed: 0"][j][:7]:
            liste.append(df["IBM"][i] / df1["CPI"][j] * 199.8)
listen=[]
for i in range(len(df2)):
    for j in range(len(df1)):
        if df2["Unnamed: 0"][i][:7]==df1["Unnamed: 0"][j][:7]:
            listen.append(df2["IBM"][i]/df1["CPI"][j]*199.8)


x=adj_func("2000-03", "2010-03")

Shiller_KGVs=[]

for i in listen:
    Shiller_KGVs.append(i/x)

Shiller_KGVs.reverse()
avg_Shiller=[(sum(Shiller_KGVs)/len(Shiller_KGVs))]


plt.plot(Shiller_KGVs)
plt.axhline(y = avg_Shiller, color = 'r', linestyle = '-')
plt.ylabel("Share PRice")

plt.grid()
plt.show()