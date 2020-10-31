from API import API
from Card import Card
from requests_html import AsyncHTMLSession
import asyncio
import time
import tweepy

cardSet = {}
tweepyEnabled = True

def notifyDifference(card, originalText):
    api = API()

    print("#######################################")
    print("            3080 STOCK ALERT           ")
    print(f"Button has changed from {originalText} to {card.getButtonText()} for {card.getName()}.")
    print(f"Please visit {card.getUrl()} for more information.")
    print("#######################################")
    print("")
    print("")

    if tweepyEnabled:
        auth = tweepy.OAuthHandler(api.getAPIKey(), api.getAPISecret())
        auth.set_access_token(api.getAccessToken(), api.getAccessTokenSecret())

        api = tweepy.API(auth)

        tweet = "3080 STOCK ALERT\n\n"
        tweet += f"{card.getName()[0:50]}...\n"
        tweet += f"{originalText} -> {card.getButtonText()}\n\n"
        tweet += f"Visit {card.getUrl()} for more info."

        api.update_status(tweet)

async def getStock():
    urls = {
        "https://www.bestbuy.com/site/searchpage.jsp?st=rtx+3080",
        "https://www.newegg.com/p/pl?N=100007709%20601357247"
    }
    s = AsyncHTMLSession()

    tasks = (parseUrl(s, url) for url in urls)

    return await asyncio.gather(*tasks)

async def parseUrl(s, url):
    if "bestbuy" in url:
        await parseBBUrl(s, url)
    if "newegg" in url:
        await parseNEUrl(s, url)

async def parseBBUrl(s, url):
    r = await s.get(url)
    cards = r.html.find('.right-column')

    for card in cards:
        header = card.find('.sku-header', first=True)

        stockButton = card.find('.sku-list-item-button', first=True).find('.btn', first=True)
        headerText = header.text
        cardUrl = f"https://www.bestbuy.com{header.find('a', first=True).attrs['href']}"
        cardId = "bb_" + cardUrl.split("skuId=")[1]

        card = Card(headerText, cardUrl, stockButton.text)

        if cardId in cardSet:
            if cardSet[cardId].getButtonText() != stockButton.text:
                originalText = cardSet[cardId].getButtonText()
                cardSet[cardId] = Card(headerText, cardUrl, stockButton.text)
                notifyDifference(cardSet[cardId], originalText)
        else:
            cardSet[cardId] = card

async def parseNEUrl(s, url):
    r = await s.get(url)
    cards = r.html.find('.item-cell')

    for card in cards:
        header = card.find('.item-info', first=True)
        stockButton = card.find('.item-button-area', first=True).find('.btn', first=True)
        headerText = header.text
        cardUrl = card.find('.item-container', first=True).find('a', first=True).attrs['href']
        cardId = "ne_" + cardUrl.split("/p/")[1].split("?")[0]

        card = Card(headerText, cardUrl, stockButton.text)

        if cardId in cardSet:
            if cardSet[cardId].getButtonText() != stockButton.text:
                originalText = cardSet[cardId].getButtonText()
                cardSet[cardId] = Card(headerText, cardUrl, stockButton.text)
                notifyDifference(cardSet[cardId], originalText)
        else:
            cardSet[cardId] = card

if __name__ == '__main__':
    print("Checking Stock...")

    while True:
        asyncio.run(getStock())
        time.sleep(10)