import requests
from selenium import webdriver
from datetime import date
import pandas as pd
import os

# find elements
driver = webdriver.Firefox()
driver.get("https://www.coppellisd.com/COVID-19Dashboard")
p_elements = driver.find_elements_by_tag_name('td')

values = [] # appending them as text
for p in p_elements:
  values.append(str(p.text))

# full = []
# current = []
# for value in values:
#   if value == "\\n":
#     "".join(current)
#     full.append(current)
#     current = []
#   else:
#     current.append(value)

# print(full)


timestamp = []
building = []
staff = []
inperson = []
remote = []
other = []

# format lists
count = 0
for p in values:
  if count == 0:
    timestamp.append(date.today())
    building.append(p)
    count += 1
  elif count == 1:
    staff.append(str(p))
    count += 1
  elif count == 2:
    inperson.append(str(p))
    count += 1
  elif count == 3:
    remote.append(str(p))
    count += 1
  else:
    other.append(str(p))
    count = 0

# add to dataframe
df = pd.DataFrame()
df["timestamp"] = timestamp
df["building"] = building
df["staff"] = staff
df["inperson"] = inperson
df["remote"] = remote
df["other"] = other


numcols = ["staff", "inperson", "remote", "other"]

df["staff"] = pd.to_numeric(df["staff"], errors='coerce')
df["inperson"] = pd.to_numeric(df["inperson"], errors='coerce')
df["remote"] = pd.to_numeric(df["remote"], errors='coerce')
df["other"] = pd.to_numeric(df["other"], errors='coerce')

df["total"] = df[numcols].sum(axis=1)
numcols.append("total")

print(df)


# save the dataframe
today = date.today().strftime('%d-%m-%Y')
os.chdir('./data')
df.to_csv(f'{today}.csv', index=False)


# save column totals to totals.csv
day_totals = [today]
for col in numcols:
  sum = sum(df[col])
  day_totals.append(sum)

with open('./data/totals.csv','wb') as file:
    file.write(totals)


# append all content to timeseries
df.to_csv('./data/timeseries.csv', mode='a', header=False, index=False)