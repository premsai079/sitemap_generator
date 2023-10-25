import scrapy
import argparse
import os
import json
from urllib.parse import urlparse

class LinkScraperSpider(scrapy.Spider):
    name = 'link_scraper'

    def __init__(self, start_url, max_pages=None, json_output_path=None, *args, **kwargs):
        super(LinkScraperSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.max_pages = max_pages
        self.visited = set()
        self.domain = urlparse(start_url).netloc
        self.json_output_path = json_output_path
        self.urls = []

    def parse(self, response):
        if self.max_pages is None or len(self.visited) < self.max_pages:
            self.visited.add(response.url)
            self.urls.append({"url": response.url})

            # Extract links and follow
            for link in response.css('a::attr(href)').extract():
                next_url = response.urljoin(link)
                next_domain = urlparse(next_url).netloc

                # Only follow links that are within the same domain
                if next_domain == self.domain:
                    yield response.follow(next_url, self.parse)
        else:
            self.crawler.engine.close_spider(self, 'Max pages reached')

    def closed(self, reason):
        # Save to JSON file when spider is closed
        with open(self.json_output_path, 'w') as f:
            json.dump(self.urls, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sitemap for a given website.")
    parser.add_argument("--start-url", help="The website URL.")
    parser.add_argument("--max-pages", type=int, help="Maximum number of pages to crawl.", default=None)
    parser.add_argument("--json-output-path", help="Path to the JSON output file.")
    args = parser.parse_args()

    # Run Scrapy spider
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(LinkScraperSpider, start_url=args.start_url, max_pages=args.max_pages, json_output_path=args.json_output_path)
    process.start()
