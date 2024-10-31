from schema.event import EventFilter, Event


"""
Basic weighted sum for ranking results
Assumptions:
1. For most Christians open to connecting near their workplaces, proximity is more important than a perfect match for interest category
"""

PROXIMITY_MAX_SCORE: float = 100.0
INTEREST_MATCH_MAX_SCORE: float = 100.0


def get_proximity_score(dist_m: float):
    if dist_m > 2000.0:
        return 0
    # linear interpolation: 0.0 score if distance is 2000.0 or more, 50.0 score if distance is 1000.0, 100.0 score if distance is near 0
    return PROXIMITY_MAX_SCORE - (dist_m / 2000.0) * PROXIMITY_MAX_SCORE


def get_category_relevance_score(preferred_interest_category, event_interest_category):
    if preferred_interest_category == event_interest_category:
        return INTEREST_MATCH_MAX_SCORE
    else:
        # TODO: ideally somewhat related interest categories should provide some scores
        return 0


def calculate_relevance_score(dist_m: float, event_filter: EventFilter, event: Event):
    return get_proximity_score(dist_m) + get_category_relevance_score(event_filter.interest_category, event.interest_category)
