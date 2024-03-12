# -*-coding:utf-8-*-
import re, os, sys
import queue, requests
import langid, argparse
import threading, logging
from requests.exceptions import ConnectTimeout,ConnectionError


logger = logging.getLogger("AppName")
formatter = logging.Formatter('%(asctime)s %(levelname)-5s: %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

q = queue.Queue()   # url队列
page_q =queue.Queue()  # 页面
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'

def get_page(keyword,page_q,path, lang):
    links = set()
    while True:
        page = page_q.get()
        url = "https://www.youtube.com/results?sp=EgIoAQ%253D%253D&search_query=" + keyword + 'page='+ str(page)
        try:
            res = requests.get(url, headers={'User-Agent': USER_AGENT}).text
        except (ConnectTimeout,ConnectionError):
            print("不能访问YouTube 检查网络问题")
            res = ''
        # reg = re.compile(r'"url":"/watch\?v=(.*?)","webPageType"', re.S)
        reg = re.compile(r'"title":\{"runs":\[\{"text":"(.*?)"\}.*?"url":"/watch\?v=(.*?)","webPageType"', re.S)
        result = reg.findall(res)
        logger.info(f"第 {page} 页, 共 {len(result)} 条")
        with open (path,'a+') as f:
            for x in result:
                if len(x[1]) < 10 or x[1][:11] in links:
                    continue
                if langid.classify(x[0])[0] != lang:
                    continue
                q.put(x)
                f.write(langid.classify(x[0])[0] +'|' + x[1][:11] + '|' + x[0] + '\n')
                # logger.info(langid.classify(x[0])[0] +' | ' + x[1] + ' | ' + x[0])
            page_q.task_done()

def deduplicate(file):
    with open(file, 'r', encoding='utf-8') as f:
        lines = set(f.readlines())
    with open(file, 'w', encoding='utf-8') as f:
        for l in lines:
            f.write(l)
    logger.info(f"{file} 共 {len(lines)} 视频\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', type=str, default='en', help='See ISO 639-1 codes for supported languages (total: 97).')
    parser.add_argument('--keywords', type=str, default='Trump,Obama', help='Keywords for searching videos.')
    parser.add_argument('--save_dir', type=str, default='./list', help='Path to save channel lists.')
    parser.add_argument('--pages', type=int, default=200, help='Each page has a maximum of 20 videos.')
    parser.add_argument('--threads', type=int, default=16, help='Multithreads.')
    args = parser.parse_args()

    keywords=args.keywords.split(',')

    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir, exist_ok=True)

    for keyword in keywords:
        path = os.path.join(args.save_dir, keyword+'.txt')
        logger.info(f"{keyword} 开始解析网页")
        for page in range(1,args.pages):
            page_q.put(page)
        for y in range(args.threads):
            t = threading.Thread(target=get_page, args=(keyword, page_q, path, args.lang))
            t.setDaemon(True)
            t.start()
        page_q.join()
        if os.path.exists(path):
            deduplicate(path)

if __name__ == '__main__':
    main()