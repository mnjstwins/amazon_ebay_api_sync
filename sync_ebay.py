#!/usr/bin/python
#
# sync_ebay.py
#
# uses a MySQL database to connect to ebay's search API, and return results to the database
#
# 2014.05.10 eXpressTek Inc, initial release (Warren Kenner)
#

class ConnectionError(Exception):
    pass

from ebaysdk.finding import Connection as finding
from ebaysdk.shopping import Connection as shopping
import json
import time
import credentials
import MySQLdb
import sys
import inspect
import subprocess

debug = False

#do a version check
version_check = subprocess.check_output(['git', 'diff', 'origin/master'])
if (version_check.strip() != ""):
    print "WARN: This software may be out of date. Please see about updating"

#make a timestamp
def stamp():
  return time.strftime("%a, %d %b %Y %H:%M:%S +0000",time.gmtime())

#get the credentials for the database from the db.conf file. (the import credentials is the actual function to do this.)
creds = credentials.load_file_config()

#connect to the database
db = MySQLdb.connect(host=creds['host'], port=int(creds['port']), user=creds['user'], passwd=creds['password'], db=creds['database'])

#initate a cursor
cursor = db.cursor()

######################################
# grab the ebay credentials from the config table of the database
######################################
cursor.execute("SELECT * FROM sync_config WHERE Sync_Type LIKE 'ebay'")

#get the return values
dbreturn = cursor.fetchall()

#unpack from the array and then unpack from tuple
key_tuple = dbreturn[0]
synctype, syncvalue, synckey = key_tuple

#reconstitute the json to a dictionary 
keydict = json.loads(synckey)

######################################
# grab the searches from the database
######################################
cursor.execute("SELECT * FROM sync_searches WHERE search_poller LIKE 'ebay'")

#get the return values
search_return = cursor.fetchall()
if search_return is 0L:
    print "{0} No searches to run, exiting".format(stamp())
    sys.exit(0)

#run for each search returned
for search_tuple in search_return:
    
    # unpack search tuple to get search text
    search_num, search_poller, search_text = search_tuple
    
    # encode search text as string
    search_text = search_text.encode('ascii','ignore')
    try:
        # establish connection using key obtained from database
        find = finding(appid=keydict['key'])
        
        #execute the search once connected. er
        find.execute('findItemsAdvanced', {'keywords': search_text, 'paginationInput':{'entriesPerPage':100, 'pageNumber':1}, 'itemFilter':{'name':'ListingType','value':'AuctionWithBIN'}, 'itemFilter':{'name':'ListingType','value':'FixedPrice'}})
    
    except ConnectionError as e:
        print "got a Connection Error"
        raise e
        sys.exit(0)
    #get the response dictionary from the call
    mydict = find.response_dict()
    if debug:
        print "mydict: "
        print mydict

    #unpack the return items and map to relevant Database fields
    items = mydict['searchResult']['item']
    item_ids = []
    for item in items:
        item_ids.append(item['itemId']['value'])
    if debug:
        print "Item IDs: "
        print item_ids
    pos = 0
    listNum = 0
    separated_item_ids = []
    separated_item_ids.append([])
    for item_id in item_ids:
        if (pos % 20 == 0) and (pos != 0):
            listNum = listNum + 1
            separated_item_ids.append([])
        separated_item_ids[listNum].append(item_id)
        pos = pos + 1
    specifics = {}
    try: 
        for item_id_list in separated_item_ids:
            shop = shopping(appid=keydict['key'])
            shop.execute('GetMultipleItems', {'itemID':item_id_list, 'includeSelector':'Details, ItemSpecifics, Description'})
            if debug:
                print dir(shop)
            specifics_partial_dict = shop.response_dict()
            if specifics_partial_dict is None:
                print "Unable to get specifics for some reason, exiting"
                sys.exit(0)
            if debug:
                print specifics_partial_dict
            specifics_dict = specifics_partial_dict['Item']
            for item in specifics_dict:
                specifics[item['ItemID']['value']] = item
    except ConnectionError as e:
        print "got a Connection Error"
        raise e
        sys.exit(0)
    for item in items:
        sku = item['itemId']['value']
        poller_type = "ebay"
        seller = ''
        images = item['galleryURL']['value']
        lastUpdate = time.time()
        category = item['primaryCategory']['categoryName']['value']
        price = item['sellingStatus']['currentPrice']['value']
        currency = item['sellingStatus']['currentPrice']['currencyId']['value']
        title = item['title']['value']
        url = item['viewItemURL']['value']
        specifics_object = specifics[sku]
        if "ItemSpecifics" in specifics_object.keys():
            item_specifics_list = specifics_object['ItemSpecifics']['NameValueList']
            item_specifics = ""
            for item_specs in item_specifics_list:
                try:
                    item_specifics = item_specifics + item_specs['Name']['value']+" : "+item_specs['Value']['value']+", "
                except TypeError as e:
                    item_specifics = item_specs
            if isinstance(item_specifics, basestring):
                item_specifics = item_specifics[:-2]
            item['specifics'] = specifics_object
        description = ''
        if "Description" in specifics_object.keys():
            description = specifics_object["Description"]
        
        #print progress of SKU's with timestamp
        print "{1} got_sku={0}".format(sku,stamp()),
        
        # check if its already in the database
        recordNum = cursor.execute("SELECT * FROM sync_ebay WHERE ItemID LIKE '{0}'".format(sku))

        # initialize the sql_statement
        sql_statement = ''

        # if its not in the database, INSERT the new record
        if (recordNum == 0L) or (recordNum == 0):
        
            print "sku does NOT exist INSERT'ing new entry"
            sql_statement = u"""INSERT INTO sync_ebay (ItemID, Type, Images, LastUpdate, Category, Price, CurrencyID, Description, Title, Seller, URL, ItemSpecifics) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', {5}, '{6}', '{7}', '{8}', '{9}', '{10}','{11}')""".format(
             sku,
             db.escape_string(poller_type),
             db.escape_string(images),
             lastUpdate,
             db.escape_string(category),
             price,
             db.escape_string(currency),
             db.escape_string(str(description)),
             db.escape_string(title),
             db.escape_string(seller),
             db.escape_string(url),
             db.escape_string(str(item_specifics))
            )

        # else its an existing record and we need to update
        else:
            print "sku does exist UPDATE'ing the EXISTING entry"
            sql_statement = u"""UPDATE sync_ebay SET Type='{0}', Images='{1}', LastUpdate='{2}', Category='{3}', Price={4}, CurrencyID='{5}', Description='{6}', Title='{7}', Seller='{8}', URL='{9}', ItemSpecifics='{10}' WHERE ItemID={11}""".format(
             db.escape_string(poller_type),
             db.escape_string(images),
             lastUpdate,
             db.escape_string(category),
             price,
             db.escape_string(currency),
             db.escape_string(str(description)),
             db.escape_string(title),
             db.escape_string(seller),
             db.escape_string(url),
             db.escape_string(str(item_specifics)),
             sku
            )

#        print "{0} DEBUG: {1}".format(stamp(),sql_statement)
        cursor.execute(sql_statement)

        
print "{0} sync_ebay.py complete".format(stamp())
