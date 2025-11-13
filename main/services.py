ITEMS = ['스웨터','목도리','장갑','모자','귀도리','양말','인형','조끼','슬리퍼','러그']

def compute_character_progress(total_points: int) -> dict:
    p = max(0, int(total_points or 0))
    completed = min(p // 10, len(ITEMS))
    in_item_points = p % 10
    in_item_progress = in_item_points / 10.0
    current_item = ITEMS[completed] if completed < len(ITEMS) else None

    return {
        'totalPoints': p,
        'completedItems': completed,
        'currentItem': current_item,
        'inItemPoints': in_item_points,
        'inItemProgress': in_item_progress,
        'items': ITEMS,
    }
