from sklearn.metrics.pairwise import cosine_similarity


# -------------------------------------------------------------------
# 1. NON-IDEA FILTER
# -------------------------------------------------------------------

def is_non_idea(text: str) -> bool:
    """
    Filters out acknowledgements, fillers, and trivial utterances.
    """
    text = text.strip().lower()

    non_idea_phrases = {
        "yes",
        "yeah",
        "yep",
        "ok",
        "okay",
        "agreed",
        "agree",
        "sounds good",
        "that makes sense",
        "right",
        "correct",
        "exactly",
        "true",
        "fine",
        "sure"
    }

    # Very short utterances are usually non-ideas
    if len(text.split()) <= 2:
        return True

    return text in non_idea_phrases


# -------------------------------------------------------------------
# 2. IDEA DETECTION (NOVELTY)
# -------------------------------------------------------------------

def detect_ideas(events, embeddings, threshold=0.75):
    """
    Detects whether each event introduces a new idea
    using semantic novelty against previous ideas only.
    """
    ideas = []

    for i, event in enumerate(events):

        # Filter acknowledgements first
        if is_non_idea(event.text):
            ideas.append(False)
            continue

        # First meaningful utterance is an idea
        if i == 0:
            ideas.append(True)
            continue

        prev_embeddings = [
            embeddings[j]
            for j in range(i)
            if ideas[j]
        ]

        if not prev_embeddings:
            ideas.append(True)
            continue

        similarities = cosine_similarity(
            [embeddings[i]],
            prev_embeddings
        )[0]

        ideas.append(max(similarities) < threshold)

    return ideas


# -------------------------------------------------------------------
# 3. KEYWORD / TOPIC OVERLAP (SYMBOLIC SIGNAL)
# -------------------------------------------------------------------

def keyword_overlap(a: str, b: str) -> float:
    """
    Computes Jaccard overlap between token sets.
    Acts as a weak but explainable topical signal.
    """
    a_tokens = set(a.lower().split())
    b_tokens = set(b.lower().split())

    if not a_tokens or not b_tokens:
        return 0.0

    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


# -------------------------------------------------------------------
# 4. IDEA REUSE DETECTION
# -------------------------------------------------------------------

def detect_idea_reuse(events, embeddings, idea_flags, threshold=0.70):
    """
    Detects later semantic reuse of an idea by other participants.
    Uses BOTH:
      - sentence embedding similarity
      - keyword overlap (fallback signal)
    """

    print("DEBUG: detect_idea_reuse threshold =", threshold)

    reuse_map = {}

    for i, is_idea in enumerate(idea_flags):
        if not is_idea:
            continue

        source_event = events[i]
        source_embedding = embeddings[i]

        reused_by = []

        for j in range(i + 1, len(events)):
            if events[j].speaker == source_event.speaker:
                continue

            similarity = cosine_similarity(
                [source_embedding],
                [embeddings[j]]
            )[0][0]

            overlap = keyword_overlap(
                source_event.text,
                events[j].text
            )

            # DEBUG — keep while developing, remove later
            print(
                f"DEBUG SIM | '{source_event.text}' --> "
                f"'{events[j].text}' | sim={similarity:.3f}, overlap={overlap:.3f}"
            )

            if similarity >= threshold or overlap >= 0.25:
                reused_by.append({
                    "speaker": events[j].speaker,
                    "text": events[j].text,
                    "similarity": round(float(similarity), 3),
                    "keyword_overlap": round(float(overlap), 3)
                })

        reuse_map[i] = reused_by

    return reuse_map


# -------------------------------------------------------------------
# 5. IGNORED-BUT-REUSED DETECTION (SIGNATURE FEATURE)
# -------------------------------------------------------------------

def detect_ignored_but_reused(
    events,
    embeddings,
    idea_flags,
    reuse_map,
    ack_window=3,
    ack_threshold=0.65
):
    """
    Detects ideas that were:
      1. Introduced
      2. Not acknowledged in the next K turns
      3. Reused later by other participants
    """

    print(
        "DEBUG: detect_ignored_but_reused ack_threshold =",
        ack_threshold
    )

    ignored_reused = {}

    for i, is_idea in enumerate(idea_flags):
        if not is_idea:
            continue

        source_event = events[i]
        source_embedding = embeddings[i]

        # ---- Step 1: check acknowledgment window ----
        acknowledged = False

        for j in range(i + 1, min(i + 1 + ack_window, len(events))):
            if events[j].speaker == source_event.speaker:
                continue

            sim = cosine_similarity(
                [source_embedding],
                [embeddings[j]]
            )[0][0]

            if sim >= ack_threshold:
                acknowledged = True
                break

        # ---- Step 2: if ignored but reused later ----
        if not acknowledged and reuse_map.get(i):
            ignored_reused[i] = {
                "idea_text": source_event.text,
                "introduced_at": round(source_event.start_time, 2),
                "later_reused_by": reuse_map[i]
            }

    return ignored_reused
