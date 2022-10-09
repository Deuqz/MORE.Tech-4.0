from django.core.exceptions import BadRequest
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from app.trends import trends


class ValidationViewSet(ViewSet):
    @staticmethod
    def validate(clazz, request=None):
        data = request.query_params if request.method == 'GET' else request.data
        serializer = clazz(data=data, context={'request': request})
        if not serializer.is_valid():
            raise BadRequest(serializer.errors)
        return serializer.validated_data


class ApiViewSet(ValidationViewSet):
    authentication_classes = ()
    permission_classes = ()

    @action(url_path='news', methods=['get'], detail=False)
    def handle_relevant_news(self, request):
        return Response({'news': [{'header': 'header1', 'link': 'news1'},
                                  {'header': 'header2', 'link': 'news2'},
                                  {'header': 'header3', 'link': 'news3'}]})

    @action(url_path='trends', methods=['get'], detail=False)
    def handle_trends(self, request):
        res = trends.analyze(request.role)
        res_dict = dict()
        for i, trend in enumerate(res):
            res_dict[f'Track {i + 1}'] = [f'{news[0]} (link: {news[1]})' for news in trend]
        # return Response({'message': ['news1', 'news2', 'news3']})
        return Response(res_dict)

    @action(url_path='digest', methods=['get'], detail=False)
    def handle_digest(self, request):
        return Response({'message': ['news1', 'news2', 'news3']})
