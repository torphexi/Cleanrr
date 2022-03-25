from tinydb import TinyDB, Query

class dbConnector:
    def __init__(self, storagePath) -> None:
        self.db = TinyDB(storagePath)
        self.sonarrTable = self.db.table('sonarr')
        self.radarrTable = self.db.table('radarr')
        pass
    Record = Query()

    def insertNewDownload(self, id, title, status, sizeleft, table):
        table.insert({'id': id, 'title': title, 'status': status,'sizeleft': sizeleft, 'inactiveCount': 0})

    def updateDownloadById(self, id,field, value, table):
        table.update({field : value}, self.Record.id == id)

    def removeDownloadById(self, id, table):
        table.remove(self.Record.id == id)

    def findDownload(self, id, table):
        return table.search(self.Record.id == id)

    def downloadExists(self, download, table):
        a = table.search(self.Record.id == download['id'])
        res = len(a) != 0
        return res

    def updateDownload(self, download, table):
        id = download["id"]
        existing = self.findDownload(id, table)
        if(len(existing) == 0):
            return
        existing = existing[0]
        if(download['status'] == 'warning' and download['sizeleft'] == existing['sizeleft']) or download['status'] == "queued":
            self.updateDownloadById(id, 'inactiveCount', existing['inactiveCount'] + 1, table)