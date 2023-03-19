import requests
import os
import json


databases = json.loads(os.environ['DATABASES'])
apiToken = os.environ['API_TOKEN']
url = 'https://api.notion.com/v1/databases/'
headers = {
    'Authorization': apiToken,
    "Notion-Version": "2022-06-28",
}
ret = requests.get(url=url + databases['Plan Data'], headers=headers)

print(ret.json())