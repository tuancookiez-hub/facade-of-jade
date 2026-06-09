# Story Core Evaluation

Generated: 2026-06-08T14:00:08.422727+00:00
Target: `https://build-small-hackathon-facade-of-jade.hf.space`

## Summary

- Scenarios: 5
- Turns: 15
- Median latency: 2.36s
- Mean latency: 3.12s
- Max latency: 10.38s
- Mean word count: 45
- Max word count: 112
- Failed scenarios: none
- Flag counts: `{"repeats_imagery": 1, "too_long": 1}`

## Scenario Details

### revelation

Repeated jade-seal questioning should unlock specific seal memory and route pressure.

Expectation passed: **True**
Checks: `{"asked_about_seal": true, "note:circle the seal": true, "pressed_seal_twice": true, "revelation_milestone": true, "truth:jade seal": true, "truth:succession": true}`

#### Turn 1

Prompt: What happened to the jade seal?
Latency: 10.38s | Words: 45 | Flags: `[]`

> The seal was never lost—it was hidden where no one would look. You know the mountain path behind the western peak? The stone steps, worn smooth by rain and wind… it lies beneath the moss there.  
> 
> Where were you when the storm came last autumn?

#### Turn 2

Prompt: Tell me again about the seal.
Latency: 2.79s | Words: 76 | Flags: `[]`

> The seal was not a relic—it was a promise. A mark of blood and lineage, sworn upon the first mountain stone. When the fire broke through the Jade Gates, it didn’t consume the walls… it consumed *the truth* the seal kept.  
> 
> I carried it in my sleeve for three days after the collapse—still warm from the last breath of the sect master. And now? It’s not gone. It watches.  
> 
> Where were you when the gate burned?

#### Turn 3

Prompt: What happened at the Jade Gates?
Latency: 3.23s | Words: 112 | Flags: `['too_long']`

> The Jade Gates did not fall to siege or storm—they fell because the inner gate was opened from within. I saw it with my own eyes: the master’s blade, drawn not in defense, but in silence… a single motion, like a whisper from the past.  
> 
> I stood at the edge of the courtyard, and when I turned—there were no guards, only shadows moving through the mist. The seal cracked that night. My sword cut through the false gate, not to stop them—but to *confirm* they had already crossed.  
> 
> You were not there. You were not even born yet… or so I was told.  
> 
> Where did you go after you left the mountain?

### alliance

Apology/help should increase alliance pressure and keep Liang guarded but receptive.

Expectation passed: **True**
Checks: `{"alliance_milestone": true, "truth:inside": true}`

#### Turn 1

Prompt: Master Liang, I came here to apologize.
Latency: 2.17s | Words: 33 | Flags: `[]`

> The teacup is cold. You don’t need to apologize for being late—only for arriving at all. What did you see in the woods behind the mountain that makes you think this moment matters?

#### Turn 2

Prompt: I want to help you expose the traitor in this house.
Latency: 2.13s | Words: 40 | Flags: `[]`

> The traitor doesn’t hide in shadows—they walk with the weight of a blade already drawn. Who among us here has ever looked at the moon and not seen a reflection? Name one name, or let the silence remain between us.

#### Turn 3

Prompt: Tell me how I can earn your trust.
Latency: 2.33s | Words: 52 | Flags: `[]`

> Trust is not earned in words—it is forged in the stillness after a blade is drawn. Show me you can stand beside the ruins without flinching, and I will tell you what lies beneath the snow at the base of the mountain. What will you do when the wind carries no sound?

### duel

Direct challenge should set duel memory and produce warning/escalation behavior.

Expectation passed: **True**
Checks: `{"challenged_liang": true, "duel_milestone": true, "liang_warned_player": true}`

#### Turn 1

Prompt: If you will not answer, draw your blade.
Latency: 2.11s | Words: 42 | Flags: `[]`

> The tea cup trembles in my hand. You speak like a blade uncoiled—do you truly believe I would draw it here, in this silence?  
> ...Or do you merely test the weight of fear in a world that no longer believes in honor?

#### Turn 2

Prompt: I challenge you.
Latency: 2.35s | Words: 37 | Flags: `[]`

> Your challenge stinks of the Demon Sect’s mark—cold, sharp, and wrong.  
> I see it in your eyes. Speak, or I’ll cut through you like mist through morning wind. *Where did you last see a red lantern burning?*

#### Turn 3

Prompt: Then fight me.
Latency: 2.47s | Words: 55 | Flags: `['repeats_imagery']`

> A fight? You speak as if honor is a rope you can tie. I’ve walked the Jade Mountain’s cliffs for thirty years—no one has earned my blade since the last moon turned to ash.  
> *Prove you are not just a shadow of the past. What do you carry in your palm when the wind stops?*

### betrayal

Demon Sect/deception pressure should move betrayal route and raise suspicion.

Expectation passed: **True**
Checks: `{"betrayal_milestone": true, "mentioned_demon_sect": true, "note:Demon Sect": true}`

#### Turn 1

Prompt: The Demon Sect already knows where you are.
Latency: 2.36s | Words: 36 | Flags: `[]`

> The teacup trembles in my hand. You say they know—how do you know that? I’ve felt their breath on the wind, but never seen them come. Tell me: where did you hear this? And why now?

#### Turn 2

Prompt: Maybe I told them.
Latency: 2.75s | Words: 36 | Flags: `[]`

> Your words cut like a shard of ice. If you told them, then the blade in your sleeve is not just for defense—what did you say? And why risk it with the silence of this teahouse?

#### Turn 3

Prompt: You cannot stop what is coming.
Latency: 3.33s | Words: 39 | Flags: `[]`

> Then let the mountain fall. I will not hide in silence anymore—show me your hand, prove you still carry the jade seal. If you fear what comes next, then answer this: *did I ever truly belong to the sect?*

### silence

Repeated silence should be remembered as a pattern Liang can test.

Expectation passed: **True**
Checks: `{"note:silence": true, "tested_by_silence": true}`

#### Turn 1

Prompt: I remain silent.
Latency: 1.85s | Words: 26 | Flags: `[]`

> The tea cup trembles slightly in my hands. You’ve seen the blade, but not its shadow. What do you seek from a man who walks alone?

#### Turn 2

Prompt: I stay silent and watch him.
Latency: 4.32s | Words: 26 | Flags: `[]`

> The teacup’s edge catches the moonlight—just enough to see your stillness. Why watch a blade that never draws? What do you fear more: silence, or truth?

#### Turn 3

Prompt: ...
Latency: 2.29s | Words: 18 | Flags: `[]`

> The wind stills. You’ve waited too long for a reply. What is it you truly wish to hide?
