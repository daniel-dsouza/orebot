from ores import ORES, MINERALS

import codecs
from datetime import datetime, timedelta
from functools import reduce, wraps
import json
from urllib.request import urlopen, Request, HTTPError
from urllib.parse import urlencode

price_cache = {'last_updated': datetime.min}

def longest_common_subsequence(string_1, string_2):
    """
    Calculates the longest common subsequence
    :param string_1: a string
    :param string_2: a string shorter than string 1
    :return: longest common subseqence as string
    """
    seq_1, seq_2 = [0], [0]
    seq_1.extend(string_1)
    seq_2.extend(string_2)
    M = [[0]*len(seq_1) for _ in range(0, len(seq_2))]

    # build table
    for i in range(1, len(seq_2)):
        for j in range(1, len(seq_1)):
            if seq_2[i] == seq_1[j]:  # matching characters
                M[i][j] = M[i-1][j-1] + 1
            else:  # use the current best solution
                M[i][j] = max(M[i][j-1], M[i-1][j])

    # recover solution
    lcs = ""
    i, j = len(seq_2)-1, len(seq_1)-1
    while i != 0 and j != 0:
        if seq_1[j] == seq_2[i] and M[i][j] != 0:  # we have found part of the solution
            lcs = seq_1[j] + lcs
            i, j = i-1, j-1
        elif M[i-1][j] > M[i][j-1]:
            i -= 1  # the next closest matching char is in seq_2
        else:
            j -= 1  # the next closest matching char is in seq_1

    return len(lcs)


def best_guess(guess):
    """
    Matches the input to the closes ore type
    :param input: user input
    :returns: the closes matching ore
    """
    matches = [(ore, longest_common_subsequence(ore.replace(' ', ''), guess.replace(' ', ''))) for ore in ORES]

    def better_match(a, b):
        return a if a[1] > b[1] or (a[1] == b[1] and len(a[0]) < len(b[0])) else b

    return reduce(better_match, matches)[0]


def check_cache(func):
    """ updates the cache if neccessary """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if datetime.now() - price_cache['last_updated'] > timedelta(hours=6):
            print('updating cache')

            ore_ids = [str(ORES[ore]['objectID']) for ore in ORES]
            mineral_ids = [str(v) for _, v in MINERALS.items()]

            uri = 'http://api.eve-central.com/api/marketstat/json?'
            get_params = {'usesystem': '30000142', 'typeid': ','.join(ore_ids + mineral_ids)}

            try:
                with urlopen(uri+urlencode(get_params)) as response:
                    reader = codecs.getreader('utf-8')
                    resp_json = json.load(reader(response))
                    for item in resp_json:
                        price_cache[item['sell']['forQuery']['types'][0]] = item['sell']['avg']

                    price_cache['last_updated'] = datetime.now()

            except HTTPError as e:
                print("Could not contact EVE Central: ", e)
            
            except json.JSONDecodeError as e:
                print("Could not decode response: ", e)


        return func(*args, **kwargs)

    return wrapper

@check_cache
def type_price_by_objectID(objectID):
    return price_cache[objectID]

@check_cache
def ore_price_by_name(ore):
    return price_cache[ORES[ore]['objectID']]

@check_cache
def mineral_price_by_name(mineral):
    return price_cache[MINERALS[mineral]]


def get_ore_value(ore_name, quantity):
    """ Calculates the value of quantity of ore based on ore prices """
    return ore_price_by_name(ore_name) * quantity


def get_mineral_value(ore_name, quantity, efficiency):
    """ Calculates the value of a quantity of ore based on mineral prices """
    mineral_amounts = [(mineral, amount*efficiency) for mineral, amount in ORES[ore_name].items() if mineral != 'objectID']
    mineral_values = [mineral_price_by_name(mineral) * amount for mineral, amount in mineral_amounts]
    return sum(mineral_values) * quantity

# print(best_guess('cdrk orche'))
# print(mineral_price_by_name('pyerite'))
# print(ore_price_by_name('gneiss'))
# print(get_mineral_value('gneiss', 100, 87))