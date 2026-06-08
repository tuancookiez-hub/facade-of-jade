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
        check_precondition=lambda state: state["trust"] < 15 or state["mood"] == "hostile",
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
        "make this right",
        "too harshly",
        "spoke too harshly",
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


HOT_BUTTON_TOPICS: dict[str, list[str]] = {
    "jade_seal": ["jade seal", "seal", "artifact", "relic"],
    "demon_sect": ["demon sect", "sect", "cult", "allegiance"],
    "jade_mountain": ["jade mountain", "mountain", "temple", "sect destroyed"],
    "betrayal": ["betray", "betrayal", "traitor", "spy", "deceive", "lied"],
    "master_past": ["past", "secret", "truth", "what happened", "confess"],
}

BEAT_GOALS: dict[str, str] = {
    "intro": "Transition-in: test the visitor and establish suspicion.",
    "revelation": "Body goal: reveal one painful truth without surrendering control.",
    "conflict": "Hot-button mix-in: confront possible Demon Sect ties.",
    "duel": "Terminal pressure: force honor through challenge.",
    "alliance": "Transition-out: accept the player as an ally if trust holds.",
    "betrayal": "Terminal pressure: eject the player after deception is exposed.",
    "ending_honor": "Ending: alliance and inheritance of the Jade Mountain legacy.",
    "ending_betrayal": "Ending: broken trust and permanent dismissal.",
    "ending_duel": "Ending: the social game collapses into blades.",
}

MIX_IN_LABELS: dict[str, str] = {
    "jade_seal": "Object hot-button: jade seal",
    "demon_sect": "Danger hot-button: Demon Sect",
    "jade_mountain": "Lore hot-button: Jade Mountain",
    "betrayal": "Trust hot-button: betrayal",
    "master_past": "Therapy-game pressure: painful past",
    "none": "Main beat continues",
}

CANON_TRUTHS: dict[str, str] = {
    "jade_seal_succession": "The jade seal is proof of succession, not just a relic.",
    "jade_mountain_fell": "Jade Mountain fell during a night assault at the Jade Gates.",
    "inside_betrayal": "The sect was not destroyed by outsiders alone; someone inside opened the way.",
    "liang_survivor_guilt": "Master Liang survived the fall and carries guilt over what his blade did that night.",
    "player_mark_hint": "The player may carry a mark or hunger connected to the seal's unfinished legacy.",
}

ROUTE_MILESTONE_LABELS: dict[str, list[str]] = {
    "revelation": [
        "Revelation route 1: admit the jade seal matters to succession.",
        "Revelation route 2: confirm Jade Mountain fell at the Jade Gates.",
        "Revelation route 3: imply there was an inside betrayal.",
        "Revelation route 4: suspect the player is connected to the seal.",
        "Revelation route 5: force a choice between truth and steel.",
    ],
    "alliance": [
        "Alliance route 1: respect earns the first opening.",
        "Alliance route 2: test whether the player wants power or repair.",
        "Alliance route 3: offer a guarded path toward training.",
        "Alliance route 4: name the player a possible successor.",
    ],
    "duel": [
        "Duel route 1: warn the player once.",
        "Duel route 2: hand moves to the blade.",
        "Duel route 3: final chance to stand down.",
        "Duel route 4: steel leaves the scabbard.",
    ],
    "betrayal": [
        "Betrayal route 1: Demon Sect suspicion enters the room.",
        "Betrayal route 2: contradictions harden Liang's expression.",
        "Betrayal route 3: the door is no longer an exit.",
        "Betrayal route 4: Liang exposes the deception.",
    ],
}


def default_memory_flags() -> dict[str, object]:
    return {
        "asked_about_seal": False,
        "seal_questions": 0,
        "pressed_seal_twice": False,
        "mentioned_demon_sect": False,
        "asked_about_jade_mountain": False,
        "accused_liang": False,
        "challenged_liang": False,
        "apologized_after_hostility": False,
        "stayed_silent_count": 0,
        "tested_by_silence": False,
        "earned_first_truth": False,
        "liang_warned_player": False,
        "player_mark_revealed": False,
    }


