import praw
import urllib.request
import xmltodict
import functools
import xml.etree.ElementTree as ET
from collections import OrderedDict
import lxml
from xml.dom.minidom import parse
import xml.dom.minidom
import json
import locale
import time


class AppURLopener(urllib.request.FancyURLopener):
    #need to send this user_Agent to yahoo so they do not block the request
    version = "Mozilla/5.0"

def getFromDict(dataDict, mapList):
    return functools.reduce(lambda d, k: d[k], mapList, dataDict)


def XmlToDictionary(requestUrl):

    opener = AppURLopener()
    #req = urllib.request.Request(requestUrl,headers={'User-Agent': 'Mozilla/5.0'})
    response = opener.open(requestUrl)
    #data = parse(response)
    #xmldoc = minidom.parse(html)
    the_page = response.read()
    data = xmltodict.parse(the_page)
    #data = lxml.parse(the_page)
    data = json.dumps(data)
    data = json.loads(data)


    return data

#Create reddit object
r = praw.Reddit(user_agent='Currency__Converter Contact /u/USERNAME')

#set locale for number formatter
locale.setlocale(locale.LC_ALL, 'en_US')

#Log in
user = 'Currency__Converter'
r.login(user,'')
already_done = []

#Create dictionary of flag values and their corresponding currency
FlagDict = {'¥': 'JPY', '€': 'EUR', '£': 'GBP', '$' : 'USD', 'CAD' : 'CAD', 'AUD' : 'AUD'}

while True:
    #Get and Flatten comments out of tree hierarchy
    multi_reddits = r.get_subreddit('Currency__Converter')
    comments = praw.helpers.flatten_tree(multi_reddits.get_comments(limit = None))
    print(len(comments))
    #Get list of comments we have already commented on
    DoneFile = "/Users/easypawn/PycharmProjects/Currency__Converter/AlreadyDone.txt"
    AlreadyDone = open(DoneFile).readlines()
    #Loop Each comment
    print("Checking for flag characters in comments...")
    for comment in comments:
        isValue = False
        #Only check comments we havent replied to yet and that were not posted by us .Strip removes \n from id
        if comment.id + "\n" not in AlreadyDone and comment.author != user:
            #Check comment for each flag character, items in list are tuple pairs of character and currency ex. {$, USD}
            #print('Checking for flag characters in comment ' + comment.id)
            for item in FlagDict.items():
                flag = item[0]

                if flag in str(comment.body):
                    print(flag + ' found in comment ' + comment.id)
                    Base = FlagDict[flag]
                    print('The base currency is ' + Base)
                    #The comment has a flag character, loop each word
                    for word in comment.body.split():

                        if flag in word:
                            #grab all other characters besides the flag character and commas
                            strValue = word.replace(flag, "")
                            strvalue = strValue.replace(',', '')
                            #try to convert to number, flag if we got a usable value or not
                            try:

                                Value = float(strValue)
                                if(Value != 0):
                                    isValue = True
                            except:
                                isValue = False

                            if isValue:
                                print('Convertable value: '+ strValue + ' found in comment ' + comment.id)
                                #if sucessful convert and comment
                                #Get FX Rates
                                requestURL = 'http://query.yahooapis.com/v1/public/yql?q=select * from yahoo.finance.xchange where pair in ("'+Base+'USD","' +Base+'EUR", "'+Base+'GBP","'+Base+'CAD","'+Base+'AUD","'+Base+'JPY","'+Base+'BTC")&env=store://datatables.org/alltableswithkeys'
                                try:
                                    #Make call to yahoo and convert returned xml to json dictionary
                                    RatesDictionary = XmlToDictionary(requestURL)
                                    #print(RatesDictionary)
                                    print('Got fx rates from Yahoo')
                                except:
                                    print('Something went wrong getting the FX rates')
                                    #exit loop of words
                                    break
                                #Extract Rates
                                USDRt = float(RatesDictionary.get("query").get("results").get("rate")[0]["Rate"])
                                EURRt = float(RatesDictionary.get("query").get("results").get("rate")[1]["Rate"])
                                GBPRt = float(RatesDictionary.get("query").get("results").get("rate")[2]["Rate"])
                                CADRt = float(RatesDictionary.get("query").get("results").get("rate")[3]["Rate"])
                                AUDRt = float(RatesDictionary.get("query").get("results").get("rate")[4]["Rate"])
                                JPYRt = float(RatesDictionary.get("query").get("results").get("rate")[5]["Rate"])
                                BTCRt = float(RatesDictionary.get("query").get("results").get("rate")[6]["Rate"])

                                #Format values with comma seperators and decimals
                                strValue = str(locale.format("%.2f", Value, grouping=True))
                                USDAmt = locale.format("%.2f", USDRt * Value, grouping=True)
                                EURAmt = locale.format("%.2f", EURRt * Value, grouping=True)
                                GBPAmt = locale.format("%.2f", GBPRt * Value, grouping=True)
                                CADAmt = locale.format("%.2f", CADRt * Value, grouping=True)
                                AUDAmt = locale.format("%.2f", AUDRt * Value, grouping=True)
                                JPYAmt = locale.format("%.2f", JPYRt * Value, grouping=True)
                                BTCAmt = locale.format("%.4f", BTCRt * Value, grouping=True)

                                #print(USDAmt)
                                #print(EURAmt)
                                #print(GBPAmt)
                                #print(CADAmt)
                                #print(AUDAmt)
                                #print(BTCAmt)

                                #Build comment
                                head = "Hi, here is **" + strValue + " " + Base +"** converted into...\n\n***\n\n"
                                body1 = "**USD:** " + str(USDAmt) + " **@Rate:** " + str(USDRt) +"\n\n **EUR:** " + str(EURAmt) + " **@Rate:** " + str(EURRt) +"\n\n **GBP:** " + str(GBPAmt) + " **@Rate:** " + str(GBPRt)
                                body2 = "\n\n **CAD:** " + str(CADAmt) + " **@Rate:** " + str(CADRt) +"\n\n **AUD:** " + str(AUDAmt) + " **@Rate:** " + str(AUDRt) +"\n\n **JPY:** " + str(JPYAmt) + " **@Rate:** " + str(JPYRt) + "\n\n **BitCoin:** " + str(BTCAmt) + " **@Rate:** " + str(BTCRt)
                                tail = "\n\n***\n\nI am a bot. You can provide feedback in my subreddit: /r/BOTSUBREDDIT"

                                try:
                                    #Try to reply and log that we already replied to the comment both in the list and the text file
                                    comment.reply(head + body1 + body2 + tail)
                                    print("Replied to comment " + comment.id)
                                    AlreadyDone.append(comment.id)
                                    try:
                                        with open(DoneFile, "a") as myFile:
                                            myFile.write(comment.id + "\n")
                                    finally:
                                        myFile.close()
                                except:
                                    print('Reddit cool down - Posting too often')
                                    print('Sleeping for 8 mins')
                                    time.sleep(550)
                                    #Try again
                                    comment.reply(head + body1 + body2 + tail)
                                    print("Replied to comment " + comment.id)
                                    AlreadyDone.append(comment.id)
                                    try:
                                        with open(DoneFile, "a") as myFile:
                                            myFile.write(comment.id + "\n")
                                    finally:
                                        myFile.close()
        else:
            #We have already replied
            print('We have already replied to comment ' + comment.id)
    #Sleep 5 mins
    print("Finished checking comments - Sleeping 5 mins")
    time.sleep(30)