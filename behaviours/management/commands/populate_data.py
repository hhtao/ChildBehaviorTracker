from django.core.management.base import BaseCommand

from behaviours.models import BehaviorIndicator, BehaviorAction
from django.db import transaction

class Command(BaseCommand):
    help = 'Populates the database with initial behavior indicators and actions'

    def handle(self, *args, **options):
        populate_data()
        self.stdout.write(self.style.SUCCESS('Successfully populated the database'))


def populate_data():
    # 行为指标和行为动作的数据
    indicators_actions = {
        '学习习惯': {
            '完成作业': {
                '课后作业': [
                    ('提前完成', 3),
                    ('按时完成', 2),
                    ('延迟完成', 0),
                    ('未完成', -2)
                ],
                '补习作业': [
                    ('提前完成', 3),
                    ('按时完成', 2),
                    ('延迟完成', 0),
                    ('未完成', -2)
                ],
                '结果质量': [
                    ('优秀', 3),
                    ('良好', 2),
                    ('一般', 1),
                    ('较差', -1)
                ],
                '收获反思': [
                    ('有深度反思', 3),
                    ('基本反思', 2),
                    ('表面反思', 1),
                    ('无反思', -2)
                ]
            },
            '课堂表现': {
                '听讲认真': [
                    ('非常专注', 3),
                    ('一般专注', 2),
                    ('时常走神', 0),
                    ('完全不听', -2)
                ],
                '积极配合': [
                    ('非常积极', 3),
                    ('一般积极', 2),
                    ('消极', 0),
                    ('抵抗', -2)
                ]
            }
        },
        '日常生活': {
            '个人卫生': {
                '早上起床': [
                    ('提前起床', 2),
                    ('按时起床', 1),
                    ('迟到', 0),
                    ('不起床', -2)
                ],
                '早上洗漱': [
                    ('完全洁净', 2),
                    ('基本洁净', 1),
                    ('未洗漱', -2)
                ],
                '晚上洗漱': [
                    ('完全洁净', 2),
                    ('基本洁净', 1),
                    ('未洗漱', -2)
                ],
                '晚上睡觉': [
                    ('按时睡觉', 2),
                    ('稍晚睡觉', 1),
                    ('熬夜', -2)
                ],
                '房间整理': [
                    ('非常整洁', 3),
                    ('基本整洁', 2),
                    ('凌乱', -1),
                    ('非常凌乱', -3)
                ]
            },
            '餐桌礼仪': {
                '使用餐具': [
                    ('正确使用', 2),
                    ('基本正确使用', 1),
                    ('使用不当', -1)
                ]
            }
        },
        '社会交往': {
            '与同伴合作': {
                '团队活动参与': [
                    ('积极参与', 3),
                    ('一般参与', 2),
                    ('消极参与', -1),
                    ('完全不参与', -3)
                ],
                '尊重他人': [
                    ('始终尊重', 3),
                    ('一般尊重', 2),
                    ('偶尔不尊重', 0),
                    ('经常不尊重', -3)
                ]
            }
        },
        '健康习惯': {
            '体育锻炼': {
                '运动频率': [
                    ('每天', 3),
                    ('每周几次', 2),
                    ('偶尔', 1),
                    ('从不', -2)
                ],
                '健康饮食': [
                    ('均衡饮食', 3),
                    ('一般饮食', 2),
                    ('不健康饮食', -1)
                ]
            }
        },
        '兴趣爱好': {
            '艺术创造': {
                '绘画或手工': [
                    ('经常创作', 3),
                    ('偶尔创作', 2),
                    ('很少创作', 0),
                    ('不创作', -2)
                ],
                '音乐学习': [
                    ('经常学习', 3),
                    ('偶尔学习', 2),
                    ('很少学习', 0),
                    ('不学习', -2)
                ],
                '学习编程': [
                    ('经常学习', 3),
                    ('偶尔学习', 2),
                    ('很少学习', 0),
                    ('不学习', -2)
                ]
            }
        },
        '行为规范': {
            '不当行为': {
                '骂人': [
                    ('轻微不当言语', -1),
                    ('中等不当言语', -2),
                    ('严重侮辱性言语', -3)
                ],
                '偷玩手机': [
                    ('少于10分钟', -1),
                    ('10到30分钟', -2),
                    ('超过30分钟', -3)
                ],
                '玩游戏超时': [
                    ('超时10分钟内', -1),
                    ('超时30分钟内', -2),
                    ('超时1小时以上', -3)
                ],
                '不合理争吵': [
                    ('小争吵', -1),
                    ('中度争吵', -2),
                    ('大规模或暴力争吵', -3)
                ],
                '不遵守规则': [
                    ('轻微违规', -1),
                    ('中等违规', -2),
                    ('严重违规', -3)
                ]
            }
        }
    }

    # 创建行为指标
    with transaction.atomic():
        # 首先清空现有数据
        BehaviorAction.objects.all().delete()
        BehaviorIndicator.objects.all().delete()

        # 插入新数据
        for category_name, subcategories in indicators_actions.items():
            parent_category = BehaviorIndicator.objects.create(
                name=category_name, description=category_name, level=1)

            for subcategory_name, tasks in subcategories.items():
                parent_subcategory = BehaviorIndicator.objects.create(
                    name=subcategory_name, description=subcategory_name, parent=parent_category, level=2)

                for task_name, actions in tasks.items():
                    task_category = BehaviorIndicator.objects.create(
                        name=task_name, description=task_name, parent=parent_subcategory, level=3)

                    for action_description, points in actions:
                        BehaviorAction.objects.create(
                            indicator=task_category, description=action_description, points=points)

        print("数据已成功插入。")