def default_route_milestones() -> dict[str, int]:
    return {"revelation": 0, "alliance": 0, "duel": 0, "betrayal": 0}


def _is_silence_move(player_input: str) -> bool:
    text = player_input.lower()
    return any(phrase in text for phrase in ("remain silent", "stay silent", "i am silent", "keep silent", "say nothing", "watch him", "watch what"))


def update_story_spine(state: dict, discourse_act: str, player_input: str, hot_button: str, trust_delta: int) -> dict[str, object]:
    text = player_input.lower()
    memory = {**default_memory_flags(), **dict(state.get("memory_flags", {}))}
    milestones = {**default_route_milestones(), **dict(state.get("route_milestones", {}))}
    known_truths = list(state.get("known_truths", []))
    dramatic_notes = list(state.get("dramatic_notes", []))[-6:]

    def reveal(truth_id: str) -> None:
        truth = CANON_TRUTHS[truth_id]
        if truth not in known_truths:
            known_truths.append(truth)

    def note(value: str) -> None:
        if value not in dramatic_notes:
            dramatic_notes.append(value)

    if hot_button == "jade_seal":
        memory["asked_about_seal"] = True
        memory["seal_questions"] = int(memory.get("seal_questions", 0)) + 1
        milestones["revelation"] = max(int(milestones["revelation"]), min(5, int(memory["seal_questions"])))
        reveal("jade_seal_succession")
        if int(memory["seal_questions"]) >= 2:
            memory["pressed_seal_twice"] = True
            milestones["revelation"] = max(int(milestones["revelation"]), 2)
            note("The player keeps trying to circle the seal; Liang should notice the pattern.")

    if hot_button == "jade_mountain" or "jade gates" in text:
        memory["asked_about_jade_mountain"] = True
        milestones["revelation"] = max(int(milestones["revelation"]), 2)
        reveal("jade_mountain_fell")

    if hot_button == "master_past" or "that night" in text:
        milestones["revelation"] = max(int(milestones["revelation"]), 3)
        reveal("liang_survivor_guilt")

    if hot_button == "betrayal" or "hiding" in text or "traitor" in text:
        memory["accused_liang"] = True
        milestones["betrayal"] = max(int(milestones["betrayal"]), 2)
        reveal("inside_betrayal")
        note("The player has pressed on betrayal; Liang should become careful and specific.")

    if hot_button == "demon_sect":
        memory["mentioned_demon_sect"] = True
        milestones["betrayal"] = max(int(milestones["betrayal"]), 1)
        note("The Demon Sect has entered the conversation; suspicion should rise.")

    if discourse_act in {"challenge", "threaten"} or "draw your blade" in text:
        memory["challenged_liang"] = True
        memory["liang_warned_player"] = True
        milestones["duel"] = max(int(milestones["duel"]), 1)
        note("The player challenged Liang; he should warn before escalating to steel.")

    if discourse_act == "apologize" and (memory.get("challenged_liang") or state.get("mood") == "hostile" or int(state.get("tension", 35)) >= 50):
        memory["apologized_after_hostility"] = True
        milestones["alliance"] = max(int(milestones["alliance"]), 1)
        note("The player apologized after drawing tension; Liang should acknowledge the repair attempt.")

    if discourse_act in {"praise", "compliment_skill"} or trust_delta >= 10:
        milestones["alliance"] = max(int(milestones["alliance"]), 1)

    if _is_silence_move(player_input):
        memory["stayed_silent_count"] = int(memory.get("stayed_silent_count", 0)) + 1
        if int(memory["stayed_silent_count"]) >= 2:
            memory["tested_by_silence"] = True
            note("The player has chosen silence repeatedly; Liang should test what the silence hides.")

    if milestones["revelation"] >= 1:
        memory["earned_first_truth"] = True

    return {
        "memory_flags": memory,
        "route_milestones": milestones,
        "known_truths": known_truths[:6],
        "dramatic_notes": dramatic_notes[-8:],
    }


