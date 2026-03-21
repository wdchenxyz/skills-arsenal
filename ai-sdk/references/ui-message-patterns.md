---
title: UIMessage Patterns
description: Course-derived patterns for UIMessage, ModelMessage, validation, and persistence.
---

# UIMessage Patterns

The course is heavily `UIMessage`-centric. Treat `UIMessage` as the UI and
storage format, and `ModelMessage` as the model-call format.

## UIMessage vs ModelMessage

- Persist and render `UIMessage`
- Convert to `ModelMessage` only at the API boundary
- Use `await convertToModelMessages(messages)` before `streamText` or
  `generateText`

```ts
import {
    convertToModelMessages,
    streamText,
    type ModelMessage,
    type UIMessage,
} from "ai";

const messages: UIMessage[] = body.messages;

const modelMessages: ModelMessage[] = await convertToModelMessages(messages);

const result = streamText({
    model,
    messages: modelMessages,
});
```

## Validate Messages at the Request Boundary

Once tools, metadata, and custom parts enter the picture, validate incoming
messages before converting them:

```ts
import { validateUIMessages, type UIMessage } from "ai";

let messages: UIMessage[];

try {
    messages = await validateUIMessages({
        messages: body.messages,
    });
} catch {
    return new Response("Invalid messages", { status: 400 });
}
```

## UIMessage Type Parameters

The course frequently uses custom metadata and custom data parts:

```ts
import type { InferUITools, UIMessage } from "ai";

type MyMessage = UIMessage<
    {
        model: "advanced" | "basic";
    },
    {
        plan: string;
        queries: string[];
    },
    InferUITools<typeof tools>
>;
```

`UIMessage` takes three type arguments:

1. message metadata
2. custom `data-*` parts
3. typed tool parts

## Persistence: Full History vs Latest Reply

The course distinguishes between model-level and UI-level `onFinish` data.

```ts
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

Use this rule of thumb:

- `streamText.onFinish.response.messages` when you want raw model output
- `toUIMessageStreamResponse.onFinish.messages` when persisting chat history
- `toUIMessageStreamResponse.onFinish.responseMessage` when persisting just
  the newest assistant message

## Explicit Chat IDs for Persistence

When chat history must survive reloads, the course passes explicit ids into
`useChat` and hydrates the hook with existing messages.

```tsx
const [backupChatId, setBackupChatId] = useState(crypto.randomUUID());

const { messages, sendMessage } = useChat({
    id: chatIdFromUrl ?? backupChatId,
    messages: data?.messages ?? [],
});
```

Keep fallback ids stable in state. Do not call `crypto.randomUUID()` inline on
every render.

## Rewriting History Is Valid

The course sometimes rewrites message history after a user picks between
multiple outputs:

```tsx
const newMessages = messages.slice(0, index);

newMessages.push({
    ...message,
    parts: [{ type: "text", text: selectedText }],
});

setMessages(newMessages);
```

This pattern is useful when the assistant should continue from a chosen result,
not from all candidates.
