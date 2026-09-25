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
```

## Configure (`configs/`)

| File | Exports | Notes |
|---|---|---|
| `character.py` | `CHARACTERS: list[Character]` | Stats from the in-game sheet; percent stats in percent. Includes the water used for drinking. |
| `encounters.py` | `ENCOUNTERS: list[Encounter]` | Type, duration, enemy count, health, and level delta. Leveling encounters also set `drink_below_mana_pct`. |
| `rotations.py` | `ROTATIONS: list[Rotation]` | A function `(SimState) -> spell or None`, called whenever the character can act. |
| `talents.py` | `TALENT_URLS: list[str]` | Links from https://www.wowhead.com/forever/talent-calc/mage |
| `meta.py` | `META: MetaConfig` | Seed, iterations, tick size, and peak-DpS warmup. |

A candidate is simulated only when the rotation's `encounter_type` matches the
encounter's type and the talent build's required level equals the character's level.

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
`enemies`, `clearcasting`, and `arcane_blast_stacks`. The highest rank known at
the character's level is used. If the pick can't be cast (not known, on
cooldown, or not enough mana), the character waits one tick; the lost time is
reported as "blocked".

## Encounter types

- `single_target` / `multi_target_aoe`: every enemy engages at once. The fight
  ends at `duration` or when all enemies die, and DpS = damage / elapsed time.
- `multi_target_leveling`: pulls of `enemy_count` enemies repeat until
  `duration`. Between pulls the character drinks to full if mana is below
  `drink_below_mana_pct`. Overkill is not counted, so DpS measures kill speed
  including drinking time.

## Outputs

For each candidate: median, p15, and p85 of total DpS and of peak DpS (the
largest cumulative DpS after the warmup window), plus the median cumulative-DpS
time series. The report also shows damage share, kills, drinking time,
blocked picks, and any talents that aren't modeled.

## Data sources and modeling

- **Spells, talents, and water**: WoW Forever data from Wowhead. Talent data is
  snapshotted in `src/magesim/data/forever_mage_talents.json`.
- **Formulas**: [wowsims/classic](https://github.com/wowsims/classic).
  - Hit table: 4/5/6/17% base miss vs +0/+1/+2/+3 enemies, and 3/2/1% vs -1/-2/-3.
  - Crit damage is 1.5x. Higher-level enemies suppress crit and add 2% partial
    resists per level.
  - Mage spirit regen is 12.5 + Spirit/4 per 2 s, gated by the five-second rule.
- **Coefficients**: per-rank wowsims values. Coefficients for Frost Nova,
  Ice Lance, and Arcane Blast are estimates (marked in `spellbook.py`).
- **Spellbook**: trainer spells with ranks up to level 22, plus the
  talent-granted Pyroblast, Ice Lance, and Arcane Blast.
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
