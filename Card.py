class Card:
    def __init__(self, model, price, name, url, btnText):
        self.name = name
        self.model = model
        self.price = price
        self.url = url
        self.btnText = btnText

    def getName(self):
        return self.name

    def getUrl(self):
        return self.url

    def getButtonText(self):
        return self.btnText

    def getModel(self):
        return self.model

    def getPrice(self):
        return self.price
