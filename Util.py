from os import path, remove
import glob
import shelve

def get_tweepy_enabled():
    return False

def get_card_dict():
    s = shelve.open('cards')

    stocks = s.items()
    stock_dict = convert_tuple_to_dict(stocks)    

    s.close()

    return stock_dict

def set_card_shelf(dic):
    s = shelve.open('cards')
    s.update(dic)
    s.close()

def clear_card_shelf():
    if path.exists(f"cards.dat"):
        card_dat_list = glob.glob(f"cards.*")
        for card_dat in card_dat_list:
            remove(card_dat)

def convert_tuple_to_dict(tup):
    dic = {}
    for a, b in tup:
        dic.setdefault(a, b)
    
    return dic
