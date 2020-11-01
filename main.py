from API import API
from Card import Card
from requests_html import AsyncHTMLSession
from string import Template
import asyncio
import random
import time
import tweepy

cardSet = {}
tweepyEnabled = True

def notifyDifference(model, price, card, originalText):
    api = API()

    print("#######################################")
    print(f"            {model} STOCK ALERT           ")
    print(f"Button has changed from {originalText} to {card.getButtonText()} for {card.getName()}.")
    print(f"It's currently for sale at {price}.")
    print(f"Please visit {card.getUrl()} for more information.")
    print("#######################################")
    print("")
    print("")

    if tweepyEnabled:
        auth = tweepy.OAuthHandler(api.getAPIKey(), api.getAPISecret())
        auth.set_access_token(api.getAccessToken(), api.getAccessTokenSecret())

        api = tweepy.API(auth)

        tweet = f"{model} STOCK ALERT\n\n"
        tweet += f"{card.getName()[0:50]}...\n"
        tweet += f"Selling for {price}.\n\n"
        tweet += f"{originalText} -> {card.getButtonText()}\n\n"
        tweet += f"Visit {card.getUrl()} for more info."

        api.update_status(tweet)

async def getStock():
    bestBuyBaseUrl = "https://www.bestbuy.com/site/computer-cards-components/video-graphics-cards/abcat0507002.c?id=abcat0507002"
    bbModelStub = Template("qp=gpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)~NVIDIA%20GeForce%20RTX%20$Model")

    # Get the current time and append to the end of the url just to add some minor difference
    # between scrapes.
    t = int(round(time.time() * 1000))

    urls = {
        f"3070-={bestBuyBaseUrl}&{bbModelStub.substitute(Model='3070')}&t={t}",
        f"3070-=https://www.newegg.com/p/pl?N=100007709%20601357250&PageSize=96&t={t}",
        f"3080-={bestBuyBaseUrl}&{bbModelStub.substitute(Model='3080')}&t={t}",
        f"3080-=https://www.newegg.com/p/pl?N=100007709%20601357247&PageSize=96&t={t}",
        f"3090-={bestBuyBaseUrl}&{bbModelStub.substitute(Model='3090')}&t={t}",
        f"3090-=https://www.newegg.com/p/pl?N=100007709%20601357248&PageSize=96&t={t}",
    }
    s = AsyncHTMLSession()

    tasks = (parseUrl(s, url.split("-=")[1], url.split("-=")[0]) for url in urls)

    return await asyncio.gather(*tasks)

async def parseUrl(s, url, model):
    if "bestbuy" in url:
        await parseBBUrl(s, url, model)
    if "newegg" in url:
        await parseNEUrl(s, url, model)

async def parseBBUrl(s, url, model):
    r = await s.get(url)
    cards = r.html.find('.right-column')

    for card in cards:
        header = card.find('.sku-header', first=True)
        priceParent = card.find('.priceView-customer-price', first=True)
        price = priceParent.find('span', first=True).text

        stockButton = card.find('.sku-list-item-button', first=True).find('.btn', first=True)
        headerText = header.text
        cardUrl = f"https://www.bestbuy.com{header.find('a', first=True).attrs['href']}"
        cardId = "bb_" + cardUrl.split("skuId=")[1]

        card = Card(model, price, headerText, cardUrl, stockButton.text)

        if cardId in cardSet:
            if cardSet[cardId].getButtonText() != stockButton.text:
                originalText = cardSet[cardId].getButtonText()
                cardSet[cardId] = Card(model, headerText, cardUrl, stockButton.text)
                notifyDifference(model, price, cardSet[cardId], originalText)
        else:
            cardSet[cardId] = card

async def parseNEUrl(s, url, model):
    r = await s.get(url)
    cards = r.html.find('.item-cell')

    for card in cards:
        header = card.find('.item-info', first=True)
        priceParent = card.find('.price-current', first=True)

        try:
            price = f"{priceParent.text.split('.')[0]}.{priceParent.text.split('.')[1][0:2]}"
        except:
            price = "Unknown"

        stockButton = card.find('.item-button-area', first=True).find('.btn', first=True)
        headerText = header.text
        cardUrl = card.find('.item-container', first=True).find('a', first=True).attrs['href']
        cardId = "ne_" + cardUrl.split("/p/")[1].split("?")[0]

        card = Card(model, price, headerText, cardUrl, stockButton.text)

        if cardId in cardSet:
            if cardSet[cardId].getButtonText() != stockButton.text:
                originalText = cardSet[cardId].getButtonText()
                cardSet[cardId] = Card(model, headerText, cardUrl, stockButton.text)
                notifyDifference(model, price, cardSet[cardId], originalText)
        else:
            cardSet[cardId] = card

if __name__ == '__main__':
    print("Checking Stock...")

    while True:
        asyncio.run(getStock())
        time.sleep(random.randint(20, 30))
