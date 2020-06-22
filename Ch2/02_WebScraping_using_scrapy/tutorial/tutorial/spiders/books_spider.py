import scrapy

class BookSpider(scrapy.Spider):
    name = "books"

    start_urls = ["http://books.toscrape.com/"]

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

    def parse_book(self, response, cat_name):
        title = response.css(".product_main h1::text").get()

        price = response.css(".product_main .price_color::text").get()

        in_stocks = response.css(".product_main .instock.availability::text").getall()
        in_stock = "".join(s.strip() for s in in_stocks)

        star_rating = response.xpath("//div[contains(@class, 'product_main')]//p[contains(@class, 'star-rating')]/@class").get()
        star_rating = star_rating.split()[1]

        yield {
            "title": title,
            "price": price,
            "stock": in_stock,
            "rating": star_rating,
            "category": cat_name
        }
