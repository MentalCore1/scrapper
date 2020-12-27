#!/usr/bin/python3

import sys
import csv
import requests
from http import HTTPStatus
from datetime import datetime


class Company(object):
    def __init__(self, name):
        self.name = name
        self.company_date_data = []

    def __str__(self):
        return self.name


class CompanyDateDatum(object):
    def __init__(self, date_index, trading_open, trading_close):
        self.date_index = date_index
        self.trading_open = trading_open
        self.trading_close = trading_close


class Scrapper(object):
    DATE_INDEX = 0
    TRADING_OPEN = 4
    TRADING_CLOSE = 6

    BASE_COM_V_FINANCE_DOWNLOAD = "https://query1.finance.yahoo.com/v7/finance/download/"

    period1 = 86400
    period2 = 1588982400
    interval = "1d"
    events = "history"

    def __init__(self, file):
        self.file = file
        self.non_passed = []

    def run(self):
        companies = self.get_companies_from_file()
        for company in companies:
            self.process_company(company)

    def get_companies_from_file(self):
        companies = []
        with open(self.file) as csv_file:
            dataframe = csv.reader(csv_file)
            for datum_frame in dataframe:
                companies.append(Company(datum_frame[0]))

        return companies

    def process_company(self, company):
        request = requests.get(
            self.BASE_COM_V_FINANCE_DOWNLOAD
            + f"{company}?period1={self.period1}&period2={self.period2}&interval={self.interval}&events={self.events}"
        )
        if request.status_code == HTTPStatus.OK:
            raw_data = request.text
            data = raw_data.splitlines()
            result = []
            for datum in data:
                result.append(datum.split(','))
            for k in range(1, len(result)):
                date_index = datetime.strptime(result[k][self.DATE_INDEX], '%Y-%m-%d').date()
                trading_open = round(float(result[k][self.TRADING_OPEN]), 2)
                trading_close = round(float(result[k][self.TRADING_CLOSE]), 2)
                company.company_date_data.append(CompanyDateDatum(date_index, trading_open, trading_close))
            with open(str(company) + '.csv', 'w', newline='') as csv_file:
                wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                array_for_output = [['Date', 'Close', 'Volume']]
                for datum in company.company_date_data:
                    array_for_output.append([datum.date_index, datum.trading_open, datum.trading_close])
                wr.writerows(array_for_output)


scrapper = Scrapper(str(sys.argv[1]))

scrapper.run()
