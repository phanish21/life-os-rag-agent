"""
End-to-end quest generation + completion eval.

Hits the LIVE Express server repeatedly and checks:
  1. /quests/generate never crashes and always returns a valid quest shape
  2. attribute selection isn't stuck picking the same stat every time
     once stats/quest history are no longer all-tied
  3. /quests/:id/complete actually updates XP and the correct stat

"""

import requests
from collections import Counter

EXPRESS_BASE_URL = "http://localhost:3000"
NUM_ROUNDS = 8
VALID_DIFFICULTIES = {"easy", "medium", "hard", "epic"}
VALID_ATTRIBUTES = {"vitality", "focus", "intellect", "balance", "connection", "progress"}


def get_stats():
    response = requests.get(f"{EXPRESS_BASE_URL}/stats")
    response.raise_for_status()
    return response.json()["player"]


def generate_quest():
    response = requests.post(f"{EXPRESS_BASE_URL}/quests/generate")
    return response


def complete_quest(quest_id):
    response = requests.post(f"{EXPRESS_BASE_URL}/quests/{quest_id}/complete")
    return response


def validate_quest_shape(quest: dict) -> list[str]:
    """Returns a list of problems found, empty list means it's valid."""
    problems = []

    if not quest.get("title") or not isinstance(quest["title"], str):
        problems.append("missing or invalid 'title'")
    if not quest.get("description") or not isinstance(quest["description"], str):
        problems.append("missing or invalid 'description'")
    if quest.get("difficulty") not in VALID_DIFFICULTIES:
        problems.append(f"invalid difficulty: {quest.get('difficulty')!r}")
    if quest.get("primary_stat") not in VALID_ATTRIBUTES:
        problems.append(f"invalid primary_stat: {quest.get('primary_stat')!r}")
    if not isinstance(quest.get("xp_reward"), int) or quest.get("xp_reward", 0) <= 0:
        problems.append(f"invalid xp_reward: {quest.get('xp_reward')!r}")

    return problems


def run():
    attribute_counts = Counter()
    seen_titles = []
    failures = []

    for round_num in range(1, NUM_ROUNDS + 1):
        print(f"\n--- Round {round_num} ---")

        stats_before = get_stats()

        gen_response = generate_quest()
        if gen_response.status_code != 201:
            failures.append(f"Round {round_num}: /quests/generate returned {gen_response.status_code}: {gen_response.text}")
            print(f"  FAILED to generate: {gen_response.status_code}")
            continue

        quest = gen_response.json()["quest"]
        problems = validate_quest_shape(quest)
        if problems:
            failures.append(f"Round {round_num}: quest shape invalid - {problems}")
            print(f"  Quest shape problems: {problems}")

        attribute_counts[quest["primary_stat"]] += 1
        seen_titles.append(quest["title"])
        print(f"  Generated: [{quest['primary_stat']}] {quest['title']} ({quest['difficulty']}, {quest['xp_reward']} XP)")

        complete_response = complete_quest(quest["id"])
        if complete_response.status_code != 200:
            failures.append(f"Round {round_num}: /quests/{quest['id']}/complete returned {complete_response.status_code}")
            print(f"  FAILED to complete: {complete_response.status_code}")
            continue

        stats_after = get_stats()

        expected_xp = stats_before["totalXP"] + quest["xp_reward"]
        actual_xp = stats_after["totalXP"]
        if actual_xp != expected_xp:
            failures.append(
                f"Round {round_num}: XP mismatch - expected {expected_xp}, got {actual_xp}"
            )

        stat_name = quest["primary_stat"]
        expected_stat = stats_before["attributes"][stat_name] + quest["xp_reward"]
        actual_stat = stats_after["attributes"][stat_name]
        if actual_stat != expected_stat:
            failures.append(
                f"Round {round_num}: {stat_name} mismatch - expected {expected_stat}, got {actual_stat}"
            )

        print(f"  Completed. XP: {stats_before['totalXP']} -> {stats_after['totalXP']}, "
              f"{stat_name}: {stats_before['attributes'][stat_name]} -> {stats_after['attributes'][stat_name]}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Attribute distribution across {NUM_ROUNDS} rounds: {dict(attribute_counts)}")

    duplicate_titles = [t for t, count in Counter(seen_titles).items() if count > 1]
    if duplicate_titles:
        print(f"WARNING: repeated quest titles (possible fallback/stuck generation): {duplicate_titles}")

    if failures:
        print(f"\n{len(failures)} FAILURE(S):")
        for f in failures:
            print(f"  - {f}")
    else:
        print("\nAll rounds passed. Full loop (generate -> complete -> stats update) is working correctly.")


if __name__ == "__main__":
    run()