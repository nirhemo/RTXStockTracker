class Card:
    def __init__(self, name, url, btnText):
        self.name = name
        self.url = url
        self.btnText = btnText 

    def getName(self):
        return self.name

    def getUrl(self):
        return self.url

    def getButtonText(self):
        return self.btnText