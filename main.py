import requests
from selenium import webdriver
from datetime import date
import pandas as pd

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

df = pd.DataFrame()
df["timestamp"] = timestamp.astype(datetime)
df["building"] = building
df["staff"] = staff.astype(float)
df["inperson"] = inperson.astype(float)
df["remote"] = remote.astype(float)
df["other"] = other.astype(float)

# df["timestamp"].to_datetime()
df["staff"].to_numeric()
df["inperson"].to_numeric()
df["remote"].to_numeric()
df["other"].to_numeric()

print(df)

# save the dataframe
today = date.today().strftime('%d-%m-%Y')
df.to_csv(f'.\data\{today}.csv', index=False)