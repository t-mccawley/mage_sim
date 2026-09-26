# MageSim

Monte Carlo DpS simulator for the WoW Forever Mage. It runs every compatible
combination of character, encounter, rotation, and talent build (a *candidate*)
and writes an HTML report comparing them.

## Setup

```sh
uv sync
```

## Run

```sh
uv run magesim                    # simulate and open the report
uv run magesim --no-open          # just write results/magesim_<timestamp>.html
uv run magesim --refresh-talents  # re-download Wowhead talent data first
uv run magesim spellbook          # write results/spellbook.csv (use --out - for stdout)
```

## Configure (`configs/`)

| File | Exports | Notes |
|---|---|---|
| `character.py` | `CHARACTERS: list[Character]` | Stats from the in-game sheet; percent stats in percent. Includes the water used for drinking. |
| `encounters.py` | `ENCOUNTERS: list[Encounter]` | Type, duration, enemy count, health, and level delta. Leveling encounters also set `drink_below_mana_pct`. |
| `rotations.py` | `ROTATIONS: list[Rotation]` | A function `(SimState) -> spell or None`, called whenever the character can act. |
| `talents.py` | `TALENT_URLS: list[str]` | Links from https://www.wowhead.com/forever/talent-calc/mage |
| `meta.py` | `META: MetaConfig` | Seed, iterations, tick size, and peak-DpS warmup. |
| `spellbook.py` | `SPELL_RANKS: dict[SpellId, list[SpellRank]]` | In-game values per rank: level, mana, damage, cast/channel time, cooldown, DoT. Spells with no ranks are never known. |

Every combination whose rotation `encounter_type` matches the encounter's type
is a candidate. A candidate is **invalid** (not simulated, listed with reasons in
the terminal and the report) when:
- the talent build's required level differs from the character's level;
- a `rank_overrides` rank doesn't exist or is learned above the character's level;
- the rotation uses a spell the character can't have: a talent spell (Pyroblast,
  Ice Lance, Arcane Blast) without the talent, or a spell first learned above
  the character's level.

  This is detected by scanning the rotation function's source, even for
  branches that never run, and by a probe run that covers helper functions.
  A spell whose `.known` the rotation checks counts as handled, so adaptive
  rotations like `sb.pyroblast if sb.pyroblast.known else sb.fireball` stay valid.

### Writing a rotation

```python
def fire(s: SimState) -> SpellChoice:
    sb = s.spells
    if s.target is not None and s.target.health_pct < 20 and sb.fire_blast.ready:
        return sb.fire_blast
    if sb.pyroblast.ready:
        return sb.pyroblast
    return sb.fireball
```

Each spell handle exposes `known`, `ready`, `on_cooldown`, `cooldown_remaining`,
`mana_cost`, `affordable`, `cast_time`, and `rank`. `SimState` also exposes
`time`, `mana`, `mana_pct`, `target` (`health_pct`, `frozen`, `has_dot(...)`),
`enemies`, `clearcasting`, and `arcane_blast_stacks`.

Each spell casts at the highest rank known at the character's level, unless the
rotation pins one, e.g. `Rotation(..., rank_overrides={SpellId.FROSTBOLT: 1})`.
Casts are reported per rank ("Fireball (Rank 4)").

If a pick is on cooldown or unaffordable, the character waits one tick, and
the lost time is reported as "blocked".

## Encounter types

- `single_target` / `multi_target_aoe`: every enemy engages at once. The fight
  ends at `duration` or when all enemies die, and DpS = damage / elapsed time.
- `multi_target_leveling`: pulls of `enemy_count` enemies repeat until
  `duration`. Between pulls the character drinks to full if mana is below
  `drink_below_mana_pct`. Overkill is not counted, so DpS measures kill speed
  including drinking time.

## Outputs

For each candidate, total DpS and peak DpS (the largest cumulative DpS after
the warmup window) are reported as `median (low - high)`. The range is a 90%
bootstrap confidence interval of the median: iterations are resampled with
replacement `bootstrap_samples` times. Both the level and the resample count
are set in `meta.py`.

The report shows:
- One chart with Total (blue) and Peak (red) bars per candidate, sorted by
  total DpS. Hover for a summary; click a bar to open its talent calculator.
- The median cumulative-DpS time series.
- A sortable, filterable Candidate Legend with damage share, kills, drinking
  time, blocked picks, and any talents that aren't modeled.

## Data sources and modeling

- **Spells, talents, and water**: WoW Forever data from Wowhead. Talent data is
  snapshotted in `src/magesim/data/forever_mage_talents.json`.
- **Formulas**: [wowsims/classic](https://github.com/wowsims/classic).
  - Hit table: 4/5/6/17% base miss vs +0/+1/+2/+3 enemies, and 3/2/1% vs -1/-2/-3.
  - Crit damage is 1.5x. Higher-level enemies suppress crit and add 2% partial
    resists per level.
  - Mage spirit regen is 12.5 + Spirit/4 per 2 s, gated by the five-second rule.
- **Coefficients**: calculated from `configs/spellbook.py` with the Classic formula
  (`src/magesim/spells/coefficients.py`):
  - Direct damage: cast time / 3.5, clamped to 1.5-3.5 s.
  - Channels: duration / 3.5, split across ticks.
  - DoTs: duration / 15.
  - Each is multiplied by a per-spell scale (AoE 1/3, slow/root 0.95, a few
    fitted to wowsims).
  - No low-level penalty: Classic cuts ranks learned below level 20 by 3.75%
    per level, but the Forever beta client stores the full coefficient on every
    rank (per [ForeverChanges](https://foreverchanges.pro/downrank-calculator),
    read from client build 1.60.1.70009). A server-side penalty would not show
    up in client data and hasn't been ruled out in game.
  - Tests check this reproduces wowsims/classic for ranks learned at level 20+.
    Ice Lance and Arcane Blast are new in Forever, so they use the standard
    formula unadjusted.
  - Audit everything with `magesim spellbook`.
- **Spellbook**: every rank from level 1 to 60 of 15 damage spells.
  - Trainer spells: Fireball, Frostbolt, Frostfire Bolt, Fire Blast, Scorch,
    Flamestrike, Arcane Missiles, Arcane Explosion, Frost Nova, Cone of Cold,
    and Blizzard.
  - Talent spells: Pyroblast, Ice Lance, Arcane Blast, and Blast Wave. Every
    rank requires the talent.
  - Frostfire Bolt counts as both Fire and Frost. It uses the better school's
    hit, crit, and spell power, and gets both schools' damage bonuses.
- **Talents**: every Arcane/Fire/Frost talent in rows 0-2 that affects damage.
  Deeper talents are parsed but flagged as unmodeled in the report.
- **Not modeled**: gear, movement and range, damage taken, spell pushback,
  Frost Nova breaking on damage, and rune abilities.

## Development

```sh
uv run pytest
uv run mypy
uv run ruff check && uv run ruff format --check
```
