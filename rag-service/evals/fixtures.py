"""
Ground-truth fixtures for retrieval evaluation.

Each entry is written to be unambiguously about ONE attribute, so we can
measure whether /search/attribute actually retrieves the right memories
for the right attribute, and whether it leaks irrelevant chunks in.

journal_id values are in the 9000+ range on purpose, to avoid colliding
with real journal entries in your dev database. created_at is fixed to
the same timestamp across all fixtures so recency scoring doesn't skew
this specific evaluation - we want to isolate semantic retrieval quality.
"""

FIXED_TIMESTAMP = "2026-08-01T09:00:00.000Z"

FIXTURES = [
    # --- vitality ---
    {"journal_id": 9001, "expected_attribute": "vitality",
     "content": "I went for a 5k run this morning and felt strong the whole way. My legs were sore afterward but in a good way."},
    {"journal_id": 9002, "expected_attribute": "vitality",
     "content": "I've been skipping meals lately and it's catching up with me. I felt low energy and dizzy by the afternoon."},
    {"journal_id": 9003, "expected_attribute": "vitality",
     "content": "Slept only four hours last night. I could barely keep my eyes open during the meeting."},

    # --- focus ---
    {"journal_id": 9004, "expected_attribute": "focus",
     "content": "I kept opening YouTube every ten minutes instead of finishing the report. I know I'm procrastinating and it's frustrating."},
    {"journal_id": 9005, "expected_attribute": "focus",
     "content": "For once I sat down and worked for two straight hours without checking my phone. It felt great to be that disciplined."},
    {"journal_id": 9006, "expected_attribute": "focus",
     "content": "I have three unfinished tasks from last week still sitting untouched. I need to stop starting new things before finishing old ones."},

    # --- intellect ---
    {"journal_id": 9007, "expected_attribute": "intellect",
     "content": "Spent the evening reading about distributed systems. Learned how consensus algorithms actually work under the hood."},
    {"journal_id": 9008, "expected_attribute": "intellect",
     "content": "I started practicing a new programming language today. It's humbling to be a beginner again."},
    {"journal_id": 9009, "expected_attribute": "intellect",
     "content": "I finally understood a math concept that's been confusing me for weeks. Felt like a small breakthrough."},

    # --- balance ---
    {"journal_id": 9010, "expected_attribute": "balance",
     "content": "I've been so stressed and overwhelmed that I couldn't relax even during my day off."},
    {"journal_id": 9011, "expected_attribute": "balance",
     "content": "I took a quiet walk in the evening with no phone, just to clear my head. It helped a lot emotionally."},
    {"journal_id": 9012, "expected_attribute": "balance",
     "content": "I've been feeling emotionally drained and on edge, snapping at small things that don't usually bother me."},

    # --- connection ---
    {"journal_id": 9013, "expected_attribute": "connection",
     "content": "Had dinner with my parents tonight, first time in weeks. It was nice just to talk and laugh together."},
    {"journal_id": 9014, "expected_attribute": "connection",
     "content": "I realized I haven't texted any of my close friends in over a month. I miss those relationships."},
    {"journal_id": 9015, "expected_attribute": "connection",
     "content": "Spent the afternoon catching up with an old friend over coffee. It reminded me how much I value that friendship."},

    # --- progress ---
    {"journal_id": 9016, "expected_attribute": "progress",
     "content": "Finally shipped the feature I've been stuck on for two weeks at work. Big milestone for the project."},
    {"journal_id": 9017, "expected_attribute": "progress",
     "content": "I set a goal to finish my side project by the end of the month, and I'm still on track."},
    {"journal_id": 9018, "expected_attribute": "progress",
     "content": "Career-wise I feel stagnant. I haven't made real progress on my goals in a while and it's bothering me."},
]