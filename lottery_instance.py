# -*- coding: UTF-8 -*-

from BingoBingo import BingoBingo
from datetime import datetime, timedelta

INTERVAL = 15
ROUNDS = 30
TOP_NUMBERS = 10

# INTERVAL = 2
# ROUNDS = 3
# TOP_NUMBERS = 4

if __name__ == "__main__":
    bingo_bingo = BingoBingo()

    bingo_bingo.crawler()
    
    sorted_days_number_occurrence = bingo_bingo.number_statistics(INTERVAL, ROUNDS)

    bingobingo_html = []
    for r in range(1, ROUNDS+1):
        bingobingo_html.append("<h1>" + (datetime.today() - timedelta(days=r)).strftime('%Y-%m-%d') + "</h1>\n" + bingo_bingo.dict_to_html(sorted_days_number_occurrence[r][:TOP_NUMBERS]))

    bingo_bingo.send_email("\n<br/>\n".join(bingobingo_html))
