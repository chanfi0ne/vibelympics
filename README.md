# Vibelympics 🏅✨

Welcome to Chainguard's Vibelympics, our first ever vibe coding tournament, where the only rule is writing code without looking at the code!

## Our Submissions

| Round | Project | Description | Tech Stack | Link |
|-------|---------|-------------|------------|------|
| 1 | 🕳️ Emoji Zork | Dungeon crawler with 100% emoji UI | Python, Flask, Chainguard Containers | [round_1/](./round_1/) |
| 2 | 🪚 CHAINSAW | npm supply chain security auditor | Python, FastAPI, React, Docker Compose | [round_2/](./round_2/) |
| 3 | 🔮 PARANOID | SBOM roast generator with AI memes | Python, FastAPI, Claude AI, Chainguard Wolfi | [round_3/](./round_3/) |

### Round 1: Emoji Zork

A text-adventure game inspired by the classic Zork, reimagined with an all-emoji interface. Navigate through dungeons, battle enemies, and claim the crown!

**Features:**
- 🔒 **0 CVEs** - Built on Chainguard Containers
- 100% emoji-based UI (no text!)
- 7 rooms to explore
- Combat system with 4 enemy types
- Inventory management
- Keyboard controls + help overlay
- Victory confetti animation
- Ambient room particles

**Container:** `ghcr.io/chanfi0ne/vibelympics/emoji-zork:latest`

### Round 2: CHAINSAW

A containerized npm supply chain security auditor that cuts through supply chain threats. Analyze packages for typosquatting, malware, vulnerabilities, and suspicious signals.

**Features:**
- 🔒 **0 CVEs** - Security-hardened containers with non-root execution
- 8+ security signals analyzed per package
- Typosquatting detection (100+ popular packages, Levenshtein distance)
- MAL-* class malware detection from OSV/GitHub Advisory Database
- Install script analysis (preinstall/postinstall hooks)
- Sigstore provenance verification
- Risk scoring (0-100) with visual radar chart
- Terminal security aesthetic with dark theme

**Containers:**
- `ghcr.io/chanfi0ne/vibelympics/chainsaw-backend:latest`
- `ghcr.io/chanfi0ne/vibelympics/chainsaw-frontend:latest`

**Quick Start:** `docker compose up --build` then visit http://localhost:3000

### Round 3: PARANOID

An SBOM roast generator that analyzes your dependencies and roasts your questionable security choices with AI-generated memes.

**Features:**
- 🔒 **0 CVEs** - Built on Chainguard Wolfi base image
- CVE detection (55+ famous vulnerabilities)
- Cursed package detection (left-pad, event-stream, colors, etc.)
- AI-powered roasts via Claude Haiku
- Custom meme generation via memegen.link
- Paranoia system with escalating distrust
- Multi-format support (package.json, requirements.txt, go.mod, SBOM)

**Container:** `ghcr.io/chanfi0ne/vibelympics/paranoid:latest`

**Quick Start:** `docker run -p 8000:8000 paranoid` then visit http://localhost:8000

---

## Entering the Competition

To register for the competition, follow these steps:

1. Make sure you're [logged in to GitHub](https://github.com/login).
2. Navigate to the [Vibelympics repository](https://github.com/chainguard-demo/vibelympics#) (this page).
3. On the top right of the repository page, near where Stars are listed, hit the green `Use this template` button, then select `Create new repository` from the dropdown. You can also [follow this direct link](https://github.com/new?template_name=vibelympics&template_owner=chainguard-demo).
4. Fill out the create repository form, filling in the GitHub account or organization that will host your Vibelympics
 repo. We recommend naming the repo `vibelympics`, but the important thing is not to change the name of the repository after you've submitted the URL to us.
5. After creating the repository, fill out the [registration form](https://vibelympics.splashthat.com/). For the field labeled "GitHub repository URL," share the link to the repository you just created.

After registering, take next steps:

1. Edit this README with information related to the projects you create for the competition.
2. When the competition starts on December 1st, review the folder for the first round of Vibelympics for information on the challenge. You'll also receive an email from us.
3. Start vibing!

## Schedule

<table role="table" aria-label="Vibelympics Competition Schedule">
  <thead>
    <tr>
      <th scope="col">Round</th>
      <th scope="col">Opens</th>
      <th scope="col">Submission Deadline</th>
      <th scope="col">Judging & Results</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Challenge 1</th>
      <td>December 1</td>
      <td>December 4, 11:59 PM EST</td>
      <td>December 5 (advancing teams announced)</td>
    </tr>
    <tr>
      <th scope="row">Challenge 2</th>
      <td>December 8</td>
      <td>December 11, 11:59 PM EST</td>
      <td>December 12 (finalists announced)</td>
    </tr>
    <tr>
      <th scope="row">Challenge 3 (Final)</th>
      <td>December 15</td>
      <td>December 18, 11:59 PM EST</td>
      <td>December 19 (livestream judging, time TBD)</td>
    </tr>
  </tbody>
</table>

## FAQ

Q: What do you mean, don't look at the code? How are you going to enforce that.

A: We can see you through our Chainguard Omniscope at all times and we will be / are monitoring you. By the way, you should consider wearing more interesting socks.

Q: No, really. Can I look at the code?

A: No.

Q: Can the AI look at the code?

A: Yes, of course. Your'e starting to get it now.

Q: I have a cool idea for the challenge, but, like, I'm worried it violates the requirements you wrote.

A: What are you, some kind of rule follower? Just do it.

Q: Can I post about my project on *teh socials*?

A: Yes, use hashtag #vibelympics and/or tag Chainguard, we'll do our best to repost / boost.

Q: Can I get a hint or something. I read this far in the FAQ and I'm probably the only one who did that.

A: Yeah, why not. We at Chainguard love talking about our beloved octopus friend Linky, burrito bowls, and wearing hats of all kinds. We also, for some reason, like to use Uber ratings as a judge of character. If you want to pander to us you can incorporate or talk about our products (Chainguard Containers, Chainguard Libraries, and Chainguard VMs) or OSS projects we're connected to (Sigstore, K8s, SLSA, Kaniko, Tekton). 

Q: Should we pander to you? Will we win if we do that?

A: Don't you ever get tired of asking questions? You do you. 👈(❛ ᗜ ❛👈)
