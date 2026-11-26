import { mkdir, readFile, copyFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

// Locate the artwork relative to this module, not the caller's working folder.
const artwork = fileURLToPath(new URL('./entry.png', import.meta.url));
const destination = resolve(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png');
const bytes = await readFile(artwork);
const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
if (bytes.length < 33 || !bytes.subarray(0, 8).equals(signature)
    || bytes.toString('ascii', 12, 16) !== 'IHDR') {
  throw new Error('The artwork lacks a complete PNG header. Run draw.py first.');
}
if (bytes.readUInt32BE(16) !== 1024 || bytes.readUInt32BE(20) !== 1024
    || bytes.length > 1024 * 1024) {
  throw new Error('Artwork must be 1024 × 1024 and no larger than 1 MiB.');
}
await mkdir(dirname(destination), { recursive: true });
if (resolve(artwork) !== destination) {
  await copyFile(artwork, destination);
}
console.log(`Published ${bytes.length} bytes to ${destination}`);
