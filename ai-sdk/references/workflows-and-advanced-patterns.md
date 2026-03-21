---
title: Workflows and Advanced Patterns
description: Course-derived patterns for sequential workflows, loops, routing, comparison, and research flows.
---

# Workflows and Advanced Patterns

The course goes well beyond single-call chats. These patterns are useful when a
task naturally breaks into multiple model calls or multiple UI phases.

## Sequential Generator -> Evaluator -> Finalizer

A simple workflow can use separate calls for drafting, critique, and final
output. Keep each step narrowly scoped.

Typical pattern:

1. `generateText` or `streamText` to create a draft
2. `generateText` or `streamObject` to critique it
3. `streamText` for the final assistant reply

This is often clearer and easier to debug than forcing one giant prompt.

## Manual Iterative Loops Need a Hard Cap

If you build your own loop, always keep a hard max iteration count, even if the
model can stop early.

```ts
let step = 0;
let mostRecentDraft = "";
let mostRecentFeedback = "";

while (step < 2) {
    const draftResult = streamText({ model, prompt: buildDraftPrompt() });
    const evaluation = streamObject({
        model,
        schema: z.object({
            feedback: z.string().optional(),
            isGoodEnough: z.boolean(),
        }),
        prompt: buildEvaluationPrompt(),
    });

    const finalEvaluation = await evaluation.object;

    if (finalEvaluation.isGoodEnough) {
        break;
    }

    mostRecentFeedback = finalEvaluation.feedback!;
    step++;
}
```

## Stream Structured State for Loop Control

The course uses `streamObject` when the loop controller should expose partial
feedback to the UI while still producing a final typed decision.

Useful for:

- draft critique
- approval readiness
- search planning
- any `isGoodEnough` style loop break condition

## Model Router Pattern

The course uses a cheap classifier model first, then routes to a stronger model
only when needed.

```ts
const routeResult = await generateText({
    model: BASIC_MODEL,
    system: `
    Return a single number.
    Return 0 for the basic model.
    Return 1 for the advanced model.
  `,
    messages: modelMessages,
});

const modelSelected = routeResult.text.trim() === "1" ? "advanced" : "basic";
```

Two key rules from the course:

- keep router output tiny, usually `0` or `1`
- always `trim()` the result before branching

The selected model can be attached as message metadata.

## Compare Multiple Outputs, Then Rewrite History

The course also shows how to stream multiple candidate outputs, let the user
choose one, then rewrite chat history so later turns continue from the chosen
answer.

```tsx
const newMessages = messages.slice(0, index);

newMessages.push({
    ...message,
    parts: [{ type: "text", text: selectedText }],
});

setMessages(newMessages);
```

This is better than leaving all alternatives in history if future turns should
build on only one answer.

## Research Workflow Pattern

The research workflow in the course looks like this:

1. `streamObject` generates a plan and search queries
2. partial plan and queries stream to the frontend as `data-*` parts
3. an external search API runs for each query
4. `streamText` synthesizes the final answer using the gathered sources

This is a good pattern when planning and answering should be separated.

## Flattened History Is Sometimes Intentional

Most normal chat routes use `await convertToModelMessages(messages)`.

Some workflows instead flatten history into a custom prompt string, especially
when the model should reason over drafts and feedback in a very controlled
format.

Use flattened history only when the workflow clearly benefits from it.

## Prompt Style in Advanced Patterns

The course commonly uses XML-like sections for advanced workflows:

- `<rules>`
- `<conversation-history>`
- `<sources>`
- `<output-format>`

Short helper calls often end with strict instructions like:

- `Return only the Slack message.`
- `Return a single number: 0 or 1.`
- `Reply as a JSON object with these properties ...`
