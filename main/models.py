from django.db import models
from django.db.models import F
from django.db.models.functions import Greatest, Least
from django.dispatch import receiver
from django.utils import timezone

from accounts.models import Family


class Character(models.Model):
    
    # 가족 캐릭터 진행도/포인트/아이템 메타
    family = models.OneToOneField(  # 가족당 캐릭터 1개를 강제
        Family, on_delete=models.CASCADE, related_name='character'
    )
    # 0.0 ~ 1.0 사이 비율(프론트에서 퍼센트로 변환 권장)
    progress = models.FloatField(default=0.0)
    # 누적 포인트(가족 활동 포인트와 분리하여 캐릭터 전용 메타로 유지)
    points = models.PositiveIntegerField(default=0)

    # 완료 아이템 목록(아이템 ID/코드 리스트 또는 객체 리스트)
    # ex) ["sticker_1", "badge_daily_3"] OR [{"code":"sticker_1","ts":"..."}]
    completed_items = models.JSONField(default=list, blank=True)
    total_items = models.PositiveIntegerField(default=0)

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'
        indexes = [
            models.Index(fields=['family']),
            models.Index(fields=['-last_updated']),
            models.Index(fields=['points']),
        ]

    def __str__(self):
        return f'Character#{self.id} fam={self.family_id} prog={self.progress:.2f}'

    # 편의 메서드(서비스 레이어에서 호출)
    def recalc_progress(self, save: bool = True):
        
        # total_items와 completed_items 길이를 이용해 진행도를 0.0~1.0로 환산
        
        if self.total_items > 0:
            done = len(self.completed_items or [])
            # 0.0 ~ 1.0 사이로 클램프
            prog = max(0.0, min(1.0, done / self.total_items))
        else:
            prog = 0.0
        self.progress = prog
        if save:
            self.save(update_fields=['progress', 'last_updated'])

    def add_points(self, amount: int):
        # 포인트 적립(음수면 차감). 트랜잭션 내에서 호출 권장.
        
        self.points = max(0, int(self.points) + int(amount))
        self.save(update_fields=['points', 'last_updated'])

    def complete_item(self, item_code: str, auto_recalc: bool = True):
        
        # 아이템 완료 처리. 중복 추가는 무시
        
        items = list(self.completed_items or [])
        if item_code not in items:
            items.append(item_code)
            self.completed_items = items
            if auto_recalc:
                # total_items 대비 진행도 갱신
                if self.total_items > 0:
                    self.progress = min(1.0, len(items) / self.total_items)
            self.save(update_fields=['completed_items', 'progress', 'last_updated'])
