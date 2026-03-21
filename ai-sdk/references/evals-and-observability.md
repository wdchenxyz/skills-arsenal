---
title: Evals and Observability
description: Course-derived patterns for Evalite, LLM-as-judge scoring, Langfuse, and local inspection.
---

# Evals and Observability

The course treats evals and observability as normal parts of building AI apps,
not as optional extras.

## Evalite File Layout

The course uses a small launcher plus one or more eval files:

```ts
// main.ts
import { runEvalite } from "evalite/runner";

await runEvalite({
    cwd: import.meta.dirname,
    mode: "watch-for-file-changes",
});
```

Then put eval definitions in `evals/*.eval.ts`.

## Basic Evalite Pattern

```ts
import { google } from "@ai-sdk/google";
import { generateText } from "ai";
import { evalite } from "evalite";

evalite("Capitals", {
    data: () => [
        { input: "What is the capital of France?", expected: "Paris" },
    ],
    task: async (input) => {
        const result = await generateText({
            model: google("gemini-2.5-flash-lite"),
            prompt: `Return only the capital for: ${input}`,
        });

        return result.text;
    },
    scorers: [
        {
            name: "includes",
            scorer: ({ output, expected }) =>
                output.includes(expected!) ? 1 : 0,
        },
    ],
});
```

## Deterministic Scorers First

The course often starts with code-based scorers for things like:

- required phrases
- links present
- maximum length
- format constraints

Do this before reaching for an LLM judge.

## LLM-as-Judge: Prefer Symbolic Grades

When using a judge model, the course pattern is to ask for symbolic grades like
`A`, `B`, `C`, or `D`, then map them to numbers in code.

This is usually more stable than asking the model for raw numeric scores.

## Dataset Strategy

The course emphasizes three separate eval sets:

- dev set for fast prompt iteration
- CI set for regression checks
- larger regression set for broader coverage

Coverage matters as much as data cleanliness.

## Langfuse with AI SDK Telemetry

The course wires Langfuse through `experimental_telemetry`.

```ts
const trace = langfuse.trace({ sessionId: body.id });

const result = streamText({
    model,
    messages: modelMessages,
    experimental_telemetry: {
        isEnabled: true,
        functionId: "chat",
        metadata: {
            langfuseTraceId: trace.id,
        },
    },
});
```

When the stream finishes, flush Langfuse:

```ts
const stream = result.toUIMessageStream({
    onFinish: async () => {
        await langfuse.flushAsync();
    },
});
```

## Title Generation as a Separate Instrumented Call

The course also shows parallel helper calls, like generating a chat title with
its own telemetry `functionId`, while the main chat response streams normally.

This is a good pattern for:

- chat titles
- summaries
- background labels
- small metadata-generation tasks

## Local Inspection with DevTools

For local debugging, also see [DevTools](devtools.md).

Use DevTools when you want to inspect raw requests and tool-call traces.

Use Evalite when you want repeatable quality checks.

Use Langfuse when you want production-facing traces and telemetry.
