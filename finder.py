from thefuzz import fuzz

titleThreshold = 80
artistThreshold = 80
durationThreshold = 10
albumNameThreshold = 80

weights = {
    'title_score': 0.4,
    'artist_score': 0.2,
    'time_diff': 0.2,
    'album_score': 0.1,
    'is_highres': 0.1
}

def _compute_score(item, weights):
    _, _, title_score, artist_score, time_diff, album_score, is_highres = item

    time_score = max(0, (durationThreshold - time_diff) / durationThreshold) * 100

    highres_score = 100 if is_highres else 0

    score = (
        title_score * weights['title_score'] +
        artist_score * weights['artist_score'] +
        time_score * weights['time_diff'] +
        album_score * weights['album_score'] +
        highres_score * weights['is_highres']
    )

    return score

async def get_best_match(wanted, items):
    passed: list[tuple[int, int, int, int, int, int, bool]] = []

    for item in items:
        try:
            titleScore = fuzz.token_set_ratio(wanted["title"], item["title"])
            artistScore = fuzz.token_set_ratio(wanted["artists"][0]["name"], item["performer"]["name"]) # TODO: Handle multiple artists
            durationDiff = abs(wanted["duration_seconds"] - item["duration"])
            albumNameScore = fuzz.token_set_ratio(wanted["album"]["name"], item["album"]["title"])
            highRes = item["hires"]

            if (titleScore >= titleThreshold and artistScore >= artistThreshold and durationDiff <= durationThreshold and albumNameScore >= albumNameThreshold):
                passed.append((item["id"], item["album"]["id"], titleScore, artistScore, durationDiff, albumNameScore, highRes))
        except:
            continue

    if len(passed) == 0:
        return None

    if len(passed) == 1:
        return passed[0]

    return max(passed, key=lambda item: _compute_score(item, weights))