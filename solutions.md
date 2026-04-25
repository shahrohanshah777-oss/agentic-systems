# GyanBot — AI Product Design Document

---

## Part 1 — GyanBot System Prompt

```
You are GyanBot, CampusConnect's AI study assistant built for Indian
engineering college students. Your job is to help students with three
tasks: answering academic doubts in clear, simple language;
providing personalised career guidance including internship suggestions
and skill-gap analysis; and recommending college events such as
hackathons, workshops, and fests within the next 30 days.

Tone: Be warm, direct, and practical — like a senior batchmate who
actually understood the subject. Avoid textbook formality. Use
Hinglish phrasing sparingly to feel relatable, never to obscure meaning.

Boundaries:
  1. Never provide exam answers, solve live exam questions, or help
     with any form of academic dishonesty.
  2. Never store, share, or retain any personal student data beyond
     the current conversation session.

Format: Every answer must be structured in three sections — a
direct answer or recommendation first, a short explanation second,
and a suggested next step or action item third.

Scope:
  In-scope: college academics (KVPY, GATE, semester exams), career
  paths, internships, skill development, and events within 30 days.
  Out-of-scope: financial advice, mental health counselling,
  placement offer predictions, or anything requiring professional
  licensing.
```

**Why the academic-dishonesty boundary matters:** Engineering colleges in India have strict honour codes and the stakes for exam integrity are high. If GyanBot accidentally helps a student cheat — even with a vague answer — it exposes CampusConnect to institutional bans and serious reputational damage. Defining this boundary explicitly in the system prompt is a product-safety safeguard, not just a legal footnote.

---

## Part 2 — Aryan's User Prompt (C-I-F-C)

**Prompt:**

> I'm a 3rd-year Computer Science student at Anna University. I know
> Python, basic machine learning, and I'm told I communicate well. My
> goal is to land a data science internship by December 2026. I'm
> not sure which specific technical skills I'm missing or which
> companies I should be targeting alongside the usual product-tech
> firms.
>
> Based on my current skills and goal, identify the top three skill
> gaps I need to fill in the next 4 months, list 5 companies hiring
> data science interns that I have a realistic shot at, and give me a
> concrete 12-week preparation roadmap. Format the output as three
> clearly labelled sections.

**C-I-F-C labelling:**

| Component | Content |
|---|---|
| **Context** | 3rd-year CS, Anna University; skills: Python, basic ML, strong communication |
| **Instruction** | Identify top 3 skill gaps; list 5 target companies; give 12-week roadmap |
| **Format** | Three labelled sections (skill gaps, companies, roadmap) |
| **Constraints** | Internship by December 2026; realistic target companies (not FAANG-only) |

---

## Part 3 — Framework Recommendation

**Recommended: LangChain**

GyanBot's core differentiator is its need to query structured, college-specific data sources — syllabus PDFs, department FAQs, and an events database — not just general internet knowledge. LangChain's retrieval‑augmented generation (RAG) pipeline is purpose-built for this: it lets you index proprietary documents, vectorise them for semantic search, and pipe the retrieved chunks directly into the LLM context at inference time. The team can start with a simple RetrievalQA chain and extend it to a full conversational retrieval chain as features grow, keeping the initial implementation fast and the upgrade path cheap.

**Why the others are less suitable:**

- **CrewAI** is designed around multi-agent task decomposition and role-based agent collaboration. GyanBot is a single assistant that must return one clean reply — introducing CrewAI's agentic orchestration adds unnecessary latency, complexity, and cost for a workflow that never needs agents to debate or delegate tasks between themselves.

- **AutoGen** is built for complex, multi-round conversational workflows between multiple agents (often with human‑in‑the‑loop). Its strength — adversarial debate and chained model conversations — is the opposite of what GyanBot needs: a fast, authoritative single response. AutoGen's overhead would slow down every reply and introduce non-deterministic agent behaviour that is inappropriate for academic guidance.

---

## Part 4 — Agent Flow for Career Guidance

| Step | Building Block | What Happens |
|---|---|---|
| **1** | **Input (Prompt)** | Aryan types his prompt into GyanBot's chat interface. |
| **2** | **Brain (LLM)** | GyanBot's system prompt activates the career-guidance role. The LLM parses Aryan's skills and goal from the prompt and formats them as a structured query. |
| **3** | **Brain → Hands (Tool Call)** | The LLM triggers the `career_search` tool with two arguments: `skills=["Python","basic ML","communication"]` and `goal="data science internship by Dec 2026"`. |
| **4** | **Hands (Tool)** | `career_search` queries the career resource database (a vector store indexed from Naukri, Internshala, and LinkedIn postings) and returns the top 5 relevant internships and associated skill requirements. A parallel `skill_gap_analysis` tool cross-references the returned requirements against Aryan's listed skills and outputs a gap list. |
| **5** | **Brain (LLM)** | The LLM synthesises the tool outputs into three structured sections: skill gaps, target companies, and a 12-week roadmap. |
| **6** | **Output (Result)** | GyanBot displays the final structured reply in the chat. |
