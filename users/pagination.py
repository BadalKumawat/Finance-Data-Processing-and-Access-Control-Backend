from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math

class CustomPagination(PageNumberPagination):
    page_size = 10  # 10 records at a Time
    page_size_query_param = 'page_size' # limit of list data can be changed from the URL in frontend example : ?page_size=20
    max_page_size = 100

    def get_paginated_response(self, data):
        # for maitaing our custome JSON format
        return Response({
            "success": True,
            "message": "Paginated data fetched successfully",
            "data": {
                "total_records": self.page.paginator.count,
                "total_pages": math.ceil(self.page.paginator.count / self.get_page_size(self.request)),
                "current_page": self.page.number,
                "next_page_url": self.get_next_link(),
                "previous_page_url": self.get_previous_link(),
                "results": data 
            }
        })