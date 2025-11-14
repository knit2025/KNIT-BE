ITEMS = ['스웨터','양말','슬리퍼','모자','조끼','목도리','인형','리본','장갑','단추']

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
