from django.urls import path
from django.conf.urls import url

from core import views

urlpatterns = [
    path('api/rank/update', views.UpdateCompanyView.as_view()),
    path('api/rank/reset', views.ResetInitDataView.as_view()),
    path('api/list/inRank', views.CompaniesRankView.as_view()),
    path('api/list/getBySymbol', views.GetBySymbolCompaniesView.as_view()),
    url(r'^api/list/(?P<sort_key>all|top10|bottom10)', views.GetBySortKeyCompaniesView.as_view()),
    path('', views.index, name='index'),
]