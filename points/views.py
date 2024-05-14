from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
from behaviours.models import BehaviorRecord
from common.models import CustomUser
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_exempt
import datetime
import random
import json

def get_points(request):
    # 渲染 points.html 模板
    return render(request, 'points/points.html')

def get_random_color():
    return f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.5)'

@csrf_exempt
def get_points_data(request):
    # 获取学生用户组
    children_group = Group.objects.get(name='学生')
    students = CustomUser.objects.filter(groups=children_group)

    # 获取七天前的日期
    seven_days_ago = datetime.date.today() - datetime.timedelta(days=7)

    # 初始化数据结构
    chart_data = {
        'labels': [(seven_days_ago + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(8)],
        'datasets': []
    }

    # 为每个学生查询得分数据
    for student in students:
        points = BehaviorRecord.objects.filter(
            performer_id=student.id,
            date__gte=seven_days_ago,
            date__lte=datetime.date.today()
        ).values('date').annotate(total_points=Sum('points'))

        # 确保数据完整性，对于没有数据的日期，设置为 0
        date_points = {point['date'].strftime('%Y-%m-%d'): point['total_points'] for point in points}
        student_data = [date_points.get(date, 0) for date in chart_data['labels']]

        # 为每个学生生成一个随机颜色
        color = get_random_color()

        # 添加到数据集中
        chart_data['datasets'].append({
            'label': student.username,  # 或者 student.name 取决于您的模型字段
            'data': student_data,
            'backgroundColor': color,
            'borderColor': color,
            'borderWidth': 1
        })

    return JsonResponse(chart_data)