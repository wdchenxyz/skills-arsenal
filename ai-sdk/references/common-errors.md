---
title: Common Errors
description: Reference for common AI SDK errors and how to resolve them.
---

# Common Errors

## `maxTokens` -> `maxOutputTokens`

```typescript
// Incorrect
const result = await generateText({
    model: "anthropic/claude-opus-4.5",
    maxTokens: 512,
    prompt: "Write a short story",
});

// Correct
const result = await generateText({
    model: "anthropic/claude-opus-4.5",
    maxOutputTokens: 512,
    prompt: "Write a short story",
});
```

## `maxSteps` -> `stopWhen: stepCountIs(n)`

```typescript
// Incorrect
const result = await generateText({
    model: "anthropic/claude-opus-4.5",
    tools: { weather },
    maxSteps: 5,
    prompt: "What is the weather in NYC?",
});

// Correct
import { generateText, stepCountIs } from "ai";

const result = await generateText({
    model: "anthropic/claude-opus-4.5",
    tools: { weather },
    stopWhen: stepCountIs(5),
    prompt: "What is the weather in NYC?",
});
```

## `parameters` -> `inputSchema` in tool definitions

```typescript
// Incorrect
const weatherTool = tool({
    description: "Get weather for a location",
    parameters: z.object({
        location: z.string(),
    }),
    execute: async ({ location }) => ({ location, temp: 72 }),
});

// Correct
const weatherTool = tool({
    description: "Get weather for a location",
    inputSchema: z.object({
        location: z.string(),
    }),
    execute: async ({ location }) => ({ location, temp: 72 }),
});
```

## `generateObject` -> `generateText` with `output`

`generateObject` still exists, but the v6-native pattern is often
`generateText` with `output`.

```typescript
// Older pattern
import { generateObject } from "ai";

const result = await generateObject({
    model: "anthropic/claude-opus-4.5",
    schema: z.object({
        recipe: z.object({
            name: z.string(),
            ingredients: z.array(z.string()),
        }),
    }),
    prompt: "Generate a recipe for chocolate cake",
});

console.log(result.object);

// Preferred v6 pattern
import { generateText, Output } from "ai";

const result = await generateText({
    model: "anthropic/claude-opus-4.5",
    output: Output.object({
        schema: z.object({
            recipe: z.object({
                name: z.string(),
                ingredients: z.array(z.string()),
            }),
        }),
    }),
    prompt: "Generate a recipe for chocolate cake",
});

console.log(result.output);
```

## Manual JSON parsing -> `generateText` with `output`

```typescript
// Incorrect
const result = await generateText({
    model: "anthropic/claude-opus-4.5",
    prompt: `Extract the user info as JSON: { "name": string, "age": number }

Input: John is 25 years old`,
});

const parsed = JSON.parse(result.text);

// Correct
import { generateText, Output } from "ai";

const result = await generateText({
    model: "anthropic/claude-opus-4.5",
    output: Output.object({
        schema: z.object({
            name: z.string(),
            age: z.number(),
        }),
    }),
    prompt: "Extract the user info: John is 25 years old",
});

console.log(result.output);
```

## Other `output` helpers

```typescript
const arrayResult = await generateText({
    model: "anthropic/claude-opus-4.5",
    output: Output.array({
        element: z.object({
            city: z.string(),
            country: z.string(),
        }),
    }),
    prompt: "List 5 capital cities",
});

const choiceResult = await generateText({
    model: "anthropic/claude-opus-4.5",
    output: Output.choice({
        options: ["positive", "negative", "neutral"] as const,
    }),
    prompt: "Classify the sentiment: I love this product!",
});

const jsonResult = await generateText({
    model: "anthropic/claude-opus-4.5",
    output: Output.json(),
    prompt: "Return some JSON data",
});
```

## `toDataStreamResponse` -> `toUIMessageStreamResponse`

When the frontend uses `useChat`, prefer UI message streams.

```typescript
// Incorrect
const result = streamText({ model, messages });
return result.toDataStreamResponse();

// Correct
const result = streamText({ model, messages });
return result.toUIMessageStreamResponse();
```

## Removed managed input state in `useChat`

`useChat` no longer owns your input state.

```tsx
// Older pattern
const { input, handleInputChange, handleSubmit } = useChat({
    api: "/api/chat",
});

// Current pattern
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { useState } from "react";

export default function Page() {
    const [input, setInput] = useState("");
    const { sendMessage } = useChat({
        transport: new DefaultChatTransport({ api: "/api/chat" }),
    });

    return (
        <form
            onSubmit={(event) => {
                event.preventDefault();
                sendMessage({ text: input });
                setInput("");
            }}
        >
            <input value={input} onChange={(e) => setInput(e.target.value)} />
            <button type="submit">Send</button>
        </form>
    );
}
```

If the project already uses the default `/api/chat` route and no custom
transport config is needed, many course examples simply use `useChat({})`.

## `tool-invocation` -> typed `tool-{toolName}` parts

Prefer typed tool parts over the old catch-all part type.

```tsx
// Older pattern
message.parts.map((part) => {
    if (part.type === "tool-invocation") {
        return <pre>{JSON.stringify(part.toolInvocation, null, 2)}</pre>;
    }
});

// Current pattern
message.parts.map((part) => {
    switch (part.type) {
        case "text":
            return part.text;
        case "tool-getWeatherInformation":
            return <WeatherView invocation={part} />;
        default:
            return null;
    }
});
```

