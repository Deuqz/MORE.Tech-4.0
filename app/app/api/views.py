from django.core.exceptions import BadRequest
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from trends import trends
from app.api.serializers import RoleSerializer
from digest.digest import filter_news
from django.conf import settings

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

    @action(url_path='trends', methods=['get'], detail=False)
    def handle_trends(self, request):
        role = self.validate(RoleSerializer, request)['role']
        ans = []
        for res in trends.analyze(role):
            res_dict = []
            for i, trend in enumerate(res):
                res_dict.append([{'header': news[0], 'link': news[1]} for news in trend])
            ans.append(res_dict)

        return Response({'trends': ans[0], 'insights': ans[1]})

    @action(url_path='digest', methods=['get'], detail=False)
    def handle_digest(self, request):
        role = self.validate(RoleSerializer, request)['role']
        role_info = settings.ROLE_SETTINGS.get(role, None)
        if role_info is None:
            raise BadRequest('Incorrect role: choose one from {}'.format(', '.join(list(settings.ROLE_SEETINGS.keys()))))
        res = []
        for _, rows in filter_news(role, role_info['role'], role_info['role_description']).iterrows():
            res.append({'header': rows['header'], 'link': rows['link']})
        return Response({'digests': res})
