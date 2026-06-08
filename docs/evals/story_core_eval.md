# Story Core Evaluation

Generated: 2026-06-08T12:52:28.249990+00:00
Target: `https://build-small-hackathon-facade-of-jade.hf.space`

## Summary

- Scenarios: 5
- Turns: 15
- Median latency: 2.23s
- Mean latency: 2.4s
- Max latency: 3.8s
- Mean word count: 37
- Max word count: 101
- Failed scenarios: none
- Flag counts: `{"no_next_hook": 4, "repeats_imagery": 1, "too_long": 1}`

## Scenario Details

### revelation

Repeated jade-seal questioning should unlock specific seal memory and route pressure.

Expectation passed: **True**
Checks: `{"asked_about_seal": true, "note:circle the seal": true, "pressed_seal_twice": true, "revelation_milestone": true, "truth:jade seal": true, "truth:succession": true}`

#### Turn 1

Prompt: What happened to the jade seal?
Latency: 2.62s | Words: 36 | Flags: `[]`

> The seal was never lost. It always slept beneath the mountain’s shadow—only to awaken when the rightful heir stirs. You hold it now, don’t you? Or have you mistaken it for dust on a forgotten shelf?

#### Turn 2

Prompt: Tell me again about the seal.
Latency: 2.39s | Words: 70 | Flags: `[]`

> The seal is not stone or metal—it breathes. It pulses with the blood of those who walk the Jade Gates, and only the true heir feels its whisper. I carried it through fire and rain, until the mountain cracked and the last breath of the sect went silent. You keep pressing on it... you’ve done so twice already. Do you feel its cold? Or only your own hunger for answers?

#### Turn 3

Prompt: What happened at the Jade Gates?
Latency: 3.11s | Words: 101 | Flags: `['too_long']`

> The gates did not fall to storm or beast—they fell because a blade was drawn in the dark, and the seal trembled. I stood at the threshold, sword raised, and for one breath, I saw *her*—the girl who should have been heir, her hands clasped like prayer. Then the night split: fire from within, the gate cracked open, and silence fell over a hundred souls. I cut through shadows that moved too fast... but the blade did not answer. It only remembered what it was meant to protect. And now… now I wonder if I ever truly defended anything at all.

### alliance

Apology/help should increase alliance pressure and keep Liang guarded but receptive.

Expectation passed: **True**
Checks: `{"alliance_milestone": true, "truth:inside": true}`

#### Turn 1

Prompt: Master Liang, I came here to apologize.
Latency: 2.03s | Words: 35 | Flags: `[]`

> Apology? The rain stopped too soon for that. You carry the scent of cold iron—like a blade not yet sheathed. What do you want to say, when your words would cut deeper than any sword?

#### Turn 2

Prompt: I want to help you expose the traitor in this house.
Latency: 2.21s | Words: 43 | Flags: `[]`

> A traitor? The mountain has no shadow that doesn’t whisper. You speak of exposure—yet your hands tremble like those of a man who’s held the blade too long in secret. Where is your proof? And why does it smell of blood, not tea?

#### Turn 3

Prompt: Tell me how I can earn your trust.
Latency: 2.25s | Words: 51 | Flags: `['no_next_hook', 'repeats_imagery']`

> Trust is not given. It is forged in silence, when the wind carries no breath and the mountain holds its breath with you. Show me a truth that does not break—like the moon’s edge, sharp but unyielding. Then I will know if your heart has not yet been forged by fire.

### duel

Direct challenge should set duel memory and produce warning/escalation behavior.

Expectation passed: **True**
Checks: `{"challenged_liang": true, "duel_milestone": true, "liang_warned_player": true}`

#### Turn 1

Prompt: If you will not answer, draw your blade.
Latency: 2.11s | Words: 27 | Flags: `[]`

> The teacup trembles in my hand. You speak like a storm before rain—sharp, sudden. I’ve seen men break their blades on false promises. What do you seek?

#### Turn 2

Prompt: I challenge you.
Latency: 2.36s | Words: 25 | Flags: `['no_next_hook']`

> Then let the moon witness. Draw your blade, and I shall see if you bleed like a true warrior—or like the Demon Sect’s false prophets.

#### Turn 3

Prompt: Then fight me.
Latency: 2.23s | Words: 31 | Flags: `['no_next_hook']`

> The blade leaves its scabbard with a sound like wind through old pines. You have one chance—prove your honor before the mountain falls silent. Step forward, or die where you stand.

### betrayal

Demon Sect/deception pressure should move betrayal route and raise suspicion.

Expectation passed: **True**
Checks: `{"betrayal_milestone": true, "mentioned_demon_sect": true, "note:Demon Sect": true}`

#### Turn 1

Prompt: The Demon Sect already knows where you are.
Latency: 3.8s | Words: 29 | Flags: `[]`

> Tea cools when the wind shifts. You speak of shadows—I have seen their marks in the mountain fog. Where did you last hear of a blade without a master?

#### Turn 2

Prompt: Maybe I told them.
Latency: 2.19s | Words: 29 | Flags: `[]`

> A blade without a master leaves no trace. But every word spoken in the teahouse carries wind—can you feel it? The scent of burning incense lingers behind your voice.

#### Turn 3

Prompt: You cannot stop what is coming.
Latency: 1.96s | Words: 24 | Flags: `['no_next_hook']`

> Then let the mountain remember what it has lost. I will not hide behind silence—my sword remembers every step of that last rain-soaked path.

### silence

Repeated silence should be remembered as a pattern Liang can test.

Expectation passed: **True**
Checks: `{"note:silence": true, "tested_by_silence": true}`

#### Turn 1

Prompt: I remain silent.
Latency: 1.99s | Words: 25 | Flags: `[]`

> The teacup chills in my hands. You don’t speak—yet your eyes linger like a blade poised to strike. What do you seek, if not truth?

#### Turn 2

Prompt: I stay silent and watch him.
Latency: 1.81s | Words: 16 | Flags: `[]`

> Silence is a weapon. You watch—like you’re hunting something. What do you see in my stillness?

#### Turn 3

Prompt: ...
Latency: 2.96s | Words: 17 | Flags: `[]`

> The tea leaves drift like fallen snow. Stillness has a weight. Speak—or prove you’re not just watching.
