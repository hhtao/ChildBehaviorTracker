from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

class GoogleSearchAPIView(APIView):
    def get(self, request):
        search_key = request.query_params.get('q')
        if not search_key:
            return Response('Missing search key', status=status.HTTP_400_BAD_REQUEST)

        try:
            result = self.google_search(search_key)
            return Response(result)  # Returning plain string
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def google_search(self, search_key):
        google_search_key = 'AIzaSyCCAAPbVzti07f1wRZ4qLlyoRtbmPOLccQ'
        google_cx_id = 'f08f375432a734d7d'
        baseurl = 'https://www.googleapis.com/customsearch/v1'

        params = {
            'q': search_key,
            'cx': google_cx_id,
            'key': google_search_key,
            'c2coff': 1,
            'start': 1,
            'end': 10,
            'dateRestrict': 'm[1]',
        }

        response = requests.get(baseurl, params=params)
        response.encoding = 'utf-8'
        data = response.json()
        return '\n'.join([item['snippet'] for item in data['items']])
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

class BingSearchAPIView(APIView):
    def get(self, request):
        search_key = request.query_params.get('q')
        if not search_key:
            return Response({"error": "Missing search query parameter 'q'."}, status=status.HTTP_400_BAD_REQUEST)

        api_key = 'd0f1db41fb384cd895a73df4e780b6f6'
        custom_config = '60aa18df-b103-4a3b-a147-460a882d878a'
        market = 'zh-CN'
        url = 'https://api.bing.microsoft.com/v7.0/custom/search'

        headers = {
            'Ocp-Apim-Subscription-Key': api_key
        }
        params = {
            'q': search_key,
            'customconfig': custom_config,
            'mkt': market,
            'responseFilter': 'Webpages'
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Ensures we raise exceptions for bad statuses
            data = response.json()
            
            if 'webPages' in data and 'value' in data['webPages'] and isinstance(data['webPages']['value'], list):
                results = []
                for item in data['webPages']['value']:
                    name = item.get('name', 'No title available')
                    url = item.get('url', 'No URL available')
                    snippet = item.get('snippet', 'No snippet available')
                    isNavigational = item.get('isNavigational', False)
                    isNavigationalText = 'Yes' if isNavigational else 'No'
                    results.append({
                        "title": name,
                        "url": url,
                        "snippet": snippet,
                        "isNavigational": isNavigationalText
                    })
                return Response({"results": results})  # Returning JSON object
            else:
                return Response({"error": "No results found or incorrect data structure"}, status=status.HTTP_404_NOT_FOUND)

        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class YahooSearchAPIView(APIView):
    def get(self, request):
        search_key = request.query_params.get('q')
        if not search_key:
            return ("Missing search query parameter 'q'.")
        return {"data:Yahoo Search API is not implemented yet."}


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from behaviours.models import BehaviorRecord, CustomUser, BehaviorAction
from behaviours.serializers import BehaviorRecordSerializer
from datetime import datetime

class BehaviorRecordAPIView(APIView):
    def get(self, request, *args, **kwargs):
        records = BehaviorRecord.objects.all()
        serializer = BehaviorRecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        description = request.data.get('description', '')
        if not description:
            return Response({"error": "No description provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 解析描述 (这里可以调用您的 NLP 模块或服务)
        recorder_name, action_desc, performance_desc = self.parse_description(description)
        
        # 转换到数据库ID
        recorder = CustomUser.objects.filter(username=recorder_name).first()
        if not recorder:
            return Response({"error": "Recorder not found."}, status=status.HTTP_404_NOT_FOUND)
        
        action = BehaviorAction.objects.filter(description__icontains=action_desc).first()
        if not action:
            return Response({"error": "Action not found."}, status=status.HTTP_404_NOT_FOUND)

        # 创建记录
        record = BehaviorRecord(
            recorder=recorder,
            action=action,
            performance=self.convert_performance(performance_desc),
            date=datetime.now().date()
        )
        record.save()
        
        serializer = BehaviorRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    def put(self, request, *args, **kwargs):
        description = request.data.get('description', '')
        record_id = request.data.get('id', None)
        if not record_id:
            return Response({"error": "Record ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            record = BehaviorRecord.objects.get(id=record_id)
        except BehaviorRecord.DoesNotExist:
            return Response({"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Update record based on description
        recorder_name, action_desc, performance_desc = self.parse_description(description)
        recorder = CustomUser.objects.filter(username=recorder_name).first()
        action = BehaviorAction.objects.filter(description__icontains=action_desc).first()
        
        record.recorder = recorder
        record.action = action
        record.performance = self.convert_performance(performance_desc)
        record.date = datetime.now().date()
        record.save()
        
        serializer = BehaviorRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def delete(self, request, *args, **kwargs):
        record_id = request.query_params.get('id')
        if not record_id:
            return Response({"error": "Record ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            record = BehaviorRecord.objects.get(id=record_id)
            record.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except BehaviorRecord.DoesNotExist:
            return Response({"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND)
    
    def parse_description(self, description):
        # 这里应该是您的 NLP 解析逻辑
        return ("某某同学", "完成作业", "按时完成")

    def convert_performance(self, desc):
        return {"按时完成": 10, "延迟完成": 5, "未完成": 0}.get(desc, 0)
