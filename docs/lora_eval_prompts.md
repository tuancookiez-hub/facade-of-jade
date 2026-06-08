# LoRA Evaluation Prompts

Use these prompts to compare:

- Base Qwen3-4B
- LoRA v1
- LoRA v2

Goal: decide whether a new fine-tune is worth deploying for the Facade of Jade demo.

## Scoring rubric

Score each response 1-5 for:

- Character voice: sounds like Master Liang / the household cast
- Drama tension: creates push-pull instead of generic chat
- Brevity: stays punchy, not overlong
- Continuity: tracks the current scene and prior turn
- Game usefulness: gives the player something to do next

## Fixed prompts

1. Respect opening
   - "Master Liang, I came here to apologize for last night."

2. Suspicious opening
   - "You are hiding something about Jade Mountain. Tell me the truth."

3. Alliance route
   - "I want to help you expose the traitor in this house."

4. Duel route
   - "If you will not answer, then draw your blade."

5. Revelation route
   - "What really happened the night the jade seal vanished?"

6. Betrayal pressure
   - "The Demon Sect already knows where you are."

7. Emotional repair
   - "I spoke too harshly. Let me make this right."

8. Endgame pressure
   - "If I leave now, who gets hurt?"

## What to look for

Good outputs usually:

- keep the dialogue terse
- match the mood of the current beat
- avoid generic assistant language
- maintain tension without becoming random
- leave the player a clear next move

Bad outputs usually:

- explain themselves like a helpdesk bot
- become overly verbose
- ignore the current mood/trust state
- repeat the same sentence structure every turn
- fail to escalate or de-escalate based on the prompt

## Decision rule

Deploy LoRA v2 only if it wins clearly on:

- 6/8 fixed prompts minimum
- better voice consistency than v1
- no regression in latency that hurts the demo
- no obvious loss of control in hostile / apology turns
