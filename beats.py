"""Facade of Jade story beats and drama-manager helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class StoryBeat:
    beat_id: str
    name: str
    description: str
    check_precondition: Callable[[dict], bool]
    transitions: list[str] = field(default_factory=list)
    is_terminal: bool = False


BEATS: dict[str, StoryBeat] = {
    "intro": StoryBeat(
        beat_id="intro",
        name="The Teahouse",
        description=(
            "A swordsman sits across from you, his hand resting on the hilt of his blade. "
            "The teahouse is quiet. The rain has stopped. He watches you with wary eyes."
        ),
        check_precondition=lambda state: False,
        transitions=["revelation", "conflict"],
    ),
    "revelation": StoryBeat(
        beat_id="revelation",
        name="The Secret",
        description=(
            "He speaks of the Jade Mountain Sect, his former home, now destroyed. "
            "His voice trembles. He has never told anyone this before."
        ),
        check_precondition=lambda state: state["trust"] >= 30
        and state["mood"] in ("curious", "friendly", "open"),
        transitions=["conflict", "alliance"],
    ),
    "conflict": StoryBeat(
        beat_id="conflict",
        name="The Demon Sect",
        description=(
            "The conversation turns dark. He suspects you may have ties to the Demon Sect, "
            "the very faction that destroyed his temple. Tension fills the room."
        ),
        check_precondition=lambda state: state["trust"] < 20 or state["mood"] == "hostile",
        transitions=["betrayal", "revelation", "duel"],
    ),
    "duel": StoryBeat(
        beat_id="duel",
        name="The Challenge",
        description=(
            "He stands. The blade half-leaves its scabbard. He challenges you to prove your "
            "honor, or die where you sit."
        ),
        check_precondition=lambda state: state["trust"] < 5
        and state["mood"] == "hostile"
        and state.get("player_challenged", False),
        transitions=["ending_duel", "betrayal"],
    ),
    "alliance": StoryBeat(
        beat_id="alliance",
        name="The Pact",
        description=(
            "He extends his hand. He offers to teach you the Iron Palm technique, "
            "the last legacy of the Jade Mountain Sect."
        ),
        check_precondition=lambda state: state["trust"] >= 60
        and state["mood"] in ("friendly", "open"),
        transitions=["ending_honor", "betrayal"],
    ),
    "betrayal": StoryBeat(
        beat_id="betrayal",
        name="The Betrayal",
        description=(
            "His expression hardens. He reveals he has known your true allegiance all along. "
            "The door slams shut."
        ),
        check_precondition=lambda state: state["trust"] < 10
        and state["mood"] == "hostile"
        and state.get("player_challenged", False)
        and state.get("turns", 0) > 3,
        transitions=["ending_betrayal"],
    ),
    "ending_honor": StoryBeat(
        beat_id="ending_honor",
        name="Honor Bound",
        description=(
            "You kneel before him. He places his hand on your shoulder and names you worthy. "
            "The rain begins again, but this time it feels like a blessing."
        ),
        check_precondition=lambda state: False,
        transitions=[],
        is_terminal=True,
    ),
    "ending_betrayal": StoryBeat(
        beat_id="ending_betrayal",
        name="Broken Trust",
        description=(
            "He turns away and dismisses you forever. You hear his blade slide back into its "
            "scabbard as the door closes behind you."
        ),
        check_precondition=lambda state: False,
        transitions=[],
        is_terminal=True,
    ),
    "ending_duel": StoryBeat(
        beat_id="ending_duel",
        name="Blade's Edge",
        description=(
            "Steel meets steel. In the end, only one of you remains standing. "
            "The teahouse will never forget what happened here tonight."
        ),
        check_precondition=lambda state: False,
        transitions=[],
        is_terminal=True,
    ),
}


KEYWORD_MAP: dict[str, list[str]] = {
    "insult": [
        "stupid",
        "idiot",
        "fool",
        "pathetic",
        "worthless",
        "die",
        "kill",
        "weak",
        "coward",
        "trash",
        "garbage",
        "useless",
        "dumb",
        "loser",
    ],
    "mock": [
        "ha",
        "haha",
        "lol",
        "lmao",
        "ridiculous",
        "absurd",
        "laughable",
        "pathetic",
        "whatever",
        "sure you are",
    ],
    "threaten": [
        "destroy",
        "crush",
        "defeat",
        "challenge",
        "fight",
        "duel",
        "kill you",
        "end you",
        "regret",
        "pay",
        "make you",
        "or else",
    ],
    "praise": [
        "wise",
        "strong",
        "brave",
        "noble",
        "honor",
        "respect",
        "admire",
        "skilled",
        "master",
        "legend",
        "impressive",
        "remarkable",
    ],
    "compliment_skill": [
        "good sword",
        "skilled",
        "technique",
        "fast",
        "powerful",
        "your skill",
        "you fight",
        "well trained",
    ],
    "flirt": [
        "beautiful",
        "handsome",
        "love",
        "marry",
        "kiss",
        "like you",
        "attracted",
        "pretty",
        "charming",
        "enchanting",
    ],
    "apologize": [
        "sorry",
        "apologize",
        "forgive",
        "regret",
        "mistake",
        "didn't mean",
        "my fault",
        "please forgive",
    ],
    "ask_question": [
        "what",
        "how",
        "why",
        "who",
        "where",
        "tell me",
        "explain",
        "what is",
        "how do",
        "why did",
        "who are",
    ],
    "share_secret": [
        "secret",
        "truth",
        "hidden",
        "nobody knows",
        "never told",
        "confession",
        "i must tell",
        "between us",
    ],
    "challenge": ["prove", "show me", "i don't believe", "doubt", "test", "prove it", "how do i know"],
    "greet": [
        "hello",
        "hi",
        "greetings",
        "good day",
        "good evening",
        "good morning",
        "salutations",
        "hey",
    ],
    "goodbye": [
        "goodbye",
        "farewell",
        "see you",
        "bye",
        "until we meet",
        "i must go",
        "leaving",
        "take care",
    ],
}


def classify_discourse_act(player_input: str) -> str:
    """Classify player input into a discourse act via keyword matching.

    Uses word boundaries so substrings inside other words
    (e.g. "ha" inside "have") do not match.
    """
    text = player_input.lower()
    scores = {act: 0 for act in KEYWORD_MAP}
    for act, keywords in KEYWORD_MAP.items():
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", text):
                scores[act] += 1

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "misc"


MOOD_TRANSITIONS: dict[tuple[str, str], str] = {
    ("wary", "insult"): "hostile",
    ("wary", "threaten"): "hostile",
    ("wary", "mock"): "hostile",
    ("wary", "praise"): "curious",
    ("wary", "flirt"): "curious",
    ("wary", "apologize"): "wary",
    ("wary", "ask_question"): "curious",
    ("wary", "share_secret"): "curious",
    ("wary", "compliment_skill"): "curious",
    ("wary", "greet"): "wary",
    ("wary", "challenge"): "hostile",
    ("curious", "insult"): "wary",
    ("curious", "threaten"): "hostile",
    ("curious", "praise"): "friendly",
    ("curious", "flirt"): "friendly",
    ("curious", "apologize"): "friendly",
    ("curious", "ask_question"): "open",
    ("curious", "share_secret"): "open",
    ("curious", "compliment_skill"): "friendly",
    ("curious", "mock"): "wary",
    ("friendly", "insult"): "wary",
    ("friendly", "threaten"): "hostile",
    ("friendly", "mock"): "wary",
    ("friendly", "praise"): "open",
    ("friendly", "flirt"): "open",
    ("friendly", "apologize"): "open",
    ("friendly", "ask_question"): "open",
    ("friendly", "share_secret"): "open",
    ("open", "insult"): "wary",
    ("open", "threaten"): "hostile",
    ("open", "mock"): "wary",
    ("open", "praise"): "open",
    ("open", "apologize"): "open",
    ("hostile", "insult"): "hostile",
    ("hostile", "threaten"): "hostile",
    ("hostile", "mock"): "hostile",
    ("hostile", "praise"): "wary",
    ("hostile", "flirt"): "wary",
    ("hostile", "apologize"): "wary",
    ("hostile", "greet"): "hostile",
    ("hostile", "ask_question"): "hostile",
    ("hostile", "challenge"): "hostile",
}

TRUST_DELTAS: dict[str, int] = {
    "insult": -15,
    "mock": -10,
    "threaten": -20,
    "praise": 14,
    "compliment_skill": 16,
    "flirt": 5,
    "apologize": 8,
    "ask_question": 8,
    "share_secret": 14,
    "challenge": -5,
    "greet": 4,
    "goodbye": 0,
    "misc": 0,
}


def update_state(state: dict, discourse_act: str, player_input: str) -> dict:
    """Update the emotional state and advance beats when preconditions match."""
    mood = state.get("mood", "wary")
    trust = state.get("trust", 0)
    current_beat = state.get("current_beat", "intro")
    player_challenged = state.get("player_challenged", False)
    turns = state.get("turns", 0) + 1

    if discourse_act == "challenge" or any(
        word in player_input.lower() for word in ("duel", "fight me", "challenge you")
    ):
        player_challenged = True

    new_mood = MOOD_TRANSITIONS.get((mood, discourse_act), mood)
    trust_delta = TRUST_DELTAS.get(discourse_act, 0)

    if mood == "hostile" and discourse_act in ("insult", "threaten"):
        trust_delta -= 10
    if discourse_act == "share_secret" and trust >= 20:
        trust_delta += 8

    trust = max(0, min(100, trust + trust_delta))
    current_beat_obj = BEATS.get(current_beat, BEATS["intro"])

    if not current_beat_obj.is_terminal:
        for target_id in current_beat_obj.transitions:
            target_beat = BEATS.get(target_id)
            if target_beat and target_beat.check_precondition({
                "mood": new_mood,
                "trust": trust,
                "current_beat": current_beat,
                "player_challenged": player_challenged,
                "turns": turns,
            }):
                current_beat = target_id
                break

    return {
        "mood": new_mood,
        "trust": trust,
        "current_beat": current_beat,
        "player_challenged": player_challenged,
        "discourse_act": discourse_act,
        "turns": turns,
    }


MOOD_VOICE_GUIDE: dict[str, str] = {
    "wary": "You are guarded and cautious. Keep responses brief. Test the player's intentions.",
    "curious": "You are interested but still careful. Ask questions. Hint at knowledge.",
    "friendly": "You are warm and open. Share wisdom freely. Use metaphors from nature.",
    "open": "You are fully open. Share your deepest memories. Speak poetically.",
    "hostile": "You are sharp and cold. Every word is a blade. Trust no one.",
}

BEAT_NUDGES: dict[str, str] = {
    "intro": "This is the beginning. You do not know this person. Be mysterious.",
    "revelation": (
        "You are sharing your tragic backstory about the Jade Mountain Sect's destruction. "
        "Let vulnerability show through your usual stoicism."
    ),
    "conflict": (
        "You suspect the player has ties to the Demon Sect. Be accusatory. Demand answers. "
        "The tension is life or death."
    ),
    "duel": "This is a fight. Short, sharp responses. Every word is steel.",
    "alliance": (
        "You have decided to trust this person. Offer to teach them the Iron Palm. "
        "This is a moment of hope."
    ),
    "betrayal": "You have discovered the player's deception. Be devastating. Cold fury.",
    "ending_honor": (
        "This is the ending. The player has earned your trust completely. Speak with the weight "
        "of a master passing knowledge to a worthy successor."
    ),
    "ending_betrayal": "This is the ending. The player has failed you. Final, cutting words.",
    "ending_duel": "This is the ending. Combat is happening. Describe the clash. Only one survives.",
}


def get_system_prompt(state: dict) -> str:
    """Build the LLM system prompt from current emotional state and story beat."""
    beat = BEATS.get(state["current_beat"], BEATS["intro"])
    mood = state.get("mood", "wary")
    trust = state.get("trust", 0)
    voice = MOOD_VOICE_GUIDE.get(mood, MOOD_VOICE_GUIDE["wary"])
    nudge = BEAT_NUDGES.get(state["current_beat"], "")

    return f"""You are Master Liang, the last swordsman of the Jade Mountain Sect. You speak with quiet weight, every word chosen carefully, like a sword drawn from its scabbard.

