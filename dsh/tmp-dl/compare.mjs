import { writeFile } from 'node:fs/promises'

const bases = [
  ['npmmirror', 'https://registry.npmmirror.com'],
  ['npmjs', 'https://registry.npmjs.org'],
]
for (const pkg of ['dsh-pet']) {
  for (const [label, base] of bases) {
    try {
      const meta = await (await fetch(`${base}/${pkg}`)).json()
      const v = meta['dist-tags'].latest
      const tarball = String(meta.versions[v].dist.tarball).replace('https://registry.npmjs.org', base)
      const t0 = Date.now()
      const buf = Buffer.from(await (await fetch(tarball)).arrayBuffer())
      const ms = Date.now() - t0
      console.log(`${label} ${pkg}@${v} bytes=${buf.length} ms=${ms} speed=${((buf.length / 1024) / (ms / 1000)).toFixed(0)}KB/s`)
      await writeFile(new URL(`./${pkg}-${label}.tgz`, import.meta.url), buf)
    } catch (error) {
      console.log(`${label} ${pkg}: FAILED ${error?.message ?? error}`)
    }
  }
}
