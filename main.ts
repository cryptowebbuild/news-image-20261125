import { copyFileSync, existsSync, mkdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';

/**
 * Deterministic entrypoint for news-image-20261125.
 * Copies the verified 1024x1024 PNG summary of Wednesday 25 November 2026
 * to /output/entry.png (or MAKEFUN_OUTPUT_DIR outside the sandbox).
 */
const srcPath = new URL('./entry.png', import.meta.url);
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const destPath = join(outDir, 'entry.png');

if (!existsSync(srcPath)) {
  throw new Error('Missing entry.png artifact beside main.ts');
}

mkdirSync(dirname(destPath), { recursive: true });
copyFileSync(srcPath, destPath);

const size = statSync(destPath).size;
if (size === 0 || size > 1048576) {
  throw new Error(`Invalid entry.png size: ${size} bytes`);
}
