---
title: Custom Streaming Patterns
description: Course-derived patterns for createUIMessageStream, custom data parts, metadata, and merged streams.
---

# Custom Streaming Patterns

The course spends a lot of time on custom message streams. Use these patterns
whenever normal `toUIMessageStreamResponse()` is too limiting.

## Start with `createUIMessageStream`

Use `createUIMessageStream` when you need to:

- merge multiple AI SDK streams into one assistant message
- emit custom `data-*` parts
- manually write text parts
- attach message metadata during streaming

```ts
import {
    createUIMessageStream,
    createUIMessageStreamResponse,
    streamText,
    type UIMessage,
} from "ai";

type MyMessage = UIMessage<never, { suggestion: string }>;

const stream = createUIMessageStream<MyMessage>({
    execute: async ({ writer }) => {
        const result = streamText({ model, messages });
        writer.merge(result.toUIMessageStream());
    },
});

return createUIMessageStreamResponse({ stream });
```

## Merge Built-In Output, Then Write Custom Parts

One common course pattern is:

1. stream the assistant text normally
2. wait for it to finish
3. generate follow-up structured or textual UI data
4. stream that data as `data-*` parts

```ts
const stream = createUIMessageStream<MyMessage>({
    execute: async ({ writer }) => {
        const answerResult = streamText({ model, messages });

        writer.merge(answerResult.toUIMessageStream());

        await answerResult.consumeStream();

        const suggestionId = crypto.randomUUID();
        let suggestion = "";

        for await (const chunk of followupResult.textStream) {
            suggestion += chunk;
            writer.write({
                type: "data-suggestion",
                id: suggestionId,
                data: suggestion,
            });
        }
    },
});
```

## `consumeStream()` Matters

If you need `onFinish` to run, or you need `await result.text` after merging a
stream, make sure the stream is actually consumed.

```ts
const result = streamText({
    model,
    prompt: "Hello, world!",
    onFinish: () => {
        console.log("finished");
    },
});

await result.consumeStream();
```

Without consumption, `onFinish` may never fire.

## Data Part Naming Convention

The type-level key and the streamed part type do not use the same string:

```ts
type MyMessage = UIMessage<
    never,
    {
        plan: string;
        queries: string[];
    }
>;
```

Those keys become:

- `data-plan`
- `data-queries`

When writing to the stream:

```ts
writer.write({
    type: "data-plan",
    id: planId,
    data: plan,
});
```

## Stable IDs Update One UI Block

Reuse a stable `id` when streaming progressive updates for the same custom part.
Otherwise the UI accumulates multiple parts instead of updating one.

```ts
const planId = crypto.randomUUID();

for await (const part of queriesResult.partialObjectStream) {
    if (part.plan) {
        writer.write({
            type: "data-plan",
            id: planId,
            data: part.plan,
        });
    }
}
```

## Message Metadata Is Message-Level, Not Part-Level

Use metadata for information about the whole message, such as the chosen model
or duration.

```ts
type MyMessage = UIMessage<{ model: "basic" | "advanced" }>;

writer.merge(
    result.toUIMessageStream<MyMessage>({
        messageMetadata: ({ part }) => {
            if (part.type === "start") {
                return { model: "advanced" };
            }
        },
    }),
);
```

## Manual Text Streaming Uses Three Part Types

When writing text by hand, emit the full trio with the same id:

```ts
const textId = crypto.randomUUID();

writer.write({ type: "text-start", id: textId });
writer.write({ type: "text-delta", id: textId, delta: "Hello" });
writer.write({ type: "text-end", id: textId });
```

## One Outer Start and Finish Envelope

When composing multiple child streams into one assistant message, only one
coherent outer `start` and `finish` should exist.

If you already started the message, suppress nested starts and finishes:

```ts
writer.write({ type: "start" });

writer.merge(
    result.toUIMessageStream({
        sendStart: false,
        sendFinish: false,
    }),
);
```

If you forget this, the frontend can split what should be one assistant message
into multiple messages.
