# Backlog — conversation-knowledge

Scope, sprint by sprint. Check off items as they're done.
---

## Sprint 0 — Setup

- [ ] Repo structure (`services/`, `simulation/`, `db/`, `models/`, `tests/`)
- [ ] `pyproject.toml` with uv, deps (fastapi, psycopg2/asyncpg, qdrant-client, ollama, sentence-transformers)
- [ ] `docker-compose.yml` — PostgreSQL + Qdrant
- [ ] `db/init.sql` — schema (threads, raw_messages, classified_messages, knowledge_objects)
- [ ] One hardcoded simulation thread: `simulation/scenarios/happy_path.json`

**Definition of done:** `docker-compose up` brings up Postgres + Qdrant, `init.sql` runs without errors, tables exist.

---

## Sprint 1 — Walking skeleton

**Goal:** Checking that the main idea actually works. If we have a full conversation, it should be turned into a useful piece of knowledge that can be saved and reused later.

- [ ] `POST /ingest/teams` stores raw messages from `happy_path.json`
- [ ] Thread reconstruction (recursive CTE, ordered by `parent_message_id`)
- [ ] Knowledge extraction prompt (Ollama) — problem / symptoms / solutions_tried / confirmed_solution
- [ ] Store result in `knowledge_objects`
- [ ] Generate embedding (sentence-transformers)
- [ ] Index embedding in Qdrant
- [ ] Manual Qdrant query to confirm retrieval returns the right object

**Definition of done:** running `uv run simulation/run_simulation.py happy_path`, query Qdrant manually, getting back a sensible, correctly-structured knowledge object.

**Sprint review question:** does the LLM extraction actually produce usable structured data, or does the prompt need rework? ...

---

## Sprint 2 — Routing known threads

**Goal:** handling a stream of messages across multiple threads, not just one isolated thread. Still using `replyToId` — no similarity search yet.

- [ ] 5 simulated threads, mixed states (some open, some already extracted)
- [ ] `route_known_thread()` — direct mapping using `replyToId` → `thread_id`
- [ ] Decision + implementation: re-extract / append / ignore when a message arrives on an already-closed thread
- [ ] Scenario: noisy thread (no clear resolution)
- [ ] Scenario: ambiguous confirmation ("ok")
- [ ] Scenario: nested replies (reply to a reply, not the root)

**Definition of done:** simulator runs each scenario file independently, each producing the expected DB state (right thread, right role tags, right extraction trigger or non-trigger).

---

## Sprint 3a — Anonymizer + Classifier

**Goal:** adding the realistic preprocessing layer in front of the already-validated pipeline. Still simulator-driven, no Power Automate yet.

- [ ] `anonymizer.py` — strip/replace author names before content reaches any LLM
- [ ] `classifier.py::is_reply()` — rule-based, checks `parent_message_id`
- [ ] `classifier.py::classify_role()` — LLM call, returns question / answer / confirmation / noise
- [ ] Store role + confidence in `classified_messages`
- [ ] Auto-trigger `extract_knowledge()` when `role == "confirmation"`
- [ ] Update simulator to send realistic names (e.g. "John Smith") to actually exercise the anonymizer

**Definition of done:** run the simulator, confirm stored author is anonymized, confirm a "confirmation"-tagged message auto-triggers extraction without manually calling `/extract-knowledge/{thread_id}`.

---

## Sprint 3b — Power Automate connection

**Goal:** proving real Teams messages reach the already-validated pipeline unchanged.

- [ ] Power Automate flow: trigger on new Teams message
- [ ] Map real Teams payload fields → `TeamsMessage` schema (check actual nesting of `replyToId`, not just docs)
- [ ] POST mapped payload to `/ingest/teams`
- [ ] End-to-end test in a real Teams test channel

**Definition of done:** posting a message in a real Teams channel, seeing it land correctly in `raw_messages`, anonymized and classified, with zero new logic written this sprint.

---

## Sprint 4 — Thread assignment engine, part 1: candidates

**Goal:** starting to handle messages without `replyToId` — i.e. new problems, not replies.

- [ ] Embedding generation for incoming unassigned messages
- [ ] Similarity search in Qdrant → top-K candidate threads
- [ ] Candidate thread metadata filtering (e.g. same channel/technology)

**Definition of done:** given a simulated "new problem" message, the system returns a ranked list of plausible candidate threads.

---

## Sprint 5 — Thread assignment engine, part 2: decision

**Goal:** complete the assignment engine — decide assign vs new thread.

- [ ] Confidence evaluation scoring on candidates
- [ ] LLM Judge — context analysis to confirm/reject the top candidate
- [ ] Best Thread Choice logic
- [ ] Fallback: create new thread when no candidate passes confidence threshold

**Definition of done:** simulated messages correctly get assigned to existing threads when relevant, and correctly spawn new threads when not — across at least 3 ambiguous test cases.

---

## Icebox (not scheduled yet)

- [ ] Deduplication of knowledge objects describing the same problem
- [ ] Caching layer (Redis) for repeated RAG queries
- [ ] Multilingual handling (French + English in the same channel)
- [ ] Full RAG assistant + auto-send answer to Teams channel

---

## Review log

(One or two sentences per sprint, right after running the Definition of Done test.)

- **Sprint 0:** _pending_
- **Sprint 1:** _pending_
- **Sprint 2:** _pending_
- **Sprint 3a:** _pending_
- **Sprint 3b:** _pending_
- **Sprint 4:** _pending_
- **Sprint 5:** _pending_

## Retro log
(what would I do differently next time.)
- **Sprint 0:** _pending_
- **Sprint 1:** _pending_
- **Sprint 2:** _pending_
- **Sprint 3a:** _pending_
- **Sprint 3b:** _pending_
- **Sprint 4:** _pending_
- **Sprint 5:** _pending_