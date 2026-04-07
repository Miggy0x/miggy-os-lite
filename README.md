# Miggy OS Lite

An AI agent that takes a single essay and generates a 48-hour social distribution plan across brand and founder surfaces.

## What it does

1. Breaks an essay into four narrative angles: thesis, contrarian, emotional hook, debate
2. Writes native outputs for each: tweets, threads, founder posts, video scripts, reply bank
3. Maps outputs to a sequenced distribution schedule

## Run locally

```bash
pip install -r requirements.txt
streamlit run miggy_os_lite.py
```

## Context

Built as a proof-of-work submission for Every's Head of Social role.

Most teams produce social content as output. This agent treats distribution as a system: one strong idea, decomposed and sequenced so it compounds instead of disappearing.

---

## Example

**Input:** An essay arguing that AI shifts leverage toward people who can direct and critique models.

**Tweet:**
> AI shifts leverage to people who can direct it.

**Thread:**
- Most people use AI for speed.
- The best operators use it to redesign workflows.
- The divide is linear thinking versus leveraged thinking.

**Founder post:**
> AI reallocates leverage. People who direct systems outperform people who execute inside them.

---

## System design

```
input → decomposition → format mapping → distribution → signal capture → iteration
```

Distillation, expansion, and pattern recognition run through the agent. Taste, judgment, and narrative direction stay with you.

Most content operations stall on idea clarity, distribution quality, and feedback loops. This system is built to close that gap.
