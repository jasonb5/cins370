#! /usr/bin/env python2

# Created by: Jason Boutte
# CINS 370 
# Spring 2015
# Phase 4 

# Required libraries 
# python-amazon-simple-product-api
#  https://github.com/yoavaviram/python-amazon-simple-product-api
# faker
#  https://github.com/joke2k/faker

# Python version 2.7.9

import sys
import time
import csv
import string
import random
import datetime
import argparse
from faker import Faker
from amazon.api import AmazonAPI

# returns the first and last token of the author 
def parse_author(author):
  tokens = string.split(author, ' ')
  return (tokens[0], tokens[len(tokens)-1])

# generates an entry for stockSchema
def generate_stock(index, list_price, price):
  aval = bool(random.randint(0,1))

  aval_date = None

  # make up date for availabilty 
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

  # if there's no list price we make up a mark up
  # guarantee a minimum of 0.01
  if not list_price:
    mark_up = random.random()+0.01
  else:
    # try to infer a mark_up from list_price and price
    mark_up = abs(float(list_price)/float(price)-1);
    # guarantee minimum of 0.01
    if mark_up < 0.01:
      mark_up = random.random()+0.01

  # format to 2 decimal marks 
  mark_up = '%.2f'%(mark_up)

  # return stock tuple
  return (index, aval, aval_date, digi, paper, hard, ordered, cost, mark_up, 0.0)

# generates entry for bookschema
def generate_book(isbn, index, title, pub_date, pub, author, genre):
  # toss entry if there's no isbn
  if isbn == '': 
    return None

  # create pub_date if it doesn't exist
  if pub_date == 'None':
    pub_date = datetime.date.today()

  return (isbn, index, title, pub_date, pub, author, genre)

# generates entry for authorschema
def generate_author(index, author):
  parsed = parse_author(author)

  return (index, parsed[0], parsed[1])

# generates entry for customerschema
def generate_customer(fake, index):
  user = fake.user_name()
  fname = fake.first_name()
  lname = fake.last_name()
  addr = fake.address()
  city = fake.city()
  state = fake.state()
  postc = fake.postcode()
  email = fake.email()

  return (index, user, fname, lname, addr, city, state, postc, email)

#generates entry for creditcard
def generate_creditcard(fake, index, fname, lname):
  cc_num = fake.credit_card_number()
  cc_exp = datetime.date.today() + datetime.timedelta(3650)
  cc_key = fake.credit_card_security_code()

  return (cc_num, index, fname, lname, cc_exp, cc_key)

#generates entry for reviewschema
def generate_review(fake, index):
  review_cus = random.randint(0, 499)
  review_rating = random.randint(0, 5)
  review_text = fake.text()

  return (review_cus, index, review_rating, review_text)

def format_csv():
  fake = Faker()

  f = open('data.csv', 'r')
  reader = csv.reader(f)

  book_dict = {}
  stock_list = []
  author_dict = {}

  book_index = 0
  author_index = 0

  print("Generating CSV files")

  # iterate over each input line
  for row in reader:
    # generate new author if not exist
    if not row[2] in author_dict:
      author_dict[row[2]] = generate_author(author_index, row[2])
      author_index += 1

    author_id = author_dict[row[2]][0]

    # generate a new book
    book = generate_book(row[0], book_index, row[1], row[3], row[4], author_id, row[5])

    # skip if there's an errro generating book
    if book == None: 
      continue
    else:
      # generate stock and increment book index
      stock = generate_stock(book_index, row[6], row[7]) 

      book_index += 1

    # check for duplicate isbn entries, occasional bug
    if not book[0] in book_dict:
      book_dict[book[0]] = book   

      stock_list.append(stock)

  # write book to csv file
  f = open('books.csv', 'wb')
  writer = csv.writer(f)

  for isbn_key, book in book_dict.iteritems():
    writer.writerow(book)
  
  print("Wrote " + str(len(book_dict)) + " books to books.csv") 

  # write authors to csv file
  f = open('authors.csv', 'wb')
  writer = csv.writer(f)

  for author, parsed in author_dict.iteritems():
    writer.writerow(parsed)

  print("Wrote " + str(len(author_dict)) + " authors to authors.csv");

  # write stock to csv file
  f = open('stock.csv', 'wb')
  writer = csv.writer(f)

  for stock in stock_list:
    writer.writerow(stock)

  print("Wrote " + str(len(stock_list)) + " items to stock stock.csv")

  # write customer and creditcard csv files
  f = open('customers.csv', 'wb')
  writer = csv.writer(f)

  f1 = open('cc.csv', 'wb')
  cc_writer = csv.writer(f1)

  cc_count = 0

  for x in range(500):
    # generate a new customer
    customer = generate_customer(fake, x)
    writer.writerow(customer)

    # generate 0 to 2 credit cards per customer
    for y in range(random.randint(0, 2)):
      cc_count += 1
      cc = generate_creditcard(fake, x, customer[2], customer[3])
      cc_writer.writerow(cc)

  print("Wrote 500 customers to customers.csv")
  print("Wrote " + str(cc_count) + " credit cards to cc.csv")

  # write customer reviews
  f = open('reviews.csv', 'wb')
  writer = csv.writer(f)

  # guard against multiple reviews by same customer
  cust_review = {}
 
  # each book has a chance for reviews
  for isbn_key, book in book_dict.iteritems():
    # chance to review between 0 and 30 books
    review_num = random.randint(0, 30)
   
    for y in range(review_num):
      cust_id = random.randint(0, 500)

      review = generate_review(fake, book[1])

      if not (review[0], review[1]) in cust_review:
        cust_review[(review[0], review[1])] = review
        writer.writerow(review)

  print("Wrote " + str(len(cust_review)) + " customer reviews to reviews.csv")

def generate_csv():
  # initialize amazon api with access key, secret key, and associate tag
  amazon = AmazonAPI('AKIAJPT5M67Z5DB6R3XA', 'P0ekhRiDVDC2xeJa4fZz1P5qHY/B2Qig71G6wZB3', 'thedeepdark-20')

  print("Querying amazon API")
  # returns available book subjects
  subjects = amazon.browse_node_lookup(BrowseNodeId=1000)

  f = open('data.csv', 'wb')
  writer = csv.writer(f)

  print("\tReturned with " + str(len(subjects[0].children)) + " subjects")

  # creates books and author lists
  for subject in subjects:
    for genre in subject.children:
      # skip calendar entries
      if genre.name.text == 'Calendars': continue

      # returns first 1000 entries in each subject
      # Amazons api limits the number of return pages to 10
      # with 10 items on each for a maximum of 100 items 
      books = amazon.search_n(100, Condition='All', BrowseNode=genre.id, SearchIndex='Books', MaxQPS=0.9)

      print("Queried " + genre.name + ", returned " + str(len(books)) + " books")

      failed = 0

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
        except UnicodeEncodeError:
          failed += 1

      print("\tDone processing books, failed to convert unicode characters " + str(failed) + " times")

      time.sleep(5)

parser = argparse.ArgumentParser()
parser.add_argument('-g', action='store_true')

args = parser.parse_args()

if args.g:
  generate_csv()
else:
  format_csv()
