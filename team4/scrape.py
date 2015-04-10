#! /usr/bin/env python2

import sys
import time
import csv
import string
import random
import datetime
import argparse
from faker import Faker
from amazon.api import AmazonAPI

def parse_author(author):
  tokens = string.split(author, ' ')
  return (tokens[0], tokens[len(tokens)-1])

def generate_stock(index, list_price, price):
  aval = bool(random.randint(0,1))

  aval_date = None

  if not aval:
    t = datetime.date.today()
    t += datetime.timedelta(random.randint(1, 30))
    aval_date = str(t)

  digi = bool(random.randint(0, 1))

  paper = None
  hard = None
  ordered = None

  if aval:
    paper = random.randint(500, 1000)
    hard = random.randint(100, 500)
  else:
    ordered = random.randint(500, 1000)

  cost = price
  
  if not list_price:
    mark_up = 0.0
  else:
    mark_up = round((float(list_price) / float(price))-1, 2)
    mark_up = '%.2f'%(mark_up)

  return [index, aval, aval_date, digi, paper, hard, ordered, cost, mark_up, None]

def format_csv():
  f = open('data.csv', 'r')
  reader = csv.reader(f)

  book_list = []
  stock_list = []
  author_dict = {}

  book_index = 0
  author_index = 0

  for row in reader:
    isbn = row[0]
    title = row[1]
    author = row[2]
    pub_date = row[3]
    pub = row[4]
    genre = row[5]
    list_price = row[6]
    price = row[7]

    if not author in author_dict:
      author_id = author_dict[author] = author_index
      author_index += 1
    else:
      author_id = author_dict[author]

    stock = generate_stock(book_index, list_price, price)
    stock_list.append(stock)

    book = [isbn, book_index, title, pub_date, author_id, genre]
    book_index += 1

    book_list.append(book)

  f = open('book.csv', 'wb')
  writer = csv.writer(f)

  for book in book_list:
    writer.writerow(book)

  f = open('author.csv', 'wb')
  writer = csv.writer(f)

  for author, aid in author_dict.iteritems():
    pauthor = parse_author(author)
    author_item = [aid, pauthor[0], pauthor[1]]
    writer.writerow(author_item)

  f = open('stock.csv', 'wb')
  writer = csv.writer(f)

  for stock in stock_list:
    writer.writerow(stock)

  fake = Faker()

  f = open('customer.csv', 'wb')
  writer = csv.writer(f)

  f1 = open('creditcard.csv', 'wb')
  cc_writer = csv.writer(f1)

  for x in range(500):
    cid = x
    user = fake.user_name()
    fname = fake.first_name()
    lname = fake.last_name()
    addr = fake.address()
    city = fake.city()
    state = fake.state()
    postc = fake.postcode()
    email = fake.email()

    person = [cid, user, fname, lname, addr, city, state, postc, email]
    writer.writerow(person)

    for x in range(random.randint(1, 2)):
      cc_num = fake.credit_card_number()
      cc_cust = x
      cc_fname = fname
      cc_lname = lname
      cc_exp = fake.date()
      cc_key = fake.credit_card_security_code()

      cc = [cc_num, cc_cust, cc_fname, cc_lname, cc_exp, cc_key]
      cc_writer.writerow(cc)

  f = open('reviews.csv', 'wb')
  writer = csv.writer(f)

  for x in range(book_index-1):
    review_num = random.randint(0, 30)
    
    for y in range(review_num):
      review_cus = random.randint(0, 500)
      review_book = x
      review_rating = random.randint(0, 5)
      review_text = fake.text()

      review = [review_cus, review_book, review_rating, review_text]
      writer.writerow(review)

def generate_csv():
  amazon = AmazonAPI('AKIAJPT5M67Z5DB6R3XA', 'P0ekhRiDVDC2xeJa4fZz1P5qHY/B2Qig71G6wZB3', 'thedeepdark-20')

  subjects = amazon.browse_node_lookup(BrowseNodeId=1000)

  f = open('data.csv', 'wb')
  writer = csv.writer(f)

  # creates books and author lists
  for subject in subjects:
    for genre in subject.children:
      if genre.name.text == 'Calendars': continue

      books = amazon.search_n(5000, BrowseNode=genre.id, SearchIndex='Books')

      for book in books:
        b_isbn = book.isbn
        b_title = book.title
        b_pub_date = str(book.publication_date)
        b_genre = genre.name
        b_publisher = book.publisher
        b_list_price = book.list_price[0]
        b_price = book.price_and_currency[0]

        if len(book.authors) == 0:
          break

        book_item = [b_isbn, b_title, book.authors[0], b_pub_date, b_publisher, b_genre, b_list_price, b_price]

        for x in range(len(book_item)):
         if isinstance(book_item[x], str):
           book_item[x] = unicode(book_item[x], 'utf-8')
  
        try:
          writer.writerow(book_item)
        except:
          print("Couldn't write row")

      time.sleep(5)

parser = argparse.ArgumentParser()
parser.add_argument('-g', action='store_true')

args = parser.parse_args()

if args.g:
  generate_csv()
else:
  format_csv()
