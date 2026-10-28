import { mkdir, readFile, writeFile } from "node:fs/promises"

const token = process.env.PROFILE_STATS_TOKEN || process.env.GITHUB_TOKEN

if (!token) {
  throw new Error("PROFILE_STATS_TOKEN or GITHUB_TOKEN is required")
}

const to = new Date()
const from = new Date(to)
from.setUTCFullYear(from.getUTCFullYear() - 1)

const query = `
  query ProfileStats($login: String!, $from: DateTime!, $to: DateTime!) {
    user(login: $login) {
      contributionsCollection(from: $from, to: $to) {
        contributionCalendar {
          totalContributions
          weeks { contributionDays { contributionCount weekday } }
        }
      }
    }
  }
`

const response = await fetch("https://api.github.com/graphql", {
  method: "POST",
  headers: {
    authorization: `bearer ${token}`,
    "content-type": "application/json",
    "user-agent": "Wuxie233-profile-stats",
  },
  body: JSON.stringify({
    query,
    variables: { login: "Wuxie233", from: from.toISOString(), to: to.toISOString() },
  }),
})

if (!response.ok) {
  throw new Error(`GitHub GraphQL request failed: ${response.status}`)
}

const payload = await response.json()
if (payload.errors?.length || !payload.data?.user) {
  throw new Error(payload.errors?.map(({ message }) => message).join("; ") || "GitHub user not found")
}

const calendar = payload.data.user.contributionsCollection.contributionCalendar
const total = calendar.totalContributions
const weeks = calendar.weeks.map((week) => week.contributionDays)
if (!Number.isInteger(total) || total < 0 || weeks.length === 0) throw new Error("Invalid contribution calendar")

const art = new URL("./art/", import.meta.url)
const pixelFont = JSON.parse(await readFile(new URL("pixel-font.json", art), "utf8")).glyphs
const glyphs = JSON.parse(await readFile(new URL("glyphs.json", art), "utf8"))

const NIGHT = "#0E0D16"
const TEXT = "#EEEAF6"
const DIM = "#A29DB8"
// Faces per level: [top, front, side]. Level 5 is the single busiest day.
const LEVELS = [
  ["#24212F", "#1A1826", "#141220"],
  ["#2E6B55", "#1F4A3C", "#173A2F"],
  ["#3E9D7B", "#2B7A5E", "#205C47"],
  ["#5BD3A6", "#3FB68B", "#2A8A67"],
  ["#A5EDD1", "#7FE0BC", "#56B894"],
  ["#F7A15A", "#D9772B", "#AE5B1B"],
]

const n = (v) => (Math.round(v * 10) / 10).toString()

function pixelText(text, x, y, p, gap, fill) {
  const cell = p + gap
  let col = 0
  let out = ""
  for (const ch of text) {
    const rows = pixelFont[ch]
    rows.forEach((row, r) => {
      ;[...row].forEach((bit, c) => {
        if (bit === "1") out += `<rect x="${n(x + (col + c) * cell)}" y="${n(y + r * cell)}" width="${p}" height="${p}" fill="${fill}"/>`
      })
    })
    col += rows[0].length + 1
  }
  return { svg: out, width: (col - 1) * cell }
}

function label(key, x, y, size, fill) {
  return `<g transform="translate(${n(x)} ${n(y)}) scale(${size / 100})" color="${fill}">${glyphs[key].svg}</g>`
}

function skyline({ x0, base, s, dx, dy, maxZ }) {
  const counts = weeks.flat().map((day) => day.contributionCount)
  const max = Math.max(1, ...counts)
  let busiest = true
  let out = ""
  for (let d = 0; d < 7; d++) {
    const depth = 6 - d
    weeks.forEach((days, w) => {
      const day = days.find((item) => item.weekday === d)
      if (!day) return
      const c = day.contributionCount
      const ratio = Math.sqrt(c / max)
      let level = c === 0 ? 0 : Math.max(1, Math.ceil(ratio * 4))
      if (c === max && busiest) {
        level = 5
        busiest = false
      }
      const [top, front, side] = LEVELS[level]
      const z = c === 0 ? 2 : 5 + ratio * maxZ
      const x = x0 + w * s + depth * dx
      const y = base - depth * dy
      const faces =
        `<polygon points="${n(x)},${n(y - z)} ${n(x + s)},${n(y - z)} ${n(x + s + dx)},${n(y - z - dy)} ${n(x + dx)},${n(y - z - dy)}" fill="${top}"/>` +
        `<polygon points="${n(x + s)},${n(y)} ${n(x + s)},${n(y - z)} ${n(x + s + dx)},${n(y - z - dy)} ${n(x + s + dx)},${n(y - dy)}" fill="${side}"/>` +
        `<rect x="${n(x)}" y="${n(y - z)}" width="${n(s)}" height="${n(z)}" fill="${front}"/>`
      out += `<g class="col" style="--w:${w}">${faces}</g>`
    })
  }
  return out
}

const style = `<style>
.col { transform-box: fill-box; transform-origin: 50% 100%; animation: grow 1s calc(var(--w) * 18ms) cubic-bezier(.16,1,.3,1) backwards; }
@keyframes grow { from { transform: scaleY(0.04); } }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
</style>`
const totalText = total.toLocaleString("en-US")
const title = `<title id="title">Wuxie's GitHub contributions over the latest rolling year</title>
<desc id="desc">${total} contributions in the latest year, drawn as a skyline of blocks, one column per day. Private activity is included only as anonymous daily counts.</desc>`

function card({ w, h, numberAt, p, labelSize, subSize, sky }) {
  const number = pixelText(totalText, numberAt.x, numberAt.y, p, 1, TEXT)
  const cap = numberAt.y + 7 * (p + 1) - 1
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-labelledby="title desc">
${title}
${style}
<rect width="${w}" height="${h}" rx="20" fill="${NIGHT}"/>
${number.svg}
${label("次贡献", numberAt.x + number.width + 16, cap, labelSize, TEXT)}
${label("最近一年", numberAt.x, cap + subSize * 1.9, subSize, DIM)}
${skyline(sky)}
</svg>
`
}

const svg = card({
  w: 1280, h: 380, numberAt: { x: 64, y: 52 }, p: 7, labelSize: 34, subSize: 20,
  sky: { x0: 64, base: 340, s: 20, dx: 10, dy: 6, maxZ: 120 },
})
const mobileSvg = card({
  w: 720, h: 560, numberAt: { x: 40, y: 48 }, p: 7, labelSize: 34, subSize: 22,
  sky: { x0: 40, base: 510, s: 11, dx: 6, dy: 5, maxZ: 230 },
})

await mkdir("assets", { recursive: true })
await writeFile("assets/github-stats.svg", svg)
await writeFile("assets/github-stats-mobile.svg", mobileSvg)
console.log(`Updated anonymous profile totals: contributions=${total} days=${weeks.flat().length}`)
