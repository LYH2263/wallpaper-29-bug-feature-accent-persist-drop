async function parseError(r) {
  const text = await r.text()
  try {
    const data = JSON.parse(text)
    if (typeof data.detail === 'string') return data.detail
    if (Array.isArray(data.detail) && data.detail.length) return data.detail[0].msg
  } catch { /* fall through to raw text */ }
  return text || `请求失败 (${r.status})`
}

export async function getJSON(path) {
  const r = await fetch(path)
  if (!r.ok) throw new Error(await parseError(r))
  return r.json()
}
export async function postJSON(path, body) {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!r.ok) throw new Error(await parseError(r))
  return r.json()
}
export async function patchJSON(path, body) {
  const r = await fetch(path, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!r.ok) throw new Error(await parseError(r))
  return r.json()
}
