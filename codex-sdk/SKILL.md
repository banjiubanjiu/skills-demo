---
name: codex-sdk
description: Programmatically control local Codex agents via the TypeScript Codex SDK. Use when integrating Codex into CI/CD pipelines, building custom agents, wiring Codex into internal tools or applications, or when working with @openai/codex-sdk, threads, and resumeThread usage.
---

# Codex SDK

## Overview

Use the TypeScript Codex SDK to control local Codex agents from a Node.js server-side application. Prefer it over non-interactive mode when you need deeper integration, custom orchestration, or app-level workflows.

## Requirements

- Run server-side with Node.js 18 or later.

## Install

```bash
npm install @openai/codex-sdk
```

## Start a thread and run a prompt

```ts
import { Codex } from "@openai/codex-sdk";

const codex = new Codex();
const thread = codex.startThread();
const result = await thread.run(
    "Make a plan to diagnose and fix the CI failures"
);

console.log(result);
```

## Continue or resume a thread

```ts
// continue the same thread
const result = await thread.run("Implement the plan");

console.log(result);

// resume a past thread
const threadId = "<thread-id>";
const thread2 = codex.resumeThread(threadId);
const result2 = await thread2.run("Pick up where you left off");

console.log(result2);
```

## Reference

- TypeScript repo: https://github.com/openai/codex/tree/main/sdk/typescript
