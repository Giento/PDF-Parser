import json

import matplotlib.pyplot as plt
import seaborn as sns

with open('occurrences_multi.json') as json_f:
    data_dict = json.load(json_f)

# treba tocan popis sto sve ukloniti
del data_dict['https://github.com']
del data_dict['https://doi.org']

urls = []
page_nums = []
count = 0

for url, url_data in data_dict.items():
    if count >= 5:
        break
    for num in url_data['page_nums']:
        if isinstance(num, list):
            for item in num:
                urls.append(url)
                page_nums.append(item)
        else:
            urls.append(url)
            page_nums.append(num)

    count += 1

# Plot histogram
plt.figure(figsize=(10, 6))
plt.hist(page_nums, bins=20, edgecolor='black')
plt.xlabel('Page Numbers')
plt.ylabel('Frequency')
plt.title('Distribution of Page Numbers')
plt.show()

# Plot boxplot
plt.figure(figsize=(10, 6))
sns.boxplot(x=urls, y=page_nums)
plt.xlabel('URL')
plt.ylabel('Page Numbers')
plt.title('Boxplot of Page Numbers by URL')
plt.xticks(rotation=90)  # Rotate x labels for readability
plt.show()

# Plot scatter plot
plt.figure(figsize=(10, 6))
sns.scatterplot(x=urls, y=page_nums)
plt.xlabel('URL')
plt.ylabel('Page Numbers')
plt.title('Scatter Plot of Page Numbers by URL')
plt.xticks(rotation=90)  # Rotate x labels for readability
plt.show()
