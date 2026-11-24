// Entry point for news-image-20261123.
//
// What it does, in plain terms: the repository ships the finished
// front page as entry.png (drawn by generate_image.py). This program
// checks that file is a real, whole 1024x1024 PNG and copies its exact
// bytes to the output directory the grader gives us, so both graded
// runs write identical bytes. It uses only the Node standard library.

import { copyFile, mkdir, readFile, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { createHash } from "node:crypto";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const EXPECTED_WIDTH = 1024;
const EXPECTED_HEIGHT = 1024;

function fail(message: string): never {
  console.error(`error: ${message}`);
  process.exit(1);
}

function readPngSize(bytes: Buffer): { width: number; height: number } {
  // A PNG starts with an 8-byte signature, then a 25-byte IHDR chunk:
  // 4 bytes length, 4 bytes "IHDR", then width and height as big-endian
  // 32-bit integers. Anything shorter cannot be a whole PNG header.
  if (bytes.length < 8 + 25) {
    fail("entry.png is too short to hold a PNG header");
  }
  if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) {
    fail("entry.png does not start with the PNG signature");
  }
  const chunkType = bytes.toString("latin1", 12, 16);
  if (chunkType !== "IHDR") {
    fail("entry.png has no IHDR chunk where the header belongs");
  }
  return {
    width: bytes.readUInt32BE(16),
    height: bytes.readUInt32BE(20),
  };
}

async function main(): Promise<void> {
  const here = dirname(fileURLToPath(import.meta.url));
  const source = join(here, "entry.png");

  const info = await stat(source).catch(() => {
    fail(`cannot find ${source}`);
  });
  if (info.size === 0) {
    fail("entry.png is empty");
  }

  const bytes = await readFile(source);
  const { width, height } = readPngSize(bytes);
  if (width !== EXPECTED_WIDTH || height !== EXPECTED_HEIGHT) {
    fail(
      `entry.png is ${width}x${height}, expected ` +
        `${EXPECTED_WIDTH}x${EXPECTED_HEIGHT}`,
    );
  }

  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
  const target = join(outDir, "entry.png");
  await mkdir(outDir, { recursive: true });
  await copyFile(source, target);

  const digest = createHash("sha256").update(bytes).digest("hex");
  console.log(`checked entry.png: ${width}x${height}, ${bytes.length} bytes`);
  console.log(`sha256: ${digest}`);
  console.log(`wrote ${target}`);

  // Read the copy back and make sure the grader will see the same bytes.
  const written = await readFile(target);
  const writtenDigest = createHash("sha256").update(written).digest("hex");
  if (writtenDigest !== digest) {
    fail("the copied entry.png does not match the source bytes");
  }
  console.log("copy verified: output bytes match the source");
}

await main();
