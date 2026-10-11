for (const pkg of ['dsh-pet', 'billion-context']) {
  const meta = await (await fetch(`https://registry.npmjs.org/${pkg}`)).json()
  const v = meta['dist-tags'].latest
  const version = meta.versions[v]
  console.log(JSON.stringify({
    pkg,
    version: v,
    published: meta.time?.[v],
    files: version.dist?.fileCount,
    unpackedSize: version.dist?.unpackedSize,
    tarball: version.dist?.tarball,
    scripts: version.scripts ?? null,
    dependencies: Object.keys(version.dependencies ?? {}),
    optionalDependencies: Object.keys(version.optionalDependencies ?? {}),
    engines: version.engines ?? null,
  }, null, 2))
}
