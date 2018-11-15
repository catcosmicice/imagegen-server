import json
from abc import ABC, abstractmethod
from time import perf_counter

import rethinkdb as r
from flask import g

from utils import fixedlist


class Endpoint(ABC):
    def __init__(self, cache):
        self.avg_generation_times = fixedlist.FixedList(20)
        self.hits = 0
        self.config = json.load(open('config.json'))
        self.RDB_DB = self.config['rdb_db']
        self.rdb = g.rdb
        self.assets = cache

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def get_avg_gen_time(self):
        if len(self.avg_generation_times) == 0:
            return 0

        return round(
            sum(self.avg_generation_times) / len(self.avg_generation_times), 2)

    def run(self, key, **kwargs):
        self.hits += 1
        start = perf_counter()
        res = self.generate(**kwargs)
        t = round((perf_counter() - start) * 1000, 2)  # Time in ms, formatted to 2dp
        print(t)
        self.avg_generation_times.append(t)
        k = r.table('keys').get(key).run(self.rdb)
        try:
            usage = k['usages'][self.name]
        except KeyError:
            usage = 0
        r.db(self.RDB_DB).table('keys').get(key).update({"total_usage": k['total_usage'] + 1,
                                                         "usages": {self.name: usage + 1}}).run(self.rdb)
        return res

    @abstractmethod
    def generate(self, avatars, text, usernames):
        raise NotImplementedError(
            f"generate has not been implemented on endpoint {self.name}"
        )
