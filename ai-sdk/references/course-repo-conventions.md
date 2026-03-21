---
title: Course Repo Conventions
description: Patterns used throughout the AI SDK v6 crash course repo.
---

# Course Repo Conventions

These notes capture the patterns used throughout the
`ai-sdk-v6-crash-course` repo. When a task is clearly in that repo, or in
another repo with the same exercise layout, prefer these conventions over
generic Next.js examples.

## Project Shape

- `main.ts` usually just boots the local dev server with
  `runLocalDevServer({ root: import.meta.dirname })`.
- `api/chat.ts` usually exports `POST(req: Request): Promise<Response>`.
- `client/root.tsx` owns `useChat`, local input state, and page composition.
- `client/components.tsx` renders `message.parts`.
- The local dev server is Vite plus Hono-style Request/Response handlers.
  Do not assume `app/api/chat/route.ts` or App Router helpers.

## Local Lookup Strategy

For this course repo, search in this order:

1. `exercises/**`, especially `99-reference/**`
2. `node_modules/ai/dist/index.d.ts`
3. `node_modules/ai/README.md`
4. `node_modules/ai/CHANGELOG.md`
5. ai-sdk.dev docs

`ai@6.0.5` in this repo does not bundle `node_modules/ai/docs/` or
`node_modules/ai/src/`.

## Provider and Model Defaults

The course usually imports providers directly:

```ts
import { google } from "@ai-sdk/google";
import { openai } from "@ai-sdk/openai";
import { anthropic } from "@ai-sdk/anthropic";
```

Common environment variables:

- `GOOGLE_GENERATIVE_AI_API_KEY`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

Common course defaults:

- `google('gemini-2.5-flash-lite')` for cheap classifiers, titles, evals,
  and small helper calls
- `google('gemini-2.5-flash')` for chat, tool calling, multimodal input,
  and richer generation

The course does not default to AI Gateway. Use direct provider imports first
unless the user explicitly wants Gateway-based examples.

## Standard Chat Route Pattern

This is the most common server pattern in the course:

```ts
import { google } from "@ai-sdk/google";
import {
    convertToModelMessages,
    createUIMessageStreamResponse,
    streamText,
    type ModelMessage,
    type UIMessage,
} from "ai";

export const POST = async (req: Request): Promise<Response> => {
    const body = await req.json();
    const messages: UIMessage[] = body.messages;

    const modelMessages: ModelMessage[] =
        await convertToModelMessages(messages);

    const result = streamText({
        model: google("gemini-2.5-flash"),
        messages: modelMessages,
    });

    return createUIMessageStreamResponse({
        stream: result.toUIMessageStream(),
    });
};
```

## Standard Client Pattern

The course usually keeps input state local and renders `message.parts`:

```tsx
import { useChat } from "@ai-sdk/react";
import { useState } from "react";

export function ChatPage() {
    const { messages, sendMessage } = useChat({});
    const [input, setInput] = useState("");

    return (
        <form
            onSubmit={(event) => {
                event.preventDefault();
                sendMessage({ text: input });
                setInput("");
            }}
        >
            {messages.map((message) => (
                <div key={message.id}>
                    {message.parts.map((part, index) => {
                        if (part.type === "text") {
                            return <div key={index}>{part.text}</div>;
                        }

                        return null;
                    })}
                </div>
            ))}
            <input value={input} onChange={(e) => setInput(e.target.value)} />
        </form>
    );
}
```

## Prompting Style Used Across the Course

The course often prefers one multiline prompt with XML-like sections:

```ts
const prompt = `
  You are a helpful assistant.

  <rules>
    - Use the provided context.
    - Be concise.
  </rules>

  <conversation-history>
    ${history}
  </conversation-history>

  <output-format>
    Return only markdown.
  </output-format>
`;
```

Common sections include:

- `<rules>`
- `<examples>`
- `<conversation-history>`
- `<sources>`
- `<output-format>`

The course also relies heavily on explicit constraints like `Return only ...`
for routers, evaluators, titles, and other helper calls.
