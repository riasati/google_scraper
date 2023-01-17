import requests
from lxml import html, etree
from pprint import pprint
from tqdm import tqdm
import os


def simple_google_search(query):
    query = query.replace(' ', '+')
    URL = f'https://google.com/search?q={query}&start=1&num=50'
    # URL = f'https://google.com/search?q={query}&start=1&num=10'
    # desktop user-agent
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

    headers = {"user-agent": USER_AGENT}
    resp = requests.get(URL, headers=headers)
    if resp.status_code == 200:
        tree = html.fromstring(resp.content)
        return tree

    return None


def simple_google_image_search(query):
    query = query.replace(' ', '+')
    URL = f"https://www.google.com/search?q={query}&tbm=isch&num=100"
    # URL = f"https://www.google.com/search?q={query}&tbm=isch&num=10"

    # desktop user-agent
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

    headers = {"user-agent": USER_AGENT}
    resp = requests.get(URL, headers=headers)
    # print(resp.headers)
    if resp.status_code == 200:
        # print(resp.content.decode("UTF-8"))
        tree = html.fromstring(resp.content.decode("UTF-8"))
        # a = etree.tostring(tree, pretty_print=True)
        return tree

    return None


def get_result_from_page(tree):
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
            "title": title.encode(encoding='utf-8').decode("UTF-8").replace('\u200c', ''),
            "link": link,
            "description": description.encode(encoding='utf-8').decode("UTF-8").replace('\u200c', '')
        })
    return return_list


def get_result_from_image_page(tree):
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
            "title": title.encode(encoding='utf-8').decode("UTF-8").replace('\u200c', ''),
            "image_data": image_data,
            "page_url": page_url
        })
    return return_list


def download_web_page(url, threaded=False):
    from urllib.parse import urlparse
    hostname = urlparse(url).hostname
    path = urlparse(url).path.replace("/", ".")
    from datetime import datetime
    # date_time = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    date_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    project_name = f'{hostname}{path}_{date_time}'
    download_folder = './path'
    from pywebcopy import save_webpage
    if threaded:
        kwargs = {'bypass_robots': True, 'project_name': project_name, 'open_in_browser': False, 'threaded': True}
    else:
        kwargs = {'bypass_robots': True, 'project_name': project_name, 'open_in_browser': False}
    save_webpage(url, download_folder, **kwargs)


# download_web_page("https://www.simplified.guide/python/get-host-name-from-url", threaded=False)


def download_image_of_query(query, query_results, continue_counter=1):
    import urllib.request
    if not os.path.exists(query):
        os.mkdir(query)
    for query_result in tqdm(query_results):
        image_url = query_result["image_data"]
        if image_url.startswith("data") or image_url.startswith("NULL"):
            continue
        # filename = f'{str(continue_counter)}.jpg'
        urllib.request.urlretrieve(query_result["image_data"], os.path.join(query, f'{str(continue_counter)}.jpg'))
        continue_counter += 1


def insert_search_results(search_results, query):
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.google
    search_collection = db.search
    for search_result in search_results:
        search_result["query"] = query
    new_result = search_collection.insert_many(search_results)
    # pprint(new_result)
    client.close()


def insert_image_results(image_results, query):
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.google
    search_collection = db.image
    for image_result in image_results:
        image_result["query"] = query
    # image_results = [image_result["query"] = query for image_result in image_results]
    new_result = search_collection.insert_many(image_results)
    pprint(new_result.inserted_ids)
    client.close()


def delete_data_in_collection(collection_name):
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.google
    one_collection = db[collection_name]
    result = one_collection.delete_many({})
    pprint(result)
    client.close()


# tree = simple_google_image_search("ایران")
# image_result = get_result_from_image_page(tree)
# pprint(image_result)
# insert_image_results(image_result, "ایران")

# tree = simple_google_search("اسلام")
# search_results = get_result_from_page(tree)
# pprint(search_results)
# insert_search_results(search_results, "ایران")

# tree = simple_google_image_search("محمد")
# image_result = get_result_from_image_page(tree)
# download_image_of_query("محمد", image_result)

# url = "https://vigiato.net/p/153846"
# download_web_page(url, threaded=True)

# delete_data_in_collection("search")