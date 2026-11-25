import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_BYTES = 1_048_576;
const MAX_DIM = 1024;
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const JPEG_SOI = Buffer.from([0xff, 0xd8, 0xff]);

function computeCrc32(data: Buffer): number {
  let crc = 0xffffffff;
  for (let i = 0; i < data.length; i++) {
    crc ^= data[i];
    for (let bit = 0; bit < 8; bit++) {
      crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
    }
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function validatePngChunks(buf: Buffer): { width: number; height: number } {
  if (buf.length < 33 || !buf.subarray(0, 8).equals(PNG_MAGIC)) {
    throw new Error('Asset is not a valid PNG file.');
  }
  let offset = 8;
  let width = 0;
  let height = 0;
  let sawIend = false;

  while (offset + 12 <= buf.length) {
    const length = buf.readUInt32BE(offset);
    const type = buf.subarray(offset + 4, offset + 8).toString('ascii');
    const dataStart = offset + 8;
    const chunkEnd = dataStart + length + 4;
    if (chunkEnd > buf.length) {
      throw new Error(`Truncated PNG chunk ${type} at offset ${offset}`);
    }
    const expectedCrc = buf.readUInt32BE(dataStart + length);
    const actualCrc = computeCrc32(buf.subarray(offset + 4, dataStart + length));
    if (expectedCrc !== actualCrc) {
      throw new Error(`PNG CRC mismatch in chunk ${type}`);
    }
    if (offset === 8) {
      if (type !== 'IHDR' || length !== 13) {
        throw new Error(`Invalid first PNG chunk: ${type}`);
      }
      width = buf.readUInt32BE(dataStart);
      height = buf.readUInt32BE(dataStart + 4);
    }
    if (type === 'IEND') {
      sawIend = true;
      break;
    }
    offset = chunkEnd;
  }

  if (!sawIend || offset + 12 !== buf.length) {
    throw new Error('PNG missing terminal IEND chunk or has trailing bytes.');
  }
  return { width, height };
}

function validateImagePayload(buf: Buffer): { width: number; height: number } {
  if (buf.length === 0 || buf.length > MAX_BYTES) {
    throw new Error(`Image size out of bounds: ${buf.length} bytes`);
  }
  if (buf.subarray(0, 8).equals(PNG_MAGIC)) {
    return validatePngChunks(buf);
  }
  if (buf.subarray(0, 3).equals(JPEG_SOI) && buf[buf.length - 2] === 0xff && buf[buf.length - 1] === 0xd9) {
    return { width: MAX_DIM, height: MAX_DIM };
  }
  throw new Error('Unsupported or truncated image payload.');
}

function main(): void {
  const rootDir = dirname(fileURLToPath(import.meta.url));
  const assetPath = join(rootDir, 'assets', 'entry.png');
  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
  const outPath = join(outDir, 'entry.png');

  const payload = readFileSync(assetPath);
  const { width, height } = validateImagePayload(payload);
  if (width < 1 || height < 1 || width > MAX_DIM || height > MAX_DIM) {
    throw new Error(`Invalid dimensions: ${width}x${height}`);
  }

  mkdirSync(outDir, { recursive: true });
  writeFileSync(outPath, payload);
}

main();
