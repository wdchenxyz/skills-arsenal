---
title: Structured Output and Multimodal
description: Course-derived patterns for Output.object, streamObject, and file/image inputs.
---

# Structured Output and Multimodal

The course prefers the v6-native structured-output path first, then uses
`streamObject` when a workflow benefits from a dedicated object stream.

## Preferred Structured Output Pattern

For normal structured generation, prefer `generateText` with `output`:

```ts
import { generateText, Output } from "ai";
import z from "zod";

const result = await generateText({
    model,
    prompt: "Generate facts about this planet.",
    output: Output.object({
        schema: z.object({
            facts: z.array(z.string()),
        }),
    }),
});

console.log(result.output);
```

Use this mental model:

- `generateText(..., output: Output.object(...))` -> `result.output`
- `streamText(..., output: Output.object(...))` -> `result.partialOutputStream`
- `generateObject(...)` -> `result.object`
- `streamObject(...)` -> `result.partialObjectStream`

## Do Not Mix Up `partialOutputStream` and `partialObjectStream`

This is an easy mistake to make:

```ts
const result = streamText({
    model,
    prompt: "Generate facts.",
    output: Output.object({ schema }),
});

for await (const chunk of result.partialOutputStream) {
    console.log(chunk);
}
```

Use `partialOutputStream` with `streamText + Output.object`.

Use `partialObjectStream` with `streamObject`.

## When the Course Uses `streamObject`

The course still uses `streamObject` when:

- partial object fields drive UI updates
- loop control depends on structured fields like `isGoodEnough`
- plan or query generation is inherently object-shaped

```ts
const evaluation = streamObject({
    model,
    schema: z.object({
        feedback: z.string().optional(),
        isGoodEnough: z.boolean(),
    }),
    prompt,
});

for await (const part of evaluation.partialObjectStream) {
    if (part.feedback) {
        writer.write({
            type: "data-feedback",
            id: feedbackId,
            data: part.feedback,
        });
    }
}

const finalEvaluation = await evaluation.object;
```

Wait for `await result.object` before branching on final values.

## File and Image Inputs Start on the Client

In the course, multimodal input is usually created in the client by sending a
`parts` array, not by adding special backend logic.

```tsx
import type { FileUIPart } from "ai";

const filePart: FileUIPart | undefined = file
    ? {
          type: "file",
          url: await fileToDataURL(file),
          mediaType: file.type,
      }
    : undefined;

sendMessage({
    parts: [{ type: "text", text: input }, ...(filePart ? [filePart] : [])],
});
```

On the server, the usual chat route often stays the same:

```ts
const modelMessages = await convertToModelMessages(messages);
const result = streamText({ model, messages: modelMessages });
```

## Multimodal Model Choice

Pick a model that can understand the file or image you are sending. In this
course, Gemini examples commonly use `google('gemini-2.5-flash')` for image
and file input.

## Zod Descriptions Help

The course frequently uses `.describe(...)` in structured schemas. Keep them
short and specific when they improve the model's behavior.
