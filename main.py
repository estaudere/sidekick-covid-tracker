import requests
from selenium import webdriver
from datetime import date
import pandas as pd

driver = webdriver.Firefox()
driver.get("https://www.coppellisd.com/COVID-19Dashboard")
p_element = driver.find_element_by_tag_name('td')
list_chars = p_element.text

full = []
current = ""
for c in list_chars:
  if c == "\\n":
    full.append(current)
    print(current)
    current = []
  else:
    current += c


timestamp = []
building = []
staff = []
inperson = []
remote = []
other = []

count = 0
for p in full:
  if count == 0:
    timestamp.append(date.today())
    building.append(str(p))
    count += 1
  if count == 1:
    staff.append(str(p))
    count += 1
  if count == 2:
    inperson.append(str(p))
    count += 1
  if count == 3:
    remote.append(str(p))
    count += 1
  if count == 4:
    other.append(str(p))
    count = 0

df = pd.DataFrame()
df["timestamp"] = timestamp
df["building"] = building
df["staff"] = staff
df["inperson"] = inperson
df["remote"] = remote
df["other"] = other

# df["timestamp"].to_numeric()
# df["building"].to_numeric()
# df["staff"].to_numeric()
# df["inperson"].to_numeric()
# df["remote"].to_numeric()
# df["other"].to_numeric()

print(df)


# path = '.\data\\'
# filename = str(date.today()) + '.csv'
# save_as = r + path + filename

# df.to_csv(save_as, index = False)