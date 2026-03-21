---
title: Tools, Agents, and MCP
description: Course-derived patterns for streamText tool loops, ToolLoopAgent, MCP, and approval flows.
---

# Tools, Agents, and MCP

The course teaches tools in stages. Start with `streamText` tool loops, then
reach for `ToolLoopAgent` when the exercise or app is explicitly agent-based.

## Default Tool Pattern in This Course

The most common tool pattern is `streamText` with `tools` and `stopWhen`:

```ts
import { stepCountIs, streamText, tool } from "ai";
import { z } from "zod";

const result = streamText({
    model,
    messages: await convertToModelMessages(messages),
    system: "You can use tools to help the user.",
    tools: {
        readFile: tool({
            description: "Read a file",
            inputSchema: z.object({ path: z.string() }),
            execute: async ({ path }) => readFile(path),
        }),
    },
    stopWhen: [stepCountIs(10)],
});

return result.toUIMessageStreamResponse();
```

Use this first when the app is mostly a chat route with tool calling.

## Move Tools to Module Scope for Typed UI Rendering

When the frontend must render tool parts, keep the `tools` object at module
scope and infer the tool UI types from it.

```ts
import { type InferUITools, type UIMessage } from "ai";

const tools = {
    sendEmail: tool({
        description: "Send an email",
        inputSchema: z.object({
            to: z.string(),
            subject: z.string(),
            body: z.string(),
        }),
        execute: async (input) => input,
    }),
};

export type MyUIMessage = UIMessage<never, never, InferUITools<typeof tools>>;
```

This gives you typed `tool-sendEmail` parts in the frontend.

## Tool Part Rendering Pattern

The course renders tool parts by switching on `part.type` and checking the
state before accessing `input` or `output`.

```tsx
if (part.type === "tool-sendEmail") {
    if (part.state === "approval-requested") {
        return <EmailApprovalView invocation={part} />;
    }

    if (part.state === "output-available") {
        return <div>Email sent to {part.input.to}</div>;
    }
}
```

## Tool Approval Pattern

Tool approval needs both backend and frontend wiring.

Backend:

```ts
const sendEmail = tool({
    description: "Send an email",
    inputSchema: z.object({
        to: z.string(),
        subject: z.string(),
        body: z.string(),
    }),
    needsApproval: true,
    execute: async (input) => ({ sent: true, ...input }),
});
```

Frontend:

```tsx
const { messages, sendMessage, addToolApprovalResponse } = useChat<MyUIMessage>(
    {
        sendAutomaticallyWhen:
            lastAssistantMessageIsCompleteWithApprovalResponses,
    },
);
```

When the part is in `approval-requested`, call:

```tsx
addToolApprovalResponse({
    id: part.approval.id,
    approved: true,
});
```

## ToolLoopAgent Is Taught Later

The course uses `ToolLoopAgent` as a later abstraction, not the default for all
tool-based apps.

```ts
import {
    createAgentUIStreamResponse,
    InferAgentUIMessage,
    ToolLoopAgent,
} from "ai";

const agent = new ToolLoopAgent({
    model,
    instructions: "You can use tools to help the user.",
    tools,
});

export type MyAgentUIMessage = InferAgentUIMessage<typeof agent>;

return createAgentUIStreamResponse({
    agent,
    uiMessages: messages,
});
```

Important agent-specific rules:

- use `instructions`, not `system`
- use `InferAgentUIMessage<typeof agent>` for the UI type
- pass `uiMessages`, not `messages`, to `createAgentUIStreamResponse`

## MCP Pattern

The course shows both stdio and HTTP MCP clients.

Stdio MCP:

```ts
import { experimental_createMCPClient as createMCPClient } from "@ai-sdk/mcp";
import { Experimental_StdioMCPTransport as StdioMCPTransport } from "@ai-sdk/mcp/mcp-stdio";

const mcpClient = await createMCPClient({
    transport: new StdioMCPTransport({
        command: "docker",
        args: ["run", "-i", "--rm", "ghcr.io/github/github-mcp-server"],
        env: {
            GITHUB_PERSONAL_ACCESS_TOKEN:
                process.env.GITHUB_PERSONAL_ACCESS_TOKEN!,
        },
    }),
});
```

HTTP MCP:

```ts
const mcpClient = await createMCPClient({
    transport: {
        type: "http",
        url: "https://api.githubcopilot.com/mcp",
        headers: {
            Authorization: `Bearer ${process.env.GITHUB_PERSONAL_ACCESS_TOKEN}`,
        },
    },
});
```

In both cases, close the MCP client in `onFinish`:

```ts
return result.toUIMessageStreamResponse({
    onFinish: async () => {
        await mcpClient.close();
    },
});
```
