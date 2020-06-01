# Building a book scraper using Scrapy

Scrapy is a python framework for scraping and crawling websites. This tutorial demonstrates the use
of scrapy to quickly mine a large amount of data from a demo website
[books.toscrape.com](http://books.toscrape.com/).

## Installation

```bash
pip install Scrapy
```

Refer the [documentation](https://docs.scrapy.org/en/latest/intro/install.html) for advanced
installation instructions.

## Tutorial

### Set-Up

First, we need to start a new scrapy project.

```
scrapy startproject tutorial
```

Scrapy auto-generates a few boilerplate files. The directory structure should look like the
following.

```
.
└── tutorial
    ├── scrapy.cfg
    └── tutorial
        ├── __init__.py
        ├── items.py
        ├── middlewares.py
        ├── pipelines.py
        ├── settings.py
        └── spiders
            └── __init__.py
```

Now enter the base project directory `cd tutorial`.

### A Spider

We will now create a new spider inside `tutorial/spiders`. A spider is nothing but a python class
which inherits from the `scrapy.Spider` class. Each spider has a unique `name` which is used when
running the spider and a `start_urls` which a list of URLs the spider starts crawling as soon as it
is run; we will set `start_urls` to `["http://books.toscrape.com/"]` which is the website we want to
scrape. Create a new file at `tutorial/spiders/books_spider.py` which will have our spider, with the
following content.

```python
import scrapy

class BookSpider(scrapy.Spider):
    name = "books"

    start_urls = ["http://books.toscrape.com/"]
```

When a spider is run, it starts by executing the `parse` function of it on all the `start_urls`. The
`parse` function has a parameter named `response` which stores all information about the fetched
page. `response.url` contains URL of the currently fetched page. Lets print the URL in the fetch
function and see what it does. (The following code should be inside the BookSpider defined earlier.

```python
    def parse(self, response):
        print(response.url)
```

Let's now run the spider. Go to base project directory (`tutorial`) and run
(Note that `books` is the name we gave the spider inside the BookSpider class)
```bash
scrapy crawl books
```
You will see lots of text output, try to find `http://books.toscrape.com/` in one of the lines.

### CSS and XPath selectors

Now, lets focus on actually extracting the content out of the website. If you have ever used CSS,
you will know about selectors which are used to apply style to specific elements. We can use the
same type of selectors to extract data from specific elements. This can be done by using
`response.css(".css selector here")` and then use `getall()` or `get()` function of the CSS object
to actually get the element. You can use `::text` in the selector to get the text contained in the
required element. To get a specific property of the element, say `href`, use `attrib["href"]` on the
object returned by `response.css`.

A more powerful type of selectors are XPath selectors. [Here](https://devhints.io/xpath) is
a cheat-sheet for XPath and [here](https://www.guru99.com/xpath-selenium.html) is a more complete
tutorial. A summary of XPath selectors that will be used in this tutorial are:
 - `//element`: Get all elements of type `element` anywhere in the DOM.
 - `element[@class='classname']]`: Get only elements of type `element` and of class `classname`.
   Note the class is matched entirely, if a element is of class `class1 class2`, a `@class='class1'`
   will not match it.
 - `element[contains(@class, 'classname')]`: Get elements of type `element` whose `class` contains
   `classname` anywhere.
 - `element/text()`: Get the text contained inside elements.
 - `element/@href`: Get the `href` attribute (can be replace with any attribute)
 - `element1/element2`: Get `element2` which a direct child of `element1`

### Extracting Data

Let's take a look at the website we want to scrape. It has a sidebar which shows the list of all
categories and on the right we can see all books.

The approach used in this tutorial is going to each of the categories and scraping all books inside
them.

A great tool to test and experiment with selectors in real time is the **Scrapy shell**. Launch the
scrapy shell for website of interest using the following command.

```bash
scrapy shell "http://books.toscrape.com/"
```
(Pro tip: have IPython installed to get a better scrapy shell experience)

From the shell, you can view the exact response it received using `view(response)` (make sure you do
this for any website you want to scrape before proceeding, the website may look different to your
browser and scrapy since scrapy does not have JavaScript by default).

Now, let's see how to select the list of categories. We will use the ever useful *Inspect Element*
tool. It can be seen in the source that the category list is in a `div` of class `side_categories`.
This div contains an unordered list whose only element contains another unordered list! The second
`ul` is the one we want since each element of this contains an anchor tag with the URL to each
category. Thus, the XPaths are as follows (you can experiment with XPaths in the scrapy shell till
you get the output you need).

```python
        cat_names = response.xpath("//div[@class='side_categories']/ul/li/ul/li/a/text()").getall()
        cat_urls = response.xpath("//div[@class='side_categories']/ul/li/ul/li/a/@href").getall()
```
`cat_names` stores the list of all categories and `cat_urls` the corresponding URLs. We can iterate
over these using zip. There is one issue though, the URLs are relative to the current URL; to fix
this, we use `response.urljoin` to get the absolute URL. Now that we have the URLs, we need a way to
scrape them separately, the `parse` function is specifically made to get the list of categories;
hence, we need a separate function which will parse all books in a category - we call this function
`parse_category`. To tell scrapy to parse a particular URL, we need to create an object of
`scrapy.Request` and return it. Since we have a list of URLs to return, we'll use `yield` instead of
return to return multiple Requests to scrapy. A `scrapy.Request` object required two parameters -
the URL and the function to pass the handle to after a response is received, called `callback`. We
  use another parameter `cb_kwargs` to pass additional parameters to the callback function instead
of just the response. Here is the `parse` function after adding all the above mentioned features.

```python
    def parse(self, response):
        num_cats_to_parse = 5
        cat_names = response.xpath("//div[@class='side_categories']/ul/li/ul/li/a/text()").getall()
        cat_urls = response.xpath("//div[@class='side_categories']/ul/li/ul/li/a/@href").getall()
        for _, name, url in zip(range(num_cats_to_parse), cat_names, cat_urls):
            name = name.strip()
            url = response.urljoin(url)
            yield scrapy.Request(url,
                                 callback=self.parse_category,
                                 cb_kwargs=dict(cat_name=name))
```
Since there are quite a few categories, we limit the number of categories crawled.…

Now, let's scrape all the books in a category which will be done inside the `parse_category`
function. You can use scrapy shell again on one of the category URLs to build selectors
interactively. Here, we can see that each book is inside an `article` of class `product_pod`, which
has a `h3` containing an anchor tag linking to the book's URL. Thus, the line to get all books will
be as follows.

```python
        book_urls = response.xpath("//article[@class='product_pod']/h3/a/@href").getall()
```
Now we can loop through the book URLs and `yield` a `scrapy.Request` for each URL with the callback
as a new function `parse_book` which we will define later. You would have noticed that some
categories have too many books to be displayed in one page and as such they are paginated i.e.,
separated into pages and there's a `next` button near the bottom of the page. After `yield`ing all
the requests for books we find the `next` button and get its URL which is then used to `yield`
another request but with the callback being `parse_category` (which is nothing but a recursion).
The entire code for this function is as follows.

```python
    def parse_category(self, response, cat_name):
        book_urls = response.xpath("//article[@class='product_pod']/h3/a/@href").getall()

        for book_url in book_urls:
            book_url = response.urljoin(book_url)
            yield scrapy.Request(book_url, callback=self.parse_book,
                                 cb_kwargs=dict(cat_name=cat_name))

        next_button = response.css(".next a")
        if next_button:
            next_url = next_button.attrib["href"]
            next_url = response.urljoin(next_url)
            yield scrapy.Request(next_url,
                                 callback=self.parse_category,
                                 cb_kwargs=dict(cat_name=cat_name))
```

Finally, let's write the `parse_book` function to scrape each book. For the purposes of this
tutorial, we will only scrape the title, price, stock information and star rating. You can use the
scrapy shell to build selectors for them. Getting title and price is trivial. The `instock` selector
gives a list of strings which mostly consist of spaces and newline with the actual information
contained in the middle, thus we use `strip` and `join` to get the required information. Obtaining
the star rating is tricky since that information is only contained in the class name, thus we use
XPath to get the class name and then select the second word in that. Finally, we return the required
information in a dictionary, the reason for this is that scrapy considers these dictionaries as
`items`. This allows you to directly export the data to a JSON using `-o output.json` options while
running the spider. The main reason to return `items` is to use scrapy pipelines to programmatically
process the data. For example, you could write a pipeline to automatically insert the data into
a database or write it to a file.

### Saving Data using a Pipeline

After a spider yields an item, it goes to the item pipeline where each it is processed sequentially
by all the pipeline objects. Each object in the pipeline is just a python class that implements
a few special functions including `process_item`, `open_spider` (optional) and `close_spider`
(optional).

Let us now create a pipeline to save the data to a CSV file. We will be using the built-in csv
module in python, specifically the `DictWriter` object from that module. Refer the
[documentation](https://docs.python.org/3/library/csv.html#csv.DictWriter) for more details.

Open `tutorial/pipelines.py` (it would have been auto-generated), delete the existing example
pipeline and replace with the following.

```python
import csv

class BookCsvPipeline():
    def open_spider(self, spider):
        self.file = open("output.csv", "at")
        fieldnames = ["title",
                      "price",
                      "stock",
                      "rating",
                      "category"]
        self.writer = csv.DictWriter(self.file, fieldnames=fieldnames)
        if self.file.tell() == 0:
            self.writer.writeheader()

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        self.writer.writerow(item)
        return item
```
Note that the pipeline's `process_item` needs to return the `item` it processes so that the
next processor in the pipeline can process it.

Before running the spider, the pipeline that we just created needs to be enabled. Open
`tutorial/settings.py` (go through this file once, it contains some very useful options)
and look for `ITEM_PIPELINES`, uncomment it and replace with the following.
```python
ITEM_PIPELINES = {
    'tutorial.pipelines.BookCsvPipeline': 300,
}
```
The `300` indicates its priority in the pipeline with `0` being the highest priority and `1000`
being the lowest.

Now we are ready to run the spider.
```
scrapy crawl books -o output.json
```
This will take a few seconds with lots of output. After it has finished executing, you can find
`output.json` and `output.csv` in the same folder from where you ran it. The CSV should contain 163
rows if `num_cats_to_parse` was set to 5 (excluding the header).

Now you have a scrapy crawler which uses most of the useful functionalities provided by scrapy.
