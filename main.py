import time

from multiprocessing import Queue

from config import URL_COUNTRIES
from workers.wiki_worker import WikiWorker
from workers.yahoo_finance_worker import YahooFinanceScheduler
from workers.postgres_worker import PostgresMasterScheduler

TOTAL_THREADS = 8
PG_TOTAL_THREADS = 2


def main():
    symbol_queue = Queue()
    pg_queue = Queue()
    time_scrapper_start = time.time()
    worker = WikiWorker(url=URL_COUNTRIES)
    companies = [company for company in worker.get_countries()]

    yahoo_threads = []
    for _ in range(TOTAL_THREADS):
        yahoo_scheduler = YahooFinanceScheduler(queue=symbol_queue, output_queue=pg_queue)
        yahoo_threads.append(yahoo_scheduler)

    pg_threads = []
    for _ in range(PG_TOTAL_THREADS):
        pg_scheduler = PostgresMasterScheduler(input_queue=pg_queue)
        pg_threads.append(pg_scheduler)

    for company in companies[:10]:
        print("queueing", company)
        symbol_queue.put(company)

    for _ in range(len(yahoo_threads)):
        symbol_queue.put("done")

    for worker in yahoo_threads:
        worker.join()

    for worker in pg_threads:
        worker.join()

    print(f"scrapper time: {time.time() - time_scrapper_start}")


if __name__ == "__main__":
    main()