def detect_hot_button(player_input: str) -> str:
    text = player_input.lower()
    for topic, keywords in HOT_BUTTON_TOPICS.items():
        if any(keyword in text for keyword in keywords):
            return topic
    return "none"


def update_social_games(state: dict, discourse_act: str, hot_button: str, trust_delta: int) -> dict[str, int]:
    affinity = int(state.get("affinity", 0))
    self_realization = int(state.get("self_realization", 0))
    tension = int(state.get("tension", 35))

    if discourse_act in {"praise", "compliment_skill", "apologize", "share_secret"}:
        affinity += 10
    if discourse_act in {"ask_question", "share_secret"} or hot_button in {"jade_mountain", "master_past", "jade_seal"}:
        self_realization += 12
    if discourse_act in {"insult", "mock", "threaten", "challenge"}:
        tension += 18
    if hot_button in {"demon_sect", "betrayal"}:
        tension += 15
    if discourse_act == "apologize":
        tension -= 10
    if trust_delta >= 10:
        affinity += 4
    if trust_delta <= -10:
        tension += 8

    return {
        "affinity": max(0, min(100, affinity)),
        "self_realization": max(0, min(100, self_realization)),
        "tension": max(0, min(100, tension)),
    }


def update_state(state: dict, discourse_act: str, player_input: str) -> dict:
    """Update the emotional state and advance beats when preconditions match."""
    mood = state.get("mood", "wary")
    trust = state.get("trust", 0)
    current_beat = state.get("current_beat", "intro")
    player_challenged = state.get("player_challenged", False)
    turns = state.get("turns", 0) + 1
    hot_button = detect_hot_button(player_input)

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
    story_spine = update_story_spine(state, discourse_act, player_input, hot_button, trust_delta)
    social = update_social_games(state, discourse_act, hot_button, trust_delta)
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
                **social,
                "hot_button": hot_button,
            }):
                current_beat = target_id
                break

    if not BEATS.get(current_beat, BEATS["intro"]).is_terminal:
        if social["affinity"] >= 72 and social["self_realization"] >= 45 and trust >= 65:
            current_beat = "ending_honor"
        elif social["tension"] >= 88 and player_challenged:
            current_beat = "ending_duel"
        elif social["tension"] >= 82 and trust <= 12 and turns >= 4:
            current_beat = "ending_betrayal"

    return {
        "mood": new_mood,
        "trust": trust,
        "current_beat": current_beat,
        "player_challenged": player_challenged,
        "discourse_act": discourse_act,
        "turns": turns,
        "hot_button": hot_button,
        "mix_in": MIX_IN_LABELS.get(hot_button, "Main beat continues"),
        "beat_goal": BEAT_GOALS.get(current_beat, "Main beat continues"),
        **social,
        **story_spine,
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


def _format_story_spine_prompt(state: dict) -> str:
    known_truths = list(state.get("known_truths", []))
    milestones = {**default_route_milestones(), **dict(state.get("route_milestones", {}))}
    memory_flags = dict(state.get("memory_flags", {}))
    dramatic_notes = list(state.get("dramatic_notes", []))

    if not known_truths and not any(milestones.values()) and not dramatic_notes:
        return ""

    sections = ["STORY SPINE:"]
    if known_truths:
        truth_lines = "\n".join(f"- {truth}" for truth in known_truths)
        sections.append(f"REVEALED CANON TRUTHS:\n{truth_lines}")

    active_milestones: list[str] = []
    for route, index in milestones.items():
        if index <= 0:
            continue
        labels = ROUTE_MILESTONE_LABELS.get(route, [])
        label = labels[min(index, len(labels)) - 1] if labels else f"{route} route milestone {index}"
        active_milestones.append(f"- {label}")
    if active_milestones:
        sections.append("CURRENT ROUTE MILESTONES:\n" + "\n".join(active_milestones))

    true_flags = []
    for key, value in sorted(memory_flags.items()):
        if value is True or (isinstance(value, int) and value > 0):
            true_flags.append(f"- {key}: {value}")
    if true_flags:
        sections.append("PLAYER MEMORY FLAGS:\n" + "\n".join(true_flags))

    if dramatic_notes:
        sections.append("DRAMATIC NOTES:\n" + "\n".join(f"- {note}" for note in dramatic_notes[-5:]))

    sections.append("Use the story spine to make consequences specific. Do not reveal unrevealed canon truths early.")
    return "\n\n".join(sections)



def get_system_prompt(state: dict) -> str:
    """Build the LLM system prompt from current emotional state and story beat."""
    beat = BEATS.get(state["current_beat"], BEATS["intro"])
    mood = state.get("mood", "wary")
    trust = state.get("trust", 0)
    voice = MOOD_VOICE_GUIDE.get(mood, MOOD_VOICE_GUIDE["wary"])
    nudge = BEAT_NUDGES.get(state["current_beat"], "")
    beat_goal = state.get("beat_goal", BEAT_GOALS.get(state["current_beat"], "Main beat continues"))
    mix_in = state.get("mix_in", "Main beat continues")
    story_spine = _format_story_spine_prompt(state)
    story_spine_section = f"\n\n{story_spine}" if story_spine else ""

    return f"""You are Master Liang, the last swordsman of the Jade Mountain Sect. You speak with quiet weight, every word chosen carefully, like a sword drawn from its scabbard.

CURRENT STORY BEAT: {beat.name}
Beat context: {beat.description}

YOUR EMOTIONAL STATE:
- Mood: {mood}
- Trust in the player: {trust}/100
- Voice: {voice}

STORY DIRECTION: {nudge}
BEAT GOAL: {beat_goal}
MIX-IN / HOT BUTTON: {mix_in}
SOCIAL GAMES:
- Affinity: {state.get("affinity", 0)}/100
- Self-realization: {state.get("self_realization", 0)}/100
- Tension: {state.get("tension", 35)}/100{story_spine_section}

RULES:
- Usually reply in 1-2 sentences. Use 3 sentences only for major revelations or endings.
- End with a concrete hook: a question, a challenge, a demanded choice, or a visible test the player can answer.
- Do not stack moon/blade/silence/mountain/wind imagery in the same response; pick one strong image, then move the drama forward.
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
        f"Trust: [{trust_bar}] {trust}% | Last act: {act} | "
        f"Tension: {int(state.get('tension', 35))}%"
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
        "affinity": state.get("affinity", 0),
        "self_realization": state.get("self_realization", 0),
        "tension": state.get("tension", 35),
        "hot_button": state.get("hot_button", "none"),
        "mix_in": state.get("mix_in", "Main beat continues"),
        "beat_goal": state.get("beat_goal", BEAT_GOALS.get(state["current_beat"], "Main beat continues")),
        "memory_flags": state.get("memory_flags", default_memory_flags()),
        "route_milestones": state.get("route_milestones", default_route_milestones()),
        "known_truths": state.get("known_truths", []),
        "dramatic_notes": state.get("dramatic_notes", []),
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
    # 5. a neutral greeting should not immediately trigger Demon Sect conflict
    s = _initial_state()
    s = update_state(s, classify_discourse_act("Hello, Master Liang."), "Hello, Master Liang.")
    assert s["current_beat"] == "intro", f"neutral greeting triggered wrong beat: {s['current_beat']}"
    # 6. Façade-inspired social games should track hot-button and mix-in metadata
    s = _initial_state()
    s = update_state(s, classify_discourse_act("What happened to the jade seal?"), "What happened to the jade seal?")
    assert s["hot_button"] == "jade_seal"
    assert s["self_realization"] > 0
    assert "beat_goal" in s and "mix_in" in s
    print("all tests passed")
