---
name: metaphor-copytemplates
description: >-
  Writes "Metaphor" ad headlines - one of the CopyTemplates headline
  techniques (think IBM Displaywriter: "Get your secretary a secretary.";
  Liquid Death: "Murder your thirst."). Use this whenever the user wants
  Metaphor-style headlines, or when the creative angle is: Can you use
  the familiar to explain the unfamiliar. Also trigger when the user is
  working through the CopyTemplates headline library and picks Metaphor, or on
  terse requests like "metaphor headlines for my product."
---

# Metaphor Headlines

<!-- CopyTemplates skill · Created by Shlomo Genchin -->

Write ad headlines using the Metaphor technique. This is one of the CopyTemplates headline techniques.

The job is always the same four steps: understand the product (Step 1), research it for real (Step 2), write the headlines (Step 3), then offer to go again (Step 4). Don't skip to Step 3 - headlines written from a blank understanding of the product fall flat, and the Metaphor technique depends on really getting what the product is and who it's for.

## Step 1 - Get the user's context

You need to understand the product before writing. The user's product details live in a reusable **context file** - named `context_copytemplates.md` - so they never have to re-enter them for every CopyTemplates technique. Most users keep one context file for their product; some keep several (one per product or client), in which case the files are named per product, e.g. `context_copytemplates_acme.md`.

**Scope context to this company.** Use only the current company's local profile or an explicitly supplied context file. Do not search other connected folders for a former company's context. If none is provided, ask for the product details needed by this task. Keep a new context file in ignored private storage.

These skills are built for the Cowork/Code desktop app, where a connected folder holds the context file. If no folder is connected at all (you can't read or save files anywhere), don't error - gently ask the user to connect or select a folder first, since that's where the context file lives and gets reused.

Then handle whichever case you're in. Open warmly and present choices as **selectable buttons** (the multiple-choice question UI - not a wall of text, and never a quoted "I couldn't find…" message). A light opener like "Hey :) Quick thing before I write - which would you like?" works well. Show only the option set that matches the situation; don't invent options.

**Case A - exactly one context file found** (and it's not set to always-use). The real question is just "use it or not," so offer:

- **Use my context** *(recommended)* - name what's in it so they recognize it, e.g. "expressvpn.com / use public wifi safely."
- **Different details just this once** - enter fresh info without changing the saved context file.
- **A different product** - they have another product to write for; let them point to or create another context file (see below).
- **Always use this context from now on** - sets `Always use this context: yes` so this question stops appearing on future runs.

**Case B - more than one context file found** (multiple products). Read the website/name from each and let them pick which product they're writing for, as buttons - one per context file - plus **Add another product** to create a new one. Use the chosen context file and continue.

**Case C - no context file found.** Offer:

- **Quick start** - just the website, promise, and pain point; write now.
- **Build my context file** - answer a few more questions and save it so every CopyTemplates skill reuses it automatically.
- **I already have a context file** - for when they keep one in another folder; they point you to it and you read it from there.

Then act on their choice:

- **Quick start** → ask only for the fields this technique leans on - **Website** and **Promise/Pain point** - then go to Step 2. After you deliver the headlines, offer to save a context file so next time is faster.
- **Build my context file / Add another product** → interview for the fields below (friendly batch, let them skip any they don't have yet). Two things to make clear while asking: they can **list several** where it helps - a few pain points, more than one promise, multiple competitors - and the last prompt should **invite anything else** they think is relevant (brand voice, words to avoid, key features, tone), captured in the Notes field. Then ask **where** to keep it (default: the current folder) and save it in the canonical format. Name the first/only file `context_copytemplates.md`; for an additional product, append a short product slug, e.g. `context_copytemplates_acme.md`. Then tell them the exact path, that every CopyTemplates skill will reuse it automatically, and that **they can update it anytime - just ask** (e.g. "add a pain point to my context" or "update my promise"). Never leave the save silent.
- **Use my context / I already have one / picked a product** → read that context file and continue. If at any point the user asks to change something in it ("update my promise," "add another competitor"), edit the file, save, and confirm - they can revise their context whenever they like.
- **Different details just this once** → ask for the fields this technique needs and use those; don't overwrite the saved context file unless they ask.
- **Always use this context** → set `Always use this context: yes` in that file, confirm, then proceed.

### Context file format

When creating or reading a context file, use this exact structure so all CopyTemplates skills stay compatible. Any field can hold **multiple entries** - just list them (a few pain points, several competitors, etc.). The **Notes** field at the end is open: anything else the user thinks is relevant goes there.

```markdown
# CopyTemplates Context

Always use this context: no

- **Website:**
- **Promise:**
- **Pain Point:**
- **Honest flaw:**
- **Objection:**
- **Time to value:**
- **Evidence:**
- **Category:**
- **Main competitors:**
- **Target account/person:**
- **Target persona:**
- **Notes (anything else):**
```

## Step 2 - Research the company

Always visit the website and read enough to genuinely understand what the product does, who it's for, and how it talks about itself. Keep this technique's angle in mind as you research: Can you use the familiar to explain the unfamiliar? Ground the headlines in what you actually learn, not just the field values.

## Step 3 - Write the headlines

**Write 10 Metaphor ad headlines.**

The structure is: "[Product] is [unrelated thing that captures its essence]." No "like" or "as" -- the product simply is the other thing.

You replace the product with a vivid image from a completely different world. The comparison skips straight to the feeling or idea, without explaining anything.

**Examples:**
- IBM Displaywriter: "Get your secretary a secretary."
- Liquid Death: "Murder your thirst."
- Workvivo: "Your internal comms swiss army knife."
- Lacoste: "Life is a beautiful sport."
- Ente: "Safe home for your photos."
- Claude: "A jetpack for your thoughts."
- Clay: "Every artist has a medium. GTM has Clay."
- Red Bull: "Red Bull gives you wings."
- Evernote: "Your second brain."

Output only the 10 finished headlines, numbered. No preamble, no explanations, no labels.

## Step 4 - Offer another set

After outputting the 10 headlines, ask the user if they want to try a different promise/pain point to generate a new set of headlines.

---

*CopyTemplates skill - created by Shlomo Genchin.*
