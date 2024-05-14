from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import BehaviorIndicator, BehaviorAction, BehaviorRecord

# 如果你需要自定义后台表单或列表显示
class BehaviorIndicatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'level')  # 在列表页显示的字段
    search_fields = ('name',)  # 允许搜索的字段

class BehaviorActionAdmin(admin.ModelAdmin):
    list_display = ('description', 'points')
    search_fields = ('description',)
    list_filter = ('indicator',)  # 添加侧边栏过滤器

class BehaviorRecordAdmin(admin.ModelAdmin):
    list_display = ('performer', 'recorder', 'action', 'performance', 'points', 'date')
    list_filter = ('date', 'action', 'performer', 'recorder')
    search_fields = ('performer__username', 'recorder__username', 'action__description')

# 使用自定义的Admin类注册模型
# 注册BehaviorIndicator为树形结构
admin.site.register(BehaviorIndicator, MPTTModelAdmin)
admin.site.register(BehaviorAction, BehaviorActionAdmin)
admin.site.register(BehaviorRecord, BehaviorRecordAdmin)
