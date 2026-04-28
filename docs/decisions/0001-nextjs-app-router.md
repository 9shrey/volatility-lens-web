# 0001 — Next.js App Router as the web framework

**Status:** Accepted
**Date:** 2026-04

## Context
The deliverable is a *deployed URL* (not a CLI). We need: SSG/ISR, edge functions,
React Server Components, opinionated routing, and first-class Vercel integration.

## Decision
Use **Next.js 14 with the App Router**, TypeScript strict, deployed to Vercel.

## Consequences
- We commit to React Server Components and the new file-based router conventions.
- Edge Runtime is available for the small set of dynamic routes (`/api/snapshot`,
  `/api/tickers`); everything else is statically generated against the artifact bundle.
- Pages-router escape hatches and `getServerSideProps` are forbidden.
