from Lottery import Lottery

class BingoBingo(Lottery):
    def __init__(self):
        self.firstname = 1

    def number_statistics(self):
        from collections import defaultdict
        import operator

        number_occurrence = defaultdict(int)
        def counter(numbers):
            for number in numbers.split():
                number_occurrence[number] += 1 

        for numbers in self.sql_action("SELECT numbers FROM BingoBingo"):
            counter(numbers[0])

        return sorted(number_occurrence.items(), key=operator.itemgetter(1), reverse=True)

    def crawler(self):
        import sys
        import datetime
        from selenium import webdriver
        from selenium.webdriver.support.select import Select

        if int(datetime.datetime.today().strftime("%H")) < 1:
            return 'Please wait till 1:00 AM for data synced.'
        
        crawled_dates = { str(d[0]): 1 for d in self.sql_action("SELECT DISTINCT(drawing_date) FROM BingoBingo") }

        sys.stdout = open("D:\\BP\\Dropbox\\Lottery\\output.txt", mode = "w", encoding = "utf8")

        try:
            driver = webdriver.Chrome()
            driver.implicitly_wait(10)
            driver.get('https://www.taiwanlottery.com.tw/Lotto/BINGOBINGO/drawing.aspx')

            # import platform
            today_date = datetime.datetime.today().strftime("%Y-%m-%d")
            # today_date = datetime.datetime.today().strftime("%Y/%#m/%#d" if platform.system().lower() == 'windows' else "%Y/%-m/%-d") # 2019/1/4

            select_element = "select[name='DropDownList1']"
            select = Select(driver.find_element_by_css_selector(select_element))
            select_options = [ month_option.get_attribute('value') for month_option in select.options ]
            for month_option in select_options:
                driver.find_element_by_css_selector(select_element + " option[value='" + month_option + "']").click()

                day_link_element = "table[id='Calendar2'] tr td a"
                day_link_hrefs = [ { 'day': day_link.text, 'href': day_link.get_attribute('href') } for day_link in driver.find_elements_by_css_selector(day_link_element) ]

                for day_link in day_link_hrefs:
                    normalized_processing_date = self.change_date_format('%Y/%m/%d', '%Y-%m-%d', month_option + '/' + day_link['day'])
                    if today_date == normalized_processing_date or (normalized_processing_date in crawled_dates and crawled_dates[normalized_processing_date]):
                        continue

                    print('Crawling ' + normalized_processing_date)

                    driver.find_element_by_css_selector(day_link_element + "[href=\"" + day_link['href'] + "\"]").click()
                    self.crawler_to_database(driver.page_source, normalized_processing_date)
                # print(driver.page_source.encode('utf8').decode('cp950', 'ignore'))
            driver.quit()
        except:
            import traceback
            traceback.print_exc()
            driver.quit()

        # ua = UserAgent()
        # header = {'User-Agent': str(ua.random)}
        # r = requests.get('https://www.taiwanlottery.com.tw/Lotto/BINGOBINGO/drawing.aspx', headers=header)
        # if r.status_code == requests.codes.ok:

    def crawler_to_database(self, html_data, processing_date):
        # import requests
        from bs4 import BeautifulSoup
        # from fake_useragent import UserAgent

        def handle_numbers(txt):
            return ' '.join(txt.split())

        def handle_big_small(txt):
            switcher = {
                '大': 'big',
                '小': 'small'
            }
            return switcher.get(txt, 'none')

        def handle_odd_even_equal(txt):
            switcher = {
                '單': 'odd',
                '雙': 'even',
                '小單': 'small_odd',
                '小雙': 'small_even',
                '和': 'equal'
            }
            return switcher.get(txt, 'equal')

        dispatch = {
            1: handle_numbers,
            3: handle_big_small,
            4: handle_odd_even_equal
        }

        soup = BeautifulSoup(html_data, 'html.parser')

        rows = []
        for drawing in soup.select('table.tableFull tr'):
            if 'thB' not in str(drawing) and drawing.find('td').text:
                row = []
                index = 0

                for td in drawing.find_all('td'):
                    txt = td.text.strip()
                    if index in dispatch:
                        txt = dispatch[index](txt)
                    row.append(txt)
                    index += 1

                row.append(processing_date)
                rows.append(row)

        print('Inserting data for ' + processing_date)
        self.sql_action(
            'INSERT IGNORE INTO BingoBingo (drawing_id, numbers, special_number, big_small, odd_even_equal, drawing_date) VALUES (%s, %s, %s, %s, %s, %s)',
            rows)
        print('Finished ' + processing_date)