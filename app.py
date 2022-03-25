import imp
import schedule
import time
import requests
import os
from dbConnector import dbConnector


apiBasePath= "/api/v3/"
frequency = os.environ['Frequency']
radarrUrl = os.environ['RadarrUrl']
radarrKey = os.environ['RadarrApikey']
sonarrUrl = os.environ['SonarrUrl']
sonarrKey = os.environ['SonarrApiKey']


db = dbConnector('/data/db.json')


def addAuthKey(url, key):
    return url + "?apikey=" + key

def appendPageSize(url, size):
    return url + "&pageSize=" + str(size)

def appendDeleteModifiers(url):
    return url + "&removeFromClient=true&blocklist=true"

def makeUrlForEndpoint(url, basePath, endpoint, authKey):
    return addAuthKey(url+basePath+endpoint, authKey)

def parseJsonRequest(url, reqtype):
    if reqtype == "get":
        r = requests.get(url)
        return r.json()
    if reqtype == "delete":
        r = requests.delete(url)
        return r.json()

def getMaxLenForRequest(url):
    req = parseJsonRequest(url, "get")
    return req['totalRecords']

def getResponseForEndpoint(endpoint, app, reqtype):
    url = ""
    if app == "sonarr":
        url = makeUrlForEndpoint(sonarrUrl, apiBasePath, endpoint, sonarrKey)
    if app == "radarr":
        url = makeUrlForEndpoint(radarrUrl, apiBasePath, endpoint, radarrKey)
    if url == "":
        raise AttributeError("App not found")
    if reqtype == "get":
        url = appendPageSize(url, getMaxLenForRequest(url))
    if reqtype == "delete":
        url = appendDeleteModifiers(url)
    return parseJsonRequest(url, reqtype)

def purgeDb():
    return

def job():
    print("scanning...")
    try:
        items = getResponseForEndpoint("queue", "sonarr", "get")
        for record in items["records"]:
            if(db.downloadExists(record, db.sonarrTable) == False):
                db.insertNewDownload(record["id"], record["title"], record["status"], record["sizeleft"], db.sonarrTable)
            else:
                db.updateDownload(record, db.sonarrTable)
        records = db.sonarrTable.all()
        for record in records:
            if(record["inactiveCount"] > 3):
                # removing stale torrents here
                print("removing torrent: " + str(record["id"]))
                try:
                    r =getResponseForEndpoint("queue/" + str(record["id"]), "sonarr", "delete")
                finally:
                    db.removeDownloadById(record["id"], db.sonarrTable)
    except Exception as e:
        print(e)



#schedule.every().minute.at(":17").do(job)
schedule.every(int(frequency)).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)