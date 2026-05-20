<!-- markdownlint-disable MD013 -->
<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

# 🚀 Git Auto Commit (`gac`)

[![PyPI version](https://img.shields.io/pypi/v/gac.svg)](https://pypi.org/project/gac/)
[![Changelog](https://img.shields.io/badge/changelog-kittylog-10b981)](https://kittylog.app/c/thomwebb/gac)
[![Python](https://img.shields.io/badge/python-3.10--3.14-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://github.com/cellwebb/gac/actions/workflows/ci.yml/badge.svg)](https://github.com/cellwebb/gac/actions)
[![codecov](https://codecov.io/gh/cellwebb/gac/branch/main/graph/badge.svg)](https://app.codecov.io/gh/cellwebb/gac)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](docs/sv/CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[**English**](../../README.md) | [简体中文](docs/zh-CN/README.md) | [繁體中文](docs/zh-TW/README.md) | [日本語](docs/ja/README.md) | [한국어](docs/ko/README.md) | [हिन्दी](docs/hi/README.md) | [Tiếng Việt](docs/vi/README.md) | [Français](docs/fr/README.md) | [Русский](docs/ru/README.md) | [Español](docs/es/README.md) | [Português](docs/pt/README.md) | [Norsk](docs/no/README.md) | **Svenska** | [Deutsch](docs/de/README.md) | [Nederlands](docs/nl/README.md) | [Italiano](docs/it/README.md)

**LLM-drivna commit-meddelanden som förstår din kod!**

**Automatisera dina commits!** Ersätt `git commit -m "..."` med `uvx gac` för kontekstuell, velformaterade commit-meddelanden genererade av stora språkmodeller!

---

## Vad Du Får

Intelligenta, kontextuella meddelanden som förklarar **varför** bakom dina ändringar:

![GAC generating a contextual commit message](assets/gac-simple-usage.sv.png)

---

</div>

<!-- markdownlint-enable MD033 MD036 -->

## Snabbstart

```bash
uvx gac init   # Konfigurera din leverantör, modell och språk
uvx gac        # Generera och commit med LLM
```

Det är allt! Granska det genererade meddelandet och bekräfta med `y`.

---

## Nyckelfunktioner

### 🌐 **30+ Stödda Leverantörer**

- **Anthropic** • **Azure OpenAI** • **Cerebras** • **ChatGPT (OAuth)** • **Chutes.ai** • **Claude Code (OAuth)**
- **Crof.ai** • **DeepInfra** • **DeepSeek** • **Fireworks** • **Gemini** • **GitHub Copilot (OAuth)** • **Groq**
- **Kimi for Coding** • **LM Studio** • **MiniMax.io** • **Mistral AI** • **Moonshot AI** • **Neuralwatt** • **Ollama**
- **OpenAI** • **OpenCode Go** • **OpenRouter** • **Qwen Cloud (CN & INTL)** • **Replicate** • **Streamlake/Vanchin**
- **Synthetic.new** • **Together AI** • **Wafer.ai** • **Z.AI (API & Coding Plans)**
- **Custom Endpoints (Anthropic/OpenAI)**

### 🧠 **Smart LLM-analys**

- **Förstår avsikt**: Analyserar kodstruktur, logik och mönster för att förstå "varför" bakom dina ändringar, inte bara vad som ändrades
- **Semantisk medvetenhet**: Känner igen refactoring, bug-fixer, funktioner och breaking changes för att generera kontextuellt lämpliga meddelanden
- **Intelligent filtrering**: Prioriterar meningsfulla ändringar medan den ignorerar genererade filer, beroenden och artefakter
- **Intelligent commit-gruppering** - Gruppera automatiskt relaterade ändringar i flera logiska commits med `--group`

### 📝 **Flera Meddelandeformat**

- **En-rads** (-o flagga): Enkel-rads commit-meddelande som följer conventional commit-format
- **Standard** (standard): Sammanfattning med punktlista som förklarar implementeringsdetaljer
- **Utförlig** (-v flagga): Omfattande förklaringar inklusive motivation, teknisk ansats och påverkananalys
- **50/72-regel** (--50-72 flagga): Tvinga det klassiska commit-meddelandeformatet för optimal läsbarhet i git log och GitHub UI
- **DCO/Signoff** (--signoff flagga): Lägg till Signed-off-by-rad för Developer Certificate of Origin-efterlevnad (krävs av Cherry Studio, Linux-kärnan och andra projekt)

### 🌍 **Flerspråkigt Stöd**

- **25+ språk**: Generera commit-meddelanden på engelska, kinesiska, japanska, koreanska, spanska, franska, tyska och 18+ fler språk
- **Flexibel översättning**: Välj att behålla conventional commit-prefix på engelska för verktygskompatibilitet, eller översätt dem helt
- **Flera arbetsflöden**: Ställ in ett standardspråk med `uvx gac language`, eller använd `-l <språk>` flagget för engångsöverstyrning
- **Stöd för originalskript**: Fullt stöd för icke-latinska skript inklusive CJK, kyrilliska, thai och mer

### 💻 **Utvecklarupplevelse**

- **Interaktiv feedback**: Skriv `r` för att köra om, `e` för att redigera (inbyggd TUI som standard, eller `$GAC_EDITOR` om angiven), eller skriv din feedback direkt som `gör den kortare` eller `fokusera på bug-fixen`
- **Interaktiv frågning**: Använd `--interactive` (`-i`) för att svara på riktade frågor om dina ändringar för mer kontextuella commit-meddelanden
- **Ett-kommandos arbetsflöden**: Kompletta arbetsflöden med flaggor som `uvx gac -ayp` (stage alla, auto-bekräfta, push)
- **Git-integration**: Respekterar pre-commit och lefthook hooks, kör dem innan dyra LLM-operationer
- **MCP-server**: Kör `uvx gac serve` för att exponera commit-verktyg till AI-agenter via [Model Context Protocol](https://modelcontextprotocol.io/)

### 📊 **Användningsstatistik**

```bash
uvx gac stats               # Översikt: totala gacs, streaks, dagliga/veckovisa toppar, topprojekt & -modeller
uvx gac stats models        # Modelluppdelning: gacs, tokens, latens, hastighet, latens-per-commit-diagram
uvx gac stats projects      # Projektuppdelning: gacs, commits, tokens, snitt filer per gac över alla repo
uvx gac stats recent        # Senaste gac-historik: tokens, hastighet, latens, filer per gac (-n 20 för fler)
uvx gac stats reset         # Återställ all statistik (ber om bekräftelse)
uvx gac stats reset model <model-id>  # Återställ statistik endast för en specifik modell
```

- **Spåra dina gacs**: Se hur många commits du har gjort med gac, din nuvarande streak, topp dagliga/veckovisa aktivitet och topprojekt
- **Token-spårning**: Totalt antal prompt-, output- och reasoning-tokens per dag, vecka, projekt och modell — med highscore-troféer för tokenanvändning också
- **Toppmodeller**: Se vilka modeller du använder mest och hur många tokens var och en förbrukar
- **Highscore-firanden**: 🏆 troféer när du sätter nya dagliga, veckovisa, token- eller streak-rekord; 🥈 för att matcha dem
- **Opt-in vid installation**: `uvx gac init` frågar om du vill aktivera statistik och förklarar exakt vad som sparas
- **Opt-out när som helst**: Ställ in `GAC_DISABLE_STATS=true` (eller `1`/`yes`/`on`) för att inaktivera. Att ställa in den på `false`/`0`/`no` (eller ta bort den) håller statistiken aktiverad
- **Integritet först**: Lagrat lokalt i `~/.gac_stats.json`. Endast antal, datum, projektnamn och modellnamn — inga commit-meddelanden, kod eller personlig information. Ingen telemetri

### 🛡️ **Inbyggd Säkerhet**

- **Automatisk hemlighetsdetektering**: Skannar efter API-nycklar, lösenord och tokens innan commit
- **Interaktivt skydd**: Frågar innan commit av potentiellt känslig data med tydliga åtgärdsalternativ
- **Smart filtrering**: Ignorerar exempelfiler, mallfiler och platshållar-text för att minska falska positiva

---

## Användningsexempel

### Grundläggande Arbetsflöde

```bash
# Stage dina ändringar
git add .

# Generera och commit med LLM
uvx gac

# Granska → y (commit) | n (avbryt) | r (köra om) | e (redigera) | eller skriv feedback
```

### Vanliga Kommandon

| Kommando            | Beskrivning                                                        |
| ------------------- | ------------------------------------------------------------------ |
| `uvx gac`           | Generera commit-meddelande                                         |
| `uvx gac -y`        | Auto-bekräfta (ingen granskning behövs)                            |
| `uvx gac -a`        | Stage alla innan generering av commit-meddelande                   |
| `uvx gac -S`        | Välj interaktivt filer att stagea                                  |
| `uvx gac -o`        | En-rads meddelande för triviala ändringar                          |
| `uvx gac -v`        | Utförligt format med Motivation, Teknisk Ansats och Påverkananalys |
| `uvx gac -h "hint"` | Lägg till kontext för LLM (t.ex., `uvx gac -h "bug fix"`)          |
| `uvx gac -s`        | Inkludera scope (t.ex., feat(auth):)                               |
| `uvx gac -i`        | Ställ frågor om ändringar för bättre kontext                       |
| `uvx gac -g`        | Gruppera ändringar i flera logiska commits                         |
| `uvx gac -p`        | Commit och push                                                    |
| `uvx gac stats`     | Visa din gac-användningsstatistik                                  |

### Exempel för Avancerade Användare

```bash
# Komplett arbetsflöde i ett kommando
# Visa din commitstatistik
uvx gac stats

# Statistik för alla projekt
uvx gac stats projects

uvx gac -ayp -h "release preparation"

# Detaljerad förklaring med scope
uvx gac -v -s

# Snabb en-rads för små ändringar
uvx gac -o

# Generera commitmeddelande på ett specifikt språk
uvx gac -l sv

# Gruppera ändringar i logiskt relaterade commits
uvx gac -ag

# Interaktivt läge med utförlig output för detaljerade förklaringar
uvx gac -iv

# Debug vad LLM ser
uvx gac --show-prompt

# Hoppa över säkerhetsskanning (använd med försiktighet)
uvx gac --skip-secret-scan

# Lägg till signoff för DCO-efterlevnad (Cherry Studio, Linux-kärnan, etc.)
uvx gac --signoff
```

### Interaktivt Feedbacksystem

Inte nöjd med resultatet? Du har flera alternativ:

```bash
# Enkel omspelning (ingen feedback)
r

# Redigera commit-meddelandet
e

# Eller skriv bara din feedback direkt!
gör den kortare och fokusera på prestandaförbättringen
använd conventional commit-format med scope
förklara säkerhetsimplicationerna

# Tryck Enter på tom input för att se prompten igen
```

Redigeringsfunktionen (`e`) låter dig förfina commit-meddelandet:

- **Som standard (inbyggd TUI)**: Flerradersredigering med vi/emacs-tangentbindningar — korrigera stavfel, justera formuleringar, omstrukturera
- **Med `GAC_EDITOR`**: Öppnar din föredragna editor (`code`, `vim`, `nano` osv.) — full editor-kraft inklusive sök/ersätt, makron osv.

GUI-editorer som VS Code hanteras automatiskt: gac infogar `--wait` så att processen blockeras tills du stänger editor-fliken. Ingen extra konfiguration behövs.

---

## Konfiguration

Kör `uvx gac init` för att konfigurera din leverantör interaktivt, eller sätt miljövariabler:

Behöver du ändra leverantörer eller modeller senare utan att röra språkinställningar? Använd `uvx gac model` för ett strömlinjeformat flöde som hoppar över språkfrågorna.

```bash
# Exempelkonfiguration
GAC_MODEL=anthropic:your-model-name
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

Se `.gac.env.example` för alla tillgängliga alternativ.

**Vill du ha commit-meddelanden på ett annat språk?** Kör `uvx gac language` för att välja från 25+ språk inklusive Español, Français, 日本語 och mer.

**Vill du anpassa commit-meddelandestil?** Se [docs/CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md) för vägledning om att skriva anpassade system-prompts.

---

## Få Hjälp

- **Full dokumentation**: [USAGE.md](USAGE.md) - Komplett CLI-referens
- **MCP-server**: [MCP.md](MCP.md) - Använd GAC som MCP-server för AI-agenter
- **Claude Code OAuth**: [docs/CLAUDE_CODE.md](docs/sv/CLAUDE_CODE.md) - Claude Code konfiguration och autentisering
- **ChatGPT OAuth**: [docs/CHATGPT_OAUTH.md](docs/sv/CHATGPT_OAUTH.md) - ChatGPT OAuth konfiguration och autentisering
- **Anpassade prompts**: [CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md) - Anpassa commit-meddelandestil
- **Användningsstatistik**: Se `uvx gac stats --help` eller den [fulla dokumentationen](USAGE.md#användningsstatistik)
- **Felsökning**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Vanliga problem och lösningar
- **Bidra**: [CONTRIBUTING.md](CONTRIBUTING.md) - Utvecklings-setup och riktlinjer

---

<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

[⭐ Stjärna oss på GitHub](https://github.com/cellwebb/gac) • [🐛 Rapportera problem](https://github.com/cellwebb/gac/issues) • [📖 Full dokumentation](USAGE.md)

</div>

<!-- markdownlint-enable MD033 MD036 -->
