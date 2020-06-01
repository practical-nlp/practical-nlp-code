# -*- coding: utf-8 -*-

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
