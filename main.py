import requests
import os
import json
import datetime

databases = json.loads(os.environ['DATABASES'])
apiToken = os.environ['API_TOKEN']
databasesURL = 'https://api.notion.com/v1/databases/'
pagesURL = 'https://api.notion.com/v1/pages/'
headers = {
    'Authorization': apiToken,
    "Notion-Version": "2022-06-28",
}


# 获取数据库属性
def getDatabaseInfo(databaseID: str):
    ret = requests.get(url=databasesURL+databaseID, headers=headers)
    return ret.json()

# 获取数据库内容
def getDatabaseQuery(databaseID: str):
    ret = requests.post(url=databasesURL+databaseID+'/query', headers=headers)
    return ret.json()

# 增加内容到数据库
def addDatabaseQuery(databaseID: str, properties: dict):
    payload = {
        "parent": {"database_id": databaseID},
        "properties": properties
    }
    ret = requests.post(url=pagesURL, headers=headers, json=payload)
    return ret.json()

# 修改数据库内容
def editDatabaseQuery(pageID: str, properties: dict):
    payload = {"properties": properties}
    ret = requests.patch(url=pagesURL+pageID, headers=headers, json=payload)
    return ret.json()

# 更新数据库进度
def refreshDatabaseQueryProgress(databaseID: str):
    queries = getDatabaseQuery(databaseID)['results']
    for q in queries:
        properties = {
            "进度": {"number": int(q['properties']['完成度']['formula']['number']*100)/100},
        }
        ret = editDatabaseQuery(pageID=q['id'], properties=properties)

# 刷新复选框内容
def checkDatabaseQuery(databaseID: str):
    # 先获取每条数据内容
    queries = getDatabaseQuery(databaseID)['results']
    for q in queries:
        updateTime = q['properties']['更新日期']['date']['start']
        if(datetime.datetime.strptime(updateTime, "%Y-%m-%d").date() < datetime.date.today()):

            if(q['properties']['预期目标']['number']==None):
                costNeed = q['properties']['总时间']['formula']['number']
            else:
                costNeed = q['properties']['预期目标']['number']

            properties = {
                "更新日期": {"date": {"start": str(datetime.date.today())}},
                "今日完成": {"checkbox": False},
                "超额完成": {"checkbox": False},
                "全部完成": {"checkbox": False},
                "当前完成": {
                    "number": q['properties']['今日完成']['checkbox'] + q['properties']['超额完成']['checkbox'] * 2 + q['properties']['当前完成']['number']
                },
            }

            if(properties['当前完成']['number']>costNeed):
                properties['当前完成']['number'] = costNeed
            if(q['properties']['全部完成']['checkbox']==True):
                properties['当前完成']['number'] = costNeed

            ret = editDatabaseQuery(pageID=q['id'], properties=properties)
    refreshDatabaseQueryProgress(databaseID=databaseID)

# 更新需要重复的数据
def setRepeatQuery(databaseID: str):
    queries = getDatabaseQuery(databaseID)['results']
    for q in queries:
        repeat = q['properties']['重复']['number']
        updateTime = q['properties']['更新日期']['date']['start']
        if(repeat != None and repeat != 0 and datetime.datetime.strptime(updateTime, "%Y-%m-%d").date() < datetime.date.today()):
            properties = {
                "重复": {
                    "number": repeat
                },
                "更新日期": {
                    "type": "date",
                    "date": {
                        "start": str(datetime.datetime.strptime(q['properties']['日期']['date']['end'], "%Y-%m-%d").date() + datetime.timedelta(days=repeat)),
                    }
                },
                "日期": {
                    "type": "date",
                    "date": {
                        "start": str(datetime.datetime.strptime(q['properties']['日期']['date']['start'], "%Y-%m-%d").date() + datetime.timedelta(days=repeat)),
                        "end": str(datetime.datetime.strptime(q['properties']['日期']['date']['end'], "%Y-%m-%d").date() + datetime.timedelta(days=repeat)),
                    }
                },
                "今日完成": {
                    "type": "checkbox",
                    "checkbox": False
                },
                "超额完成": {
                    "type": "checkbox",
                    "checkbox": False
                },
                "标签": {
                    "type": "multi_select",
                    "multi_select": q['properties']['标签']['multi_select']
                },
                "当前完成": {
                    "type": "number",
                    "number": 0
                },
                "进度": {
                    "type": "number",
                    "number": 0
                },
                "预期目标": {
                    "type": "number",
                    "number": None
                },
                "全部完成": {
                    "type": "checkbox",
                    "checkbox": False
                },
                "名称": {
                    "id": "title",
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": q['properties']['名称']['title'][0]['text']['content'],
                            },
                        }
                    ]
                }
            }
            editDatabaseQuery(pageID=q['id'], properties={"重复": {"number": 0}})
            ret = addDatabaseQuery(databaseID=databaseID, properties=properties)
    refreshDatabaseQueryProgress(databaseID=databaseID)

"""
    {
        "名称": {
            "title": [{"text": {"content": title}}]
        },
    }
"""

if __name__ == '__main__':
    checkDatabaseQuery(databaseID=databases['Plan Data'])
    setRepeatQuery(databaseID=databases['Plan Data'])