## `useChat` state-dependent property access

Tool part properties only exist in some states.

```tsx
// Incorrect
if (part.type === "tool-getWeather") {
    const location = part.input.location;
}

// Correct
if (
    part.type === "tool-getWeather" &&
    (part.state === "input-available" || part.state === "output-available")
) {
    const location = part.input.location;
}

// Incorrect
if (part.type === "tool-getWeather") {
    const weather = part.output;
}

// Correct
if (part.type === "tool-getWeather" && part.state === "output-available") {
    const weather = part.output;
}
```

## `part.toolInvocation.args` -> `part.input`

```tsx
// Older pattern
const location = part.toolInvocation.args.location;

// Current pattern
const location = part.input.location;
```

## `part.toolInvocation.result` -> `part.output`

```tsx
// Older pattern
const weather = part.toolInvocation.result;

// Current pattern
const weather = part.output;
```

## `part.toolInvocation.toolCallId` -> `part.toolCallId`

```tsx
// Older pattern
const id = part.toolInvocation.toolCallId;

// Current pattern
const id = part.toolCallId;
```

## Tool invocation states renamed

```tsx
// Older pattern
switch (part.toolInvocation.state) {
    case "partial-call":
        return <div>Loading...</div>;
    case "call":
        return <div>Executing...</div>;
    case "result":
        return <div>Done</div>;
}

// Current pattern
switch (part.state) {
    case "input-streaming":
        return <div>Loading...</div>;
    case "input-available":
        return <div>Executing...</div>;
    case "output-available":
        return <div>Done</div>;
}
```

## `addToolResult` -> `addToolOutput`

```tsx
// Older pattern
addToolResult({
    toolCallId: part.toolInvocation.toolCallId,
    result: "Yes, confirmed.",
});

// Current pattern
addToolOutput({
    tool: "askForConfirmation",
    toolCallId: part.toolCallId,
    output: "Yes, confirmed.",
});
```

## `messages` -> `uiMessages` in `createAgentUIStreamResponse`

```typescript
// Incorrect
return createAgentUIStreamResponse({
    agent: myAgent,
    messages,
});

// Correct
return createAgentUIStreamResponse({
    agent: myAgent,
    uiMessages: messages,
});
```

## `convertToModelMessages` is async

```typescript
// Incorrect
const modelMessages = convertToModelMessages(messages);

// Correct
const modelMessages = await convertToModelMessages(messages);
```

## `system` -> `instructions` on `ToolLoopAgent`

```typescript
// Incorrect
const agent = new ToolLoopAgent({
    model,
    system: "You are a helpful assistant.",
    tools,
});

// Correct
const agent = new ToolLoopAgent({
    model,
    instructions: "You are a helpful assistant.",
    tools,
});
```

## `partialObjectStream` vs `partialOutputStream`

`streamText` with `Output.object(...)` uses `partialOutputStream`.

`streamObject(...)` uses `partialObjectStream`.

```typescript
// Incorrect
const result = streamText({
    model,
    output: Output.object({ schema }),
    prompt: "Generate facts",
});

for await (const chunk of result.partialObjectStream) {
    console.log(chunk);
}

// Correct
for await (const chunk of result.partialOutputStream) {
    console.log(chunk);
}
```

## `onFinish` not firing because the stream was never consumed

```typescript
const result = streamText({
    model,
    prompt: "Hello, world!",
    onFinish: () => {
        console.log("finished");
    },
});

await result.consumeStream();
```

This matters especially when you merge one stream into another and later need
`await result.text` or rely on `onFinish` side effects.

## Skipping `validateUIMessages` for inbound chat history

```typescript
// Risky
const messages: UIMessage[] = body.messages;

// Safer
const messages = await validateUIMessages({
    messages: body.messages,
});
```

This is especially important once tools, custom data parts, and metadata are
part of the request body.

## Mixing up model-level and UI-level `onFinish`

```typescript
const result = streamText({
    model,
    messages: await convertToModelMessages(messages),
    onFinish: ({ response }) => {
        // response.messages are model messages
    },
});

return result.toUIMessageStreamResponse({
    originalMessages: messages,
    onFinish: ({ messages, responseMessage }) => {
        // messages is full UI history
        // responseMessage is the latest assistant UI message
    },
});
```

## Forgetting `sendStart: false` or `sendFinish: false` when merging child streams

```typescript
writer.write({ type: "start" });

writer.merge(
    result.toUIMessageStream({
        sendStart: false,
        sendFinish: false,
    }),
);
```

If you already started the outer message, nested child streams should usually
not emit their own `start` or `finish` parts.

## Streaming custom `data-*` updates without a stable `id`

```typescript
// Incorrect
for await (const chunk of stream.textStream) {
    writer.write({
        type: "data-suggestion",
        id: crypto.randomUUID(),
        data: chunk,
    });
}

// Correct
const suggestionId = crypto.randomUUID();
let fullSuggestion = "";

for await (const chunk of stream.textStream) {
    fullSuggestion += chunk;
    writer.write({
        type: "data-suggestion",
        id: suggestionId,
        data: fullSuggestion,
    });
}
```

Reusing the same id lets the frontend reconcile updates into one logical part.
