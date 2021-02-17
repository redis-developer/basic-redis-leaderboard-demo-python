import json

from django.http import HttpResponse
from django.views import View

from .companies_redis import CompaniesRanks


class CompaniesRankView(View):
    def get(self, request):
        start_index = request.GET.get('start')
        end_index = request.GET.get('end')
        return HttpResponse(CompaniesRanks().get_zrange(start_index, end_index), status=200)


class GetBySortKeyCompaniesView(View):
    def get(self, request, sort_key):
        return HttpResponse(CompaniesRanks().get_ranks_by_sort_key(sort_key), status=200)


class GetBySymbolCompaniesView(View):
    def get(self, request):
        symbols = request.GET.getlist('symbols[]')
        return HttpResponse(CompaniesRanks().get_ranks_by_symbols(symbols), status=200)


class UpdateCompanyView(View):
    def patch(self, request):
        company = json.loads(request.body)
        CompaniesRanks().update_company_market_capitalization(company.get('amount'), company.get('symbol'))
        return HttpResponse(json.dumps({'success': True}), status=200)


class ResetInitDataView(View):
    def get(self, request):
        CompaniesRanks().set_init_data()
        return HttpResponse(json.dumps({'success': True}), status=200)
