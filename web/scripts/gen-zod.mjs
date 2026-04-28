#!/usr/bin/env node
/**
 * Convert the JSON Schema bundle exported by `vlens schema export` into a
 * single .ts file of zod schemas. We use it as a *check*: the hand-written
 * `lib/artifacts/schemas.ts` must remain consistent with the generated zod.
 *
 * Usage:
 *   node scripts/gen-zod.mjs <input.json> [output.ts]
 */
import { readFileSync, writeFileSync } from "node:fs";
import { jsonSchemaToZod } from "json-schema-to-zod";

const inputPath = process.argv[2] ?? "lib/artifacts/schemas.generated.json";
const outputPath = process.argv[3] ?? "lib/artifacts/schemas.generated.ts";

const bundle = JSON.parse(readFileSync(inputPath, "utf8"));

const lines = [
  "// AUTO-GENERATED. Do not edit by hand. Regenerate with `pnpm gen:schemas`.",
  'import { z } from "zod";',
  "",
];
for (const [name, schema] of Object.entries(bundle.definitions ?? {})) {
  const zodSrc = jsonSchemaToZod(schema, { name: `${name}Schema`, module: "esm" });
  lines.push(`// ${name}`);
  lines.push(zodSrc);
  lines.push("");
}
writeFileSync(outputPath, lines.join("\n"));
console.log(`wrote ${outputPath}`);