CURRENT STORY BEAT: {beat.name}
Beat context: {beat.description}

YOUR EMOTIONAL STATE:
- Mood: {mood}
- Trust in the player: {trust}/100
- Voice: {voice}

STORY DIRECTION: {nudge}

RULES:
- Respond in 1-3 sentences maximum. Be concise.
- Never break character. You are a Wuxia swordsman, not a chatbot.
- Use Wuxia imagery sparingly: rain, mountains, blades, tea, moonlight.
- If trust is below 20, be cold and suspicious.
- If trust is above 60, share wisdom and personal stories.
- If this is a terminal beat, this is your final response. Make it memorable.
- Do not narrate actions in asterisks. Speak only as Master Liang."""


def format_state_for_display(state: dict) -> str:
    """Format the current state for UI display."""
    beat = BEATS.get(state["current_beat"], BEATS["intro"])
    trust = max(0, min(100, int(state.get("trust", 0))))
    filled = trust // 10
    trust_bar = ("#" * filled) + ("-" * (10 - filled))
    mood = str(state.get("mood", "wary")).capitalize()
    act = str(state.get("discourse_act", "none")).replace("_", " ").title()
    turn = int(state.get("turns", 0))
    return (
        f"**{beat.name}** | Turn: {turn} | Mood: {mood} | "
        f"Trust: [{trust_bar}] {trust}% | Last act: {act}"
    )


def is_game_over(state: dict) -> bool:
    """Return whether the current beat is terminal."""
    beat = BEATS.get(state["current_beat"], BEATS["intro"])
    return beat.is_terminal


def get_trace_entry(session_id: str, player_input: str, state: dict, npc_response: str) -> dict:
    """Generate a compact trace entry for a single turn."""
    return {
        "session_id": session_id,
        "player_input": player_input,
        "discourse_act": state.get("discourse_act", "misc"),
        "mood": state["mood"],
        "trust": state["trust"],
        "current_beat": state["current_beat"],
        "npc_response": npc_response,
        "is_terminal": is_game_over(state),
    }



if __name__ == "__main__":
    from app import _initial_state
    # 1. "have" must NOT match "ha" in mock list
    a = classify_discourse_act("I have come a long way, Master")
    assert a != "mock", f"BUG: friendly input classified as mock: {a}"
    assert a in ("greet", "misc", "praise"), f"Expected greet/misc/praise, got {a}"
    # 2. Praise should classify as praise
    b = classify_discourse_act("You are wise.")
    assert b == "praise", f"Expected praise, got {b}"
    # 3. After 2 friendly turns, trust >= 25
    s = _initial_state()
    for msg in ("Hello, Master.", "You are wise."):
        s = update_state(s, classify_discourse_act(msg), msg)
    assert s["trust"] >= 25, f"Trust after 2 friendly turns: {s['trust']}"
    # 4. betrayal must be unreachable in first 3 turns even with insults
    s = _initial_state()
    for msg in ("You are a fool.", "Kill you, coward.", "I challenge you to a duel."):
        s = update_state(s, classify_discourse_act(msg), msg)
    assert s["current_beat"] != "betrayal", f"betrayal reachable too early: {s['current_beat']}"
    print("all tests passed")
