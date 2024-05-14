from django.shortcuts import render
from django.contrib.auth.models import Group
from django.utils import timezone
from behaviours.models import BehaviorRecord, BehaviorIndicator
from common.models import CustomUser


def build_indicator_hierarchy(indicators):
    # 使用字典来存储层次结构，键是指标的ID，值是指标对象和其子指标的字典
    hierarchy = {}
    
    # 第一遍遍历，构建所有指标的层次结构
    for indicator in indicators:
        # 获取指标的级别
        level = indicator.level
        # 将指标对象添加到层次结构中
        hierarchy[indicator.id] = {
            'indicator': indicator,
            'level': level,  # 添加 level 字段
            'children': {}
        }
        # 如果指标有父指标，将其添加到父指标的 children 字典中
        if indicator.parent_id:
            parent_id = indicator.parent_id
            # 确保父指标存在于层次结构中
            if parent_id not in hierarchy:
                # 如果父指标不存在，则创建一个新的层次结构节点
                hierarchy[parent_id] = {
                    'indicator': indicator.parent,
                    'level': indicator.parent.level,  # 添加 level 字段
                    'children': {}
                }
            # 将指标添加到父指标的 children 字典中
            hierarchy[parent_id]['children'][indicator.id] = hierarchy[indicator.id]
    
    # 第二遍遍历，过滤掉没有三级指标的一级指标
    filtered_hierarchy = {}
    for level0_id, level0_data in hierarchy.items():
        # 检查一级指标是否有至少一个关联的三级指标
        has_three_level_indicators = any(
            any(child['children'])  # 检查二级指标是否有至少一个三级指标
            for child in level0_data['children'].values()
        )
        if has_three_level_indicators:
            filtered_hierarchy[level0_id] = level0_data
    
    return filtered_hierarchy

# 在 index 函数中使用优化后的 build_indicator_hierarchy 函数
def index(request):
    # 获取学生用户组
    children_group = Group.objects.get(name='学生')
    students = CustomUser.objects.filter(groups=children_group)
    student_data = []

    for student in students:
        # 获取该学生的所有行为记录，只显示当天的记录
        today = timezone.now().date()
        records = BehaviorRecord.objects.filter(performer=student, date=today).order_by('-id')  # 按 id 倒序排列
        score = sum(record.points for record in records)  # 计算得分        

        # 获取已完成的指标和行为
        completed_indicators = records.values('performance__name', 'action__description', 'action__points').distinct()

        # 获取未完成的指标
        incomplete_indicators = BehaviorIndicator.objects.exclude(
            id__in=records.values_list('performance',flat=True)
        ).distinct()

        # 构建指标层次结构
        indicator_hierarchy = build_indicator_hierarchy(incomplete_indicators)
     
        # 构建每个学生的数据字典，包含 id 字段和 record_id 字段
        student_data.append({
            'id': student.id,
            'name': student.username,
            'score': score,
            'completed_indicators': completed_indicators,
            'incomplete_indicators': indicator_hierarchy,  # 确保这里传递的是 indicator_hierarchy
            'record_id': records.first().id if records.exists() else None  # 获取最新的记录 id
        })  
    return render(request, 'index.html', {'students': student_data})

from django.shortcuts import render, redirect
from behaviours.models import BehaviorIndicator, BehaviorAction, BehaviorRecord
from common.models import CustomUser as User
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def record(request):
    # 获取学生用户组
    children_group = Group.objects.get(name='学生')
    students = User.objects.filter(groups=children_group)
    student_data = [{'id': student.id, 'name': student.username} for student in students]

    if request.method == 'POST':
        performer_id = request.POST.get('performer_id')
        indicator_id = request.POST.get('indicator_id')
        action_id = request.POST.get('action_id')

        # Check if all required fields are filled
        if performer_id and indicator_id and action_id:
            try:
                performer = User.objects.get(id=performer_id)
                action = BehaviorAction.objects.get(id=action_id)
                recorder = User.objects.first()  # Assuming the first user is the recorder
                
                # 确保performance字段与indicator_id对应
                performance = BehaviorIndicator.objects.get(id=indicator_id)
                
                BehaviorRecord.objects.create(
                    performer=performer,
                    recorder=recorder,
                    action=action,
                    performance=performance,  # 设置performance字段
                    points=action.points,  # 从行为动作中获取点数
                    date=timezone.now().date()
                )
                return JsonResponse({'success': True})
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Performer does not exist.'}, status=400)
            except BehaviorAction.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Action does not exist.'}, status=400)
            except BehaviorIndicator.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Indicator does not exist.'}, status=400)
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

    # 如果不是POST请求，或者请求不完整，则返回学生数据
    return render(request, 'record.html', {'students': student_data})


from mptt.templatetags.mptt_tags import tree_item_iterator
@csrf_exempt
def get_indicators(request):
    if request.method == 'GET':
        indicators = BehaviorIndicator.objects.all()
        # 使用tree_item_iterator来遍历指标树
        indicator_data = []
        for indicator in indicators:
            # 获取指标的所有祖先，包括自己
            ancestors = indicator.get_ancestors(include_self=True)
            # 使用|符号连接祖先的名称
            name = ' | '.join([ancestor.name for ancestor in ancestors])
            indicator_data.append({
                'id': indicator.id,
                'name': name
            })
        return JsonResponse({'indicators': indicator_data})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@csrf_exempt
def get_actions(request, indicator_id):
    if request.method == 'GET':
        actions = BehaviorAction.objects.filter(indicator_id=indicator_id)
        action_data = [{'id': action.id, 'description': action.description, 'points': action.points} for action in actions]
        return JsonResponse({'actions': action_data})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)


from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from behaviours.models import BehaviorRecord, BehaviorAction
from common.models import CustomUser as User

@csrf_exempt
def record_action(request):
    if request.method == 'POST':
        # 使用 print 函数打印请求的 POST 数据
        #print(f"Received POST data: {request.POST}")
        
        performer_id = request.POST.get('student_id')
        action_id = request.POST.get('action_id')

        # 使用 print 函数打印获取到的 performer_id 和 action_id
        #print(f"performer_id: {performer_id}, action_id: {action_id}")

        # Check if all required fields are filled
        if performer_id and action_id:
            try:
                performer = User.objects.get(id=performer_id)
                action = BehaviorAction.objects.get(id=action_id)
                recorder = User.objects.first()  # Assuming the first user is the recorder
                
                # 创建行为记录
                BehaviorRecord.objects.create(
                    performer=performer,
                    recorder=recorder,
                    action=action,
                    performance=action.indicator,  # 使用indicator字段
                    points=action.points,  # 从行为动作中获取点数
                    date=timezone.now().date()
                )
                return JsonResponse({'success': True})
            except User.DoesNotExist:
                #print("Performer does not exist.")
                return JsonResponse({'success': False, 'error': 'Performer does not exist.'}, status=400)
            except BehaviorAction.DoesNotExist:
                #print("Action does not exist.")
                return JsonResponse({'success': False, 'error': 'Action does not exist.'}, status=400)
            except Exception as e:
                #print(f"An error occurred: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            #print("Missing required fields.")
            return JsonResponse({'success': False, 'error': 'Missing required fields.'}, status=400)
    else:
        #print("Invalid request method.")
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)