from database import DataBase


class Scrape:

    def google_image_search(self, query):
        import requests
        from lxml import html
        query = query.replace(' ', '+')
        URL = f"https://www.google.com/search?q={query}&tbm=isch&num=100"

        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

        headers = {"user-agent": USER_AGENT}
        resp = requests.get(URL, headers=headers)
        if resp.status_code == 200:
            tree = html.fromstring(resp.content.decode("UTF-8"))
            return tree

        return None

    def result_from_image_page(self, tree, query):
        return_list = []
        one_image_divs = tree.xpath("//div[contains(@class, 'isv-r')]")
        for one_image in one_image_divs:
            title_list = one_image.xpath("./h3/text()")
            if len(title_list) == 0:
                title = "NULL"
            else:
                title = " ".join(title_list)
            image_data_list = one_image.xpath("./a[1]//img/@data-src")
            if len(image_data_list) == 0:
                image_data_list = one_image.xpath("./a[1]//img/@src")
                if len(image_data_list) == 0:
                    image_data = "NULL"
                else:
                    image_data = " ".join(image_data_list)
            else:
                image_data = " ".join(image_data_list)
            page_url_list = one_image.xpath("./a[2]/@href")
            if len(page_url_list) == 0:
                page_url = "NULL"
            else:
                page_url = " ".join(page_url_list)
            if title == "NULL" and image_data == "NULL" and page_url == "NULL":
                continue

            return_list.append({
                "query": query,
                "title": title.encode(encoding='utf-8').decode("UTF-8").replace('\u200c', ''),
                "image_data": image_data,
                "page_url": page_url
            })
        return return_list

    def google_search(self, query):
        import requests
        from lxml import html
        query = query.replace(' ', '+')
        URL = f'https://google.com/search?q={query}&start=1&num=50'
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
        headers = {"user-agent": USER_AGENT}
        resp = requests.get(URL, headers=headers)
        if resp.status_code == 200:
            tree = html.fromstring(resp.content)
            return tree
        return None

    def result_from_page(self, tree, query):
        return_list = []
        one_search_divs = tree.xpath("//*[@id='search']//div[contains(@class,'g ') or @class='g']/div[1]")
        for one_search in one_search_divs:
            try:
                top = one_search.xpath("./div[@data-header-feature='0']")
                if len(top) == 0:
                    top = one_search.xpath("./div[1]")[0]
                else:
                    top = top[0]
                title = top.xpath(".//h3//text()")
                title = " ".join(title)
                link = top.xpath(".//a[not(contains("
                                 "@class, 'fl') or contains(@class, 'exp-r') or contains(@href, 'webcache') or contains(@href, "
                                 "'/search?'))]/@href")[0]
            except:
                title = "NULL"
                link = "NULL"
            try:
                bottom = one_search.xpath("./div[@data-content-feature='1']")
                if len(bottom) == 0:
                    bottom = one_search.xpath("./div[2]")[0]
                else:
                    bottom = bottom[0]
                description = bottom.xpath(".//text()")
                description = " ".join(description)
            except:
                description = "NULL"

            if title == "NULL" and description == "NULL":
                continue

            return_list.append({
                "query": query,
                "title": title.encode(encoding='utf-8').decode("UTF-8").replace('\u200c', ''),
                "link": link,
                "description": description.encode(encoding='utf-8').decode("UTF-8").replace('\u200c', '')
            })
        return return_list

    def fill_database(self, collection, query):

        if collection == "image":

            tree = self.google_image_search(query)
            if tree is None:
                return None

            results = self.result_from_image_page(tree, query)
        else:
            tree = self.google_search(query)
            if tree is None:
                return None

            results = self.result_from_page(tree, query)

        db = DataBase(collection)
        db.add_documents(results)

        return results