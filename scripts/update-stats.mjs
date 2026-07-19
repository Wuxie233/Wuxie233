import { mkdir, writeFile } from "node:fs/promises"

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
        contributionCalendar { totalContributions }
        totalCommitContributions
        totalIssueContributions
        totalPullRequestContributions
        totalRepositoriesWithContributedCommits
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

const stats = payload.data.user.contributionsCollection
const values = [
  ["CONTRIBUTIONS", stats.contributionCalendar.totalContributions],
  ["COMMITS", stats.totalCommitContributions],
  ["ISSUES", stats.totalIssueContributions],
  ["PULL REQUESTS", stats.totalPullRequestContributions],
  ["COMMIT REPOS", stats.totalRepositoriesWithContributedCommits],
]

for (const [label, value] of values) {
  if (!Number.isInteger(value) || value < 0) throw new Error(`Invalid ${label} value`)
}

const blocks = values.map(([label, value], index) => {
  const x = 54 + index * 238
  const color = ["#2457FF", "#FF5A36", "#168C78", "#111111", "#2457FF"][index]
  const valueColor = index === 1 ? "#111111" : "#FFFFFF"
  return `
    <rect x="${x}" y="110" width="218" height="105" fill="${color}"/>
    <text x="${x + 18}" y="147" fill="${valueColor}" font-size="16" font-weight="700">${label}</text>
    <text x="${x + 18}" y="193" fill="${valueColor}" font-size="38" font-weight="800">${value.toLocaleString("en-US")}</text>`
}).join("")

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="270" viewBox="0 0 1280 270" role="img" aria-labelledby="title desc">
  <title id="title">Wuxie's latest rolling-year GitHub activity</title>
  <desc id="desc">${values.map(([label, value]) => `${label}: ${value}`).join(", ")}. Private activity is included only as anonymous totals.</desc>
  <rect width="1280" height="270" fill="#F4F4F0"/>
  <text x="54" y="48" fill="#111111" font-family="Arial, sans-serif" font-size="15" font-weight="700">GITHUB / LATEST ROLLING YEAR</text>
  <text x="1226" y="48" fill="#555555" text-anchor="end" font-family="Arial, sans-serif" font-size="14">PUBLIC + ANONYMOUS PRIVATE TOTALS</text>
  <path d="M54 69H1226" stroke="#111111" stroke-width="2"/>
  <g font-family="Arial, sans-serif">${blocks}
  </g>
  <text x="54" y="247" fill="#555555" font-family="Arial, sans-serif" font-size="13">Generated in this repository with GitHub GraphQL · no third-party stats service</text>
</svg>
`

const mobileBlocks = values.map(([label, value], index) => {
  const y = 142 + index * 106
  const color = ["#2457FF", "#FF5A36", "#168C78", "#111111", "#2457FF"][index]
  const valueColor = index === 1 ? "#111111" : "#FFFFFF"
  return `
    <rect x="42" y="${y}" width="636" height="86" fill="${color}"/>
    <text x="64" y="${y + 35}" fill="${valueColor}" font-size="18" font-weight="700">${label}</text>
    <text x="656" y="${y + 59}" fill="${valueColor}" text-anchor="end" font-size="36" font-weight="800">${value.toLocaleString("en-US")}</text>`
}).join("")

const mobileSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="720" height="730" viewBox="0 0 720 730" role="img" aria-labelledby="title desc">
  <title id="title">Wuxie's latest rolling-year GitHub activity</title>
  <desc id="desc">${values.map(([label, value]) => `${label}: ${value}`).join(", ")}. Private activity is included only as anonymous totals.</desc>
  <rect width="720" height="730" fill="#F4F4F0"/>
  <text x="42" y="48" fill="#111111" font-family="Arial, sans-serif" font-size="17" font-weight="700">GITHUB / LATEST ROLLING YEAR</text>
  <text x="42" y="80" fill="#555555" font-family="Arial, sans-serif" font-size="14">PUBLIC + ANONYMOUS PRIVATE TOTALS</text>
  <path d="M42 105H678" stroke="#111111" stroke-width="2"/>
  <g font-family="Arial, sans-serif">${mobileBlocks}
  </g>
  <text x="42" y="696" fill="#555555" font-family="Arial, sans-serif" font-size="13">Generated with GitHub GraphQL · no third-party stats service</text>
</svg>
`

await mkdir("assets", { recursive: true })
await writeFile("assets/github-stats.svg", svg)
await writeFile("assets/github-stats-mobile.svg", mobileSvg)
console.log(`Updated anonymous profile totals: ${values.map(([label, value]) => `${label}=${value}`).join(" ")}`)
