#! /usr/bin/env python2

import time
import csv
import string
import random
import datetime
from amazon.api import AmazonAPI

def parse_author(author):
	tokens = string.split(author, ' ')
	return (tokens[0], tokens[len(tokens)-1])

amazon = AmazonAPI('AKIAJPT5M67Z5DB6R3XA', 'P0ekhRiDVDC2xeJa4fZz1P5qHY/B2Qig71G6wZB3', 'thedeepdark-20')

subjects = amazon.browse_node_lookup(BrowseNodeId=1000)

book_list = []
price_list = []
author_dict = {}
stock_list = []

book_index = 0
author_index = 0
stock_index = 0

# creates books and author lists
for subject in subjects:
	for genre in subject.children:
		if genre.name.text == 'Calendars': continue
		books = amazon.search_n(5000, BrowseNode=genre.id, SearchIndex='Books')

		for book in books:
			b_isbn = book.isbn
			b_id = book_index
			book_index += 1
			b_title = book.title
			b_pub_date = str(book.publication_date)
			b_genre = genre.name
			b_publisher = book.publisher
			b_list_price = book.list_price[0]
			b_price = book.price_and_currency[0]

			if len(book.authors) == 0:
				break

			if not book.authors[0] in author_dict:
				author_dict[book.authors[0]] = author_index
				author_index += 1

			book_item = [b_isbn, b_id, b_title, b_pub_date, b_publisher, b_genre]

			book_list.append(book_item)

			price_item = [b_price, b_list_price]

			price_list.append(price_item)

			#for x in range(len(book_item)):
			#	if isinstance(book_item[x], str):
			#		book_item[x] = unicode(book_item[x], 'utf-8')

		time.sleep(5)

for book in book_list:
	aval = bool(random.randint(0, 1))
	
	aval_date = None
	
	if not aval:
		curr = datetime.date.today()
		curr += datetime.timedelta(random.randint(1, 30))
		aval_date = curr

	digi = bool(random.randint(0, 1))

	paper = None
	hard = None
	ordered = None

	if aval:
		paper = random.randint(1, 1000)
		hard = random.randint(1, 500)
	else:
		ordered = random.randint(1, 1000)

	price_item = price_list.index(book[1])	

	b_cost = price_item[0]

	b_markup = 1 - (price_item[1] - price_item[0])

	b_price = None

	stock_item = []
	stock_item.append(stock_index)
	stock_index += 1
	stock_item.append(aval)
	if aval:
		stock_item.append('')
	else:
		stock_item.append(aval_date)
	stock_item.append(digi)
	if aval:
		stock_item.append(paper)
		stock_item.append(hard)
		stock_item.append('')
	else:
		stock_item.append('')
		stock_item.append('')
		stock_item.append(ordered)

	stock.append(b_cost)
	stock.append(b_markup)
	stock.append('')

	stock_list.append(stock)
