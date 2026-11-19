"""Session 17: page-number pagination for every list: ?page=2 and ?page_size=10 (at most 20)."""
from rest_framework.pagination import PageNumberPagination


class ClinicPagination(PageNumberPagination):
    page_size = 3                       # small, so the eight doctors of the lab need three pages
    page_size_query_param = "page_size"
    max_page_size = 20
