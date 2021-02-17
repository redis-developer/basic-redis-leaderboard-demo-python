import json
import enum
import logging

from django.conf import settings
from redis import Redis, RedisError, ConnectionError

logger = logging.getLogger(__name__)

class RankSortKeys(enum.Enum):
    ALL = 'all'
    TOP10 = 'top10'
    BOTTOM10 = 'bottom10'


class RedisClient:
    def __init__(self):
        try:
            if settings.REDIS_URL:
                self.redis_client = Redis.from_url(
                    url=settings.REDIS_URL,
                    decode_responses=True
                )
            else:
                self.redis_client = Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    db=settings.REDIS_DB,
                    decode_responses=True
                )
        except RedisError:
            logger.error(f'Redis failed connection to {settings.REDIS_HOST}:{settings.REDIS_PORT}.')
            return

    def set_init_data(self):
        with open(f'companies_data.json', 'r') as init_data:
            companies = json.load(init_data)
            try:
                for company in companies:
                    self.redis_client.zadd(
                        settings.REDIS_LEADERBOARD,
                        {
                            company.get('symbol').lower(): company.get('marketCap')
                        }
                    )

                    self.redis_client.hset(
                        company.get('symbol').lower(),
                        mapping={
                            'company': company.get('company'),
                            'country': company.get('country')
                        }
                    )
            except ConnectionError:
                logger.error(f'Redis connection time out to {settings.REDIS_HOST}:{settings.REDIS_PORT}.')
                return


class CompaniesRanks(RedisClient):
    def update_company_market_capitalization(self, amount, symbol):
        self.redis_client.zincrby(settings.REDIS_LEADERBOARD, amount, symbol)

    def get_ranks_by_sort_key(self, key):
        sort_key = RankSortKeys(key)

        if sort_key is RankSortKeys.ALL:
            return self.get_zrange(0, -1)
        elif sort_key is RankSortKeys.TOP10:
            return self.get_zrange(0, 9)
        elif sort_key is RankSortKeys.BOTTOM10:
            return self.get_zrange(0, 9, False)
    
    def get_ranks_by_symbols(self, symbols):
        companies_capitalization = [
            self.redis_client.zscore(settings.REDIS_LEADERBOARD, symbol)
            for symbol in symbols
        ]
        companies = []

        for index, market_capitalization in enumerate(companies_capitalization):
            companies.append([
                symbols[index],
                market_capitalization
            ])

        return self.get_result(companies)

    def get_zrange(self, start_index, stop_index, desc=True):
        query_args = {
            'name': settings.REDIS_LEADERBOARD,
            'start': start_index,
            'end': stop_index,
            'withscores': True,
            'score_cast_func': int,
        }

        if desc:
            companies = self.redis_client.zrevrange(**query_args)
        else:
            companies = self.redis_client.zrange(**query_args)

        return self.get_result(companies, start_index, desc)

    def get_result(self, companies, start_index=0, desc=True):
        start_rank = int(start_index) + 1 if desc else (len(companies) - start_index)
        increase_factor = 1 if desc else -1
        results = []

        for company in companies:
            symbol = company[0]
            market_cap = company[1]
            company_info = self.redis_client.hgetall(symbol)
            results.append(
                {
                    'company': company_info['company'],
                    'country': company_info['country'],
                    'marketCap': market_cap,
                    'rank': start_rank,
                    'symbol': symbol
                }
            )
            start_rank += increase_factor

        return json.dumps(results)
