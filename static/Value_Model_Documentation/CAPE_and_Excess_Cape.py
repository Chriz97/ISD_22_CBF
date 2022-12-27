# This Python file is used for the CAPE and Excess CAPE Graph for the Value Model
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


df=pd.read_excel("Dow 30 Stocks.xlsx")
df1=pd.read_excel("List_CPI_2.xlsx")

df3=pd.read_excel("List_Treasury_Yield_10J.xlsx")
df4=pd.read_excel("GiovanniProject_adj_quarterly_1990.xlsx")

#input(start_date/end_date)= earlierst possible"1996-03"

def adj_func(start_date,end_date,company):
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
                liste.append((df[company][i]/df1["CPI"][j])*df1["CPI"][cpi_index[0]])
    # return (sum(liste))/(int(end_date[0:4])-int(start_date[0:4])) #->E10 needed for ShillerKGV=infl.adj.stockprice/avg(infl.adj.EPS_TrailingTenYears)
    E_ten=(sum(liste))/(int(end_date[0:4])-int(start_date[0:4]))
    #here we can go either way, just calculating CAPE or Excess CAPE Ratio
    #CAPE:
        #return float(df4[company][index] / E_ten)
    #Excess CAPE Ratio:
    index = []
    for i in range(len(df4["Date"])):
        if df4["Date"][i][:7] == end_date:
            index.append(i)
    yield_index = []
    for i in range(len(df3["Unnamed: 0"])):
        if df3["Unnamed: 0"][i][:7] == end_date:
            yield_index.append(i)
    shiller_kgv=float(df4[company][index] / E_ten)


    return (float(E_ten/df4[company][index]))*100-float(df3["Treasury Yield 10 Years"][yield_index])

# print(adj_func("2012-06","2022-06","AAPL"))


# dow_30=["IBM","MMM","AXP","AMGN","AAPL","BA","CAT","CVX","CSCO","KO","DIS","HD","HON","INTC","JNJ","JPM","MCD","MRK","MSFT","NKE","PG","TRV","UNH","VZ","WBA","WMT"]
# shiller_kgv_sets=[]
# for i in dow_30:
#     shiller_kgv_sets.append(adj_func("2012-09","2022-09",i))
# df6=pd.DataFrame(shiller_kgv_sets)
# df6.to_excel(r"C:\Users\ruven\PycharmProjects\InformationSystemDevelopement\excess_cape62.xlsx")
#using the above we get the data together store them in one file which is later used for the models

df5=pd.read_excel("excess_cape_full.xlsx")
df6=pd.read_excel("Shiller_KGV_full.xlsx")

def value_graph(company):
    plt.title(company)
    plt.plot(df5[company])
    plt.axhline(y=df5[company].mean(), color='r', linestyle='-')
    plt.axhline(y=df5[company].mean()+df5[company].std(ddof=1), color='g', linestyle='-')
    plt.axhline(y=df5[company].mean()-df5[company].std(ddof=1), color='g', linestyle='-')
    plt.axhline(y=df5[company].mean() + 2*df5[company].std(ddof=1), color='y', linestyle='-')
    plt.axhline(y=df5[company].mean() - 2*df5[company].std(ddof=1), color='y', linestyle='-')
    plt.ylabel("excess CAPE")
    plt.grid()
    plt.show()



def value_graph(company):
    plt.title(company)
    plt.plot(df6[company])
    plt.axhline(y=df6[company].mean(), color='r', linestyle='-')
    plt.axhline(y=df6[company].mean() + df6[company].std(ddof=1), color='g', linestyle='-')
    plt.axhline(y=df6[company].mean() - df6[company].std(ddof=1), color='g', linestyle='-')
    plt.axhline(y=df6[company].mean() + 2 * df6[company].std(ddof=1), color='y', linestyle='-')
    plt.axhline(y=df6[company].mean() - 2 * df6[company].std(ddof=1), color='y', linestyle='-')
    plt.ylabel("CAPE")
    plt.grid()
    plt.show()

