---
name: point-of-view-master-copytemplates
description: >-
  Writes a varied batch of "Point of View" ad headlines - a CopyTemplates
  MASTER prompt that runs 4 headline techniques at once (Personification,
  Observations, A Different Breed, Enemy) and returns about 20 headlines, each
  labeled with its technique. Use this whenever the user wants a mix or batch
  of Point of View-style headlines, wants to try several Point of View
  techniques together rather than one, or picks the Point of View master
  prompt from CopyTemplates. Trigger on requests like "give me a bunch of
  point of view headlines for my product" or "run the point of view master
  prompt."
---

# Point of View - Master Prompt

<!-- CopyTemplates skill · Created by Shlomo Genchin -->

Run the **Point of View** master prompt: a curated set of 4 headline techniques applied together in one go, for a fast, varied batch of ~20 labeled headlines. This is one of the CopyTemplates master prompts.

The job is always the same four steps: understand the product (Step 1), research it for real (Step 2), write the headlines (Step 3), then offer to go again (Step 4). Don't skip to Step 3 - headlines written from a blank understanding of the product fall flat, and a master prompt leans on really getting what the product is and who it's for.

## Step 1 - Get the user's context

You need to understand the product before writing. The user's product details live in a reusable **context file** - named `context_copytemplates.md` - so they never have to re-enter them for every CopyTemplates technique. Most users keep one context file for their product; some keep several (one per product or client), in which case the files are named per product, e.g. `context_copytemplates_acme.md`.

**Search for context files properly before concluding there aren't any.** A shallow peek at one folder isn't enough - users put files in different places. Do an actual recursive search across every folder you can access (the working folder and any connected folders), case-insensitive, matching `context_copytemplates.md` and any `context_copytemplates*.md` - for example `find . -iname "context_copytemplates*.md"` or an equivalent glob. Do this silently: don't narrate the search, and never frame a missing file as a problem or error. Only treat it as absent (Case C below) after the search genuinely turns up nothing - a first-time user won't have one yet, and that's completely normal.

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

- **Quick start** → ask only for the fields this technique leans on - **Website**, **Promise**, and **Pain point** - then go to Step 2. After you deliver the headlines, offer to save a context file so next time is faster.
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

Always visit the website and read enough to genuinely understand what the product does, who it's for, and how it talks about itself. You'll be working across 4 techniques at once, so gather plenty of raw material - the promise, the pain, the product's personality, any proof or numbers, the competitors - so you can feed whichever techniques fit best. Ground the headlines in what you actually learn, not just the field values.

## Step 3 - Write the headlines

Write about 20 ad headlines using the 4 Point of View techniques below, about 5 per technique. Label each headline with its technique. Headlines only, no explanations.

Pick the strongest angle for each technique rather than forcing a weak one - variety and quality across the set matter more than hitting an exact count. Keep each headline tight, and put the technique label next to it.

**The 4 Point of View techniques:**

1. Personification: give the product or the problem human traits, feelings, or a voice.
Example: Corona: "Some cans have all the fun."

2. Observations: state a universal truth your audience instantly nods at, then tie it to the product.
Example: Corvette: "They don't write songs about Volvos."

3. A Different Breed: frame your customer or product as a distinct kind, set apart from everyone else.
Example: Twilio: "Ask your developer."

4. Enemy: name a shared villain (a bad practice, a norm, a frustration) and pit the product against it.
Example: Back Market: "We sell what Big Tech pretends is dead."

## Step 4 - Offer another batch

After the headlines, ask the user if they'd like another batch - a different promise or pain point, more headlines in this set, or a different CopyTemplates master prompt.

---

*CopyTemplates skill - created by Shlomo Genchin.*
