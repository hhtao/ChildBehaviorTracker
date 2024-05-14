from django.utils.translation import gettext_lazy as _
from common.models import CustomUser
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

class BehaviorIndicator(MPTTModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    level = models.IntegerField(default=1)  # 默认等级
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True)
    # django-mptt fields
    lft = models.IntegerField(default=0)
    rght = models.IntegerField(default=0)
    tree_id = models.IntegerField(default=0)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class BehaviorAction(models.Model):
    indicator = models.ForeignKey(BehaviorIndicator, on_delete=models.CASCADE, related_name='actions')
    description = models.CharField(max_length=255)
    points = models.IntegerField()

    def __str__(self):
        return f"{self.indicator.name} - {self.description}"

class BehaviorRecord(models.Model):
    performer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='performed_behaviors', verbose_name=_('Performer'))
    recorder = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recorded_behaviors', verbose_name=_('Recorder'))
    action = models.ForeignKey(BehaviorAction, on_delete=models.CASCADE, verbose_name=_('Action'))
    performance = models.ForeignKey(BehaviorIndicator, on_delete=models.CASCADE, verbose_name=_('Performance Indicator'), db_column='performance')
    points = models.IntegerField(verbose_name=_('Points'), editable=False)  # 可以设置为不可编辑
    date = models.DateField(verbose_name=_('Date'))

    def __str__(self):
        return f"{self.performer.username} - {self.action.description} on {self.date}"

    def save(self, *args, **kwargs):
        if not self.pk:  # 如果记录是新创建的，则从行为动作中获取点数
            self.points = self.action.points
        super().save(*args, **kwargs)