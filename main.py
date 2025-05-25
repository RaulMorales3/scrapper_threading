import time

from multiprocessing import Queue

from config import URL_SP_500, URL_YAHOO_FINANCE, XPATH_YAHOO_FINANCE
from workers.wiki_worker import WikiWorker
from workers.yahoo_finance_worker import YahooFinanceScheduler

TOTAL_THREADS = 8



def main():
    symbol_queue = Queue()
    time_scrapper_start = time.time()
    worker = WikiWorker(url=URL_SP_500)
    companies = [company for company in worker.get_companies_500SP()]
    yahoo_threads = []
    for _ in range(TOTAL_THREADS):
        yahoo_scheduler = YahooFinanceScheduler(queue=symbol_queue)
        yahoo_threads.append(yahoo_scheduler)

    for company in companies[:10]:
        print("queueing", company)
        symbol_queue.put(company)

    for _ in range(len(yahoo_threads)):
        symbol_queue.put("done")

    for worker in yahoo_threads:
        worker.join()

    print(f"scrapper time: {time.time() - time_scrapper_start}")


if __name__ == "__main__":
    main()
