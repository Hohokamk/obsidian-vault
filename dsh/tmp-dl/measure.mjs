import { writeFile } from 'node:fs/promises'

const pkgs = ['dsh-pet', 'billion-context']
for (const pkg of pkgs) {
  try {
    const t0 = Date.now()
    const metaRes = await fetch(`https://registry.npmjs.org/${pkg}`)
    const meta = await metaRes.json()
    const metaMs = Date.now() - t0
    const v = meta['dist-tags'].latest
    const dist = meta.versions[v].dist
    const t1 = Date.now()
    const res = await fetch(dist.tarball)
    const buf = Buffer.from(await res.arrayBuffer())
    const dlMs = Date.now() - t1
    await writeFile(new URL(`./${pkg}.tgz`, import.meta.url), buf)
    const kbps = (buf.length / 1024) / (dlMs / 1000)
    console.log(`${pkg}: latest=${v} packument=${metaMs}ms download=${dlMs}ms bytes=${buf.length} speed=${kbps.toFixed(0)}KB/s unpackedSize=${dist.unpackedSize}`)
  } catch (error) {
    console.log(`${pkg}: FAILED ${error?.message ?? error}`)
  }
}
