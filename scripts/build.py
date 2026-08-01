"""
PPOTY season dashboard builder.

Scans data/tournaments/*.tdt (raw Tournament Director exports), parses each
one, and writes data/season.json -- the single data file the dashboard
(index.html) fetches at load time.

Config (edit these by hand as the league changes -- no code changes needed):
    config/roster.json    the 12 official league members. Anyone else who
                           plays is treated as a non-scoring guest.
    config/seasons.json   season date ranges. A season with "end": null is
                           the current, still-open season.
    config/history.json   hand-maintained year-by-year champions list, for
                           years that predate digital tournament records.

Run locally:
    python3 scripts/build.py

This is also invoked automatically by .github/workflows/build.yml whenever
a new .tdt file is pushed to data/tournaments/.
"""
import os
import re
import sys
import json
import glob
import datetime

# ---------------------------------------------------------------------------
# Parser for TD's .tdt save format (a relaxed JS-object-literal dialect, not
# valid JSON: unquoted keys, values wrapped in `new ClassName(...)`, and
# `Map.from([[k,v],...])` for maps).
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, s):
        self.s = s
        self.i = 0
        self.n = len(s)

    def ws(self):
        while self.i < self.n and self.s[self.i] in ' \t\r\n':
            self.i += 1

    def peek(self):
        return self.s[self.i] if self.i < self.n else ''

    def parse_value(self):
        self.ws()
        c = self.peek()
        if c == '{':
            return self.parse_object()
        if c == '[':
            return self.parse_array()
        if c == '"':
            return self.parse_string()
        if self.s.startswith('new ', self.i):
            return self.parse_new()
        if self.s.startswith('Map.from(', self.i):
            self.i += len('Map.from')
            return self.parse_call('Map.from')
        if self.s.startswith('true', self.i):
            self.i += 4
            return True
        if self.s.startswith('false', self.i):
            self.i += 5
            return False
        if self.s.startswith('null', self.i):
            self.i += 4
            return None
        if self.s.startswith('undefined', self.i):
            self.i += 9
            return None
        m = re.match(r'-?\d+(\.\d+)?([eE][+-]?\d+)?', self.s[self.i:])
        if m:
            txt = m.group(0)
            self.i += len(txt)
            return float(txt) if ('.' in txt or 'e' in txt or 'E' in txt) else int(txt)
        raise ValueError(f"Unexpected char at {self.i}: {self.s[self.i:self.i+50]!r}")

    def parse_ident(self):
        m = re.match(r'[A-Za-z_$][A-Za-z0-9_$]*(\.[A-Za-z_$][A-Za-z0-9_$]*)*', self.s[self.i:])
        if not m:
            raise ValueError(f"Expected identifier at {self.i}: {self.s[self.i:self.i+50]!r}")
        txt = m.group(0)
        self.i += len(txt)
        return txt

    def parse_new(self):
        self.i += 4
        self.ws()
        name = self.parse_ident()
        return self.parse_call(name)

    def parse_call(self, name):
        self.ws()
        assert self.peek() == '(', f"expected ( after {name} at {self.i}"
        self.i += 1
        self.ws()
        if self.peek() == ')':
            self.i += 1
            inner = None
        else:
            inner = self.parse_value()
            self.ws()
            assert self.peek() == ')', f"expected ) at {self.i}"
            self.i += 1
        if name == 'Map.from':
            d = {}
            for pair in inner:
                d[pair[0]] = pair[1]
            return {"__map__": True, "data": d}
        if isinstance(inner, dict):
            inner = dict(inner)
            inner['__class__'] = name
        return inner

    def parse_string(self):
        self.i += 1
        out = []
        while True:
            c = self.s[self.i]
            if c == '\\':
                nxt = self.s[self.i + 1]
                mapping = {'n': '\n', 't': '\t', 'r': '\r', '"': '"', '\\': '\\', '/': '/', 'b': '\b', 'f': '\f'}
                if nxt == 'u':
                    out.append(chr(int(self.s[self.i + 2:self.i + 6], 16)))
                    self.i += 6
                elif nxt in mapping:
                    out.append(mapping[nxt])
                    self.i += 2
                else:
                    out.append(nxt)
                    self.i += 2
            elif c == '"':
                self.i += 1
                break
            else:
                out.append(c)
                self.i += 1
        return ''.join(out)

    def parse_object(self):
        self.i += 1
        obj = {}
        self.ws()
        if self.peek() == '}':
            self.i += 1
            return obj
        while True:
            self.ws()
            key = self.parse_string() if self.peek() == '"' else self.parse_ident()
            self.ws()
            assert self.peek() == ':'
            self.i += 1
            obj[key] = self.parse_value()
            self.ws()
            if self.peek() == ',':
                self.i += 1
                self.ws()
                if self.peek() == '}':
                    self.i += 1
                    break
                continue
            elif self.peek() == '}':
                self.i += 1
                break
            else:
                raise ValueError(f"expected , or }} at {self.i}")
        return obj

    def parse_array(self):
        self.i += 1
        arr = []
        self.ws()
        if self.peek() == ']':
            self.i += 1
            return arr
        while True:
            arr.append(self.parse_value())
            self.ws()
            if self.peek() == ',':
                self.i += 1
                self.ws()
                if self.peek() == ']':
                    self.i += 1
                    break
                continue
            elif self.peek() == ']':
                self.i += 1
                break
            else:
                raise ValueError(f"expected , or ] at {self.i}")
        return arr


def parse_tdt(path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        data = fh.read()
    return Parser(data).parse_value()


# ---------------------------------------------------------------------------
# Per-tournament extraction
# ---------------------------------------------------------------------------

def fee_lookup(buy_config):
    out = {}
    if not buy_config:
        return out
    for prof in buy_config.get('Profiles', []) or []:
        out[prof.get('Name')] = prof.get('Fee', 0) or 0
    return out


def extract_tournament(path):
    data = parse_tdt(path)
    t = data['T']

    title = t.get('Title') or ''
    start_ms = t.get('StartTime') or 0
    date = None
    if start_ms:
        date = datetime.datetime.utcfromtimestamp(start_ms / 1000).strftime('%Y-%m-%d')

    players_raw = t['Players']['Players']['data']
    buyin_fees = fee_lookup(t.get('Financials', {}).get('Buyins'))
    addon_fees = fee_lookup(t.get('Financials', {}).get('AddOns'))

    prizes = t.get('Prizes', {}).get('Prizes', []) or []

    prize_by_place = {}
    max_prize_place = 0
    for prize in prizes:
        place = prize.get('Recipient')
        awarded = prize.get('AwardedToPlayers') or []
        dollars_total = prize.get('CalculatedAmount', 0) or 0
        if awarded:
            prize_by_place[place] = {
                'uuids': awarded,
                'dollars_each': dollars_total / len(awarded),
            }
            max_prize_place = max(max_prize_place, place)

    players_out = []
    active_count = 0

    for uuid, p in players_raw.items():
        name = p['Name']['Nickname']
        buyins = p.get('Buyins', []) or []
        addons = p.get('AddOns', []) or []

        fee_paid = sum(buyin_fees.get(b.get('ProfileName'), 0) for b in buyins)
        fee_paid += sum(addon_fees.get(a.get('ProfileName'), 0) for a in addons)

        last_buyin = max(buyins, key=lambda b: b.get('Time', 0)) if buyins else None
        still_active = bool(last_buyin) and not last_buyin.get('BustOut')
        if still_active:
            active_count += 1

        bustout_times = [b['BustOut']['Time'] for b in buyins if b.get('BustOut')]
        last_bustout_time = max(bustout_times) if bustout_times else None

        players_out.append({
            'uuid': uuid,
            'name': name,
            'num_buyins': len(buyins),
            'num_addons': len(addons),
            'fee_paid': fee_paid,
            'still_active': still_active,
            'last_bustout_time': last_bustout_time,
        })

    incomplete = active_count != 1

    place_map, dollars_map = {}, {}
    for place, info in prize_by_place.items():
        for u in info['uuids']:
            place_map[u] = place
            dollars_map[u] = dollars_map.get(u, 0) + info['dollars_each']

    unplaced = [pl for pl in players_out if pl['uuid'] not in place_map and not pl['still_active']]
    unplaced.sort(key=lambda pl: (pl['last_bustout_time'] or 0), reverse=True)

    next_place = max_prize_place + 1
    for pl in unplaced:
        place_map[pl['uuid']] = next_place
        next_place += 1

    for pl in players_out:
        pl['place'] = place_map.get(pl['uuid'])
        pl['prize_dollars'] = round(dollars_map.get(pl['uuid'], 0), 2)
        pl['net'] = round(pl['prize_dollars'] - pl['fee_paid'], 2)

    players_out.sort(key=lambda pl: (pl['place'] is None, pl['place'] if pl['place'] is not None else 999))

    return {
        'title': title,
        'date': date,
        'start_ms': start_ms,
        'num_players': len(players_out),
        'total_pot': round(sum(pl['fee_paid'] for pl in players_out), 2),
        'incomplete': incomplete,
        'players': players_out,
    }


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def season_for_date(date_str, seasons):
    """Return the season dict whose [start, end] window contains date_str."""
    if not date_str:
        return None
    for s in seasons:
        if s['start'] and date_str < s['start']:
            continue
        if s.get('end') and date_str > s['end']:
            continue
        return s
    return None


def current_season(seasons):
    """The open-ended season (end == null), or failing that the one with the
    latest start date."""
    open_seasons = [s for s in seasons if not s.get('end')]
    if open_seasons:
        return max(open_seasons, key=lambda s: s['start'])
    if seasons:
        return max(seasons, key=lambda s: s['start'])
    return None


# ---------------------------------------------------------------------------
# Season aggregation
# ---------------------------------------------------------------------------

def build_season(tdt_paths, roster, seasons, manual_games=None):
    # roster: list of {"spreadsheet_name": ..., "display_name": ...}
    # display_name is the Nickname that actually shows up in Tournament
    # Director's exports -- that's what we match against. spreadsheet_name
    # (e.g. "Whited", "Harrison") is what the dashboard displays, matching
    # the league's spreadsheet.
    nickname_to_canonical = {
        m['display_name'].strip().lower(): m['spreadsheet_name'] for m in roster
    }

    tournaments = []
    for path in sorted(tdt_paths):
        try:
            rec = extract_tournament(path)
        except Exception as e:
            print(f"WARNING: failed to parse {path}: {e}", file=sys.stderr)
            continue
        rec['source_file'] = os.path.basename(path)
        tournaments.append(rec)

    # manual_games: pre-parsed tournament dicts (e.g. transcribed from a
    # spreadsheet, before real .tdt exports exist for them). They already
    # carry 'is_roster' / 'display_name' per player, so they skip the
    # nickname-matching step below.
    for g in (manual_games or []):
        tournaments.append(g)

    complete = [t for t in tournaments if not t['incomplete']]
    skipped = [t['source_file'] for t in tournaments if t['incomplete']]
    complete.sort(key=lambda t: t['start_ms'] or 0)

    for t in complete:
        s = season_for_date(t['date'], seasons)
        t['season_id'] = s['id'] if s else None
        for pl in t['players']:
            if 'is_roster' in pl and 'display_name' in pl:
                continue  # already resolved (manual game entry)
            canonical = nickname_to_canonical.get(pl['name'].strip().lower())
            pl['is_roster'] = canonical is not None
            # display_name is what shows up everywhere on the dashboard:
            # the spreadsheet name for roster members, the raw TD nickname
            # for guests.
            pl['display_name'] = canonical or pl['name']

    cur_season = current_season(seasons)
    cur_season_id = cur_season['id'] if cur_season else None

    # per-season per-player aggregation (roster members only)
    seasons_out = {}
    for s in seasons:
        players = {}
        season_tournaments = [t for t in complete if t['season_id'] == s['id']]
        for t in season_tournaments:
            for pl in t['players']:
                if not pl['is_roster']:
                    continue
                rec = players.setdefault(pl['uuid'], {
                    'uuid': pl['uuid'],
                    'name': pl['display_name'],
                    'tournaments_played': 0,
                    'wins': 0,
                    'cashes': 0,
                    'total_winnings': 0.0,
                    'total_fees': 0.0,
                    'net': 0.0,
                    'best_place': None,
                    'sum_place': 0,
                    'history': [],
                })
                rec['name'] = pl['display_name']
                rec['tournaments_played'] += 1
                rec['wins'] += 1 if pl['place'] == 1 else 0
                rec['cashes'] += 1 if pl['prize_dollars'] > 0 else 0
                rec['total_winnings'] += pl['prize_dollars']
                rec['total_fees'] += pl['fee_paid']
                rec['net'] += pl['net']
                rec['sum_place'] += pl['place'] or 0
                if pl['place'] is not None:
                    rec['best_place'] = pl['place'] if rec['best_place'] is None else min(rec['best_place'], pl['place'])
                rec['history'].append({
                    'date': t['date'],
                    'title': t['title'],
                    'place': pl['place'],
                    'num_players': t['num_players'],
                    'prize_dollars': pl['prize_dollars'],
                    'fee_paid': pl['fee_paid'],
                    'net': pl['net'],
                    'cumulative_winnings': None,
                    'cumulative_net': None,
                })

        for rec in players.values():
            cum_w, cum_n = 0.0, 0.0
            for h in rec['history']:
                cum_w += h['prize_dollars']
                cum_n += h['net']
                h['cumulative_winnings'] = round(cum_w, 2)
                h['cumulative_net'] = round(cum_n, 2)
            rec['avg_place'] = round(rec['sum_place'] / rec['tournaments_played'], 2) if rec['tournaments_played'] else None
            rec['itm_pct'] = round(rec['cashes'] / rec['tournaments_played'], 4) if rec['tournaments_played'] else 0
            rec['total_winnings'] = round(rec['total_winnings'], 2)
            rec['total_fees'] = round(rec['total_fees'], 2)
            rec['net'] = round(rec['net'], 2)

        players_list = sorted(players.values(), key=lambda r: r['total_winnings'], reverse=True)
        leader_total = players_list[0]['total_winnings'] if players_list else 0
        for r in players_list:
            r['diff'] = round(r['total_winnings'] - leader_total, 2)

        seasons_out[s['id']] = {
            'id': s['id'],
            'label': s['label'],
            'start': s['start'],
            'end': s.get('end'),
            'num_tournaments': len(season_tournaments),
            'players': players_list,
        }

    return {
        'generated_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'current_season_id': cur_season_id,
        'roster': sorted(m['spreadsheet_name'] for m in roster),
        'seasons': seasons_out,
        'skipped_incomplete_files': skipped,
        'tournaments': [
            {
                'title': t['title'],
                # Only games added by email carry a separate host; the older
                # spreadsheet ones keep it inside the title string.
                'host': t.get('host'),
                'date': t['date'],
                'season_id': t['season_id'],
                'num_players': t['num_players'],
                'total_pot': t['total_pot'],
                'source_file': t['source_file'],
                'results': [
                    {
                        'name': pl['display_name'],
                        'place': pl['place'],
                        'prize_dollars': pl['prize_dollars'],
                        'net': pl['net'],
                        'is_roster': pl['is_roster'],
                    }
                    for pl in t['players']
                ],
            }
            for t in complete
        ],
    }


def build_schedule(schedule_cfg):
    events = schedule_cfg.get('events', []) or []
    return sorted(events, key=lambda e: e.get('date') or '')


def build_message(message_cfg):
    text = (message_cfg or {}).get('text')
    if not text:
        return None
    return {'text': text, 'updated': (message_cfg or {}).get('updated')}


def build_photos(photos_cfg):
    photos = photos_cfg.get('photos', []) or []
    out = []
    for p in photos:
        pid = p.get('id')
        if not pid:
            continue
        out.append({
            'id': pid,
            'date': p.get('date'),
            'thumb': f'photos/thumbs/{pid}.jpg',
            'full': f'photos/full/{pid}.jpg',
        })
    return sorted(out, key=lambda p: p.get('date') or '', reverse=True)


def build_history(history_cfg):
    champions = history_cfg.get('champions', [])
    counts = {}
    for c in champions:
        name = c.get('name')
        if not name:
            continue
        counts[name] = counts.get(name, 0) + 1
    trophy_counts = sorted(
        [{'name': n, 'count': c} for n, c in counts.items()],
        key=lambda r: r['count'],
        reverse=True,
    )
    return {
        'champions': sorted(champions, key=lambda c: c['year']),
        'trophy_counts': trophy_counts,
        'years_tracked': len([c for c in champions if c.get('name')]),
    }


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tdt_dir = os.path.join(root, 'data', 'tournaments')
    manual_games_path = os.path.join(root, 'data', 'manual_games.json')
    out_path = os.path.join(root, 'data', 'season.json')
    config_dir = os.path.join(root, 'config')

    roster_cfg = load_json(os.path.join(config_dir, 'roster.json'), {'members': []})
    seasons_cfg = load_json(os.path.join(config_dir, 'seasons.json'), {'seasons': []})
    history_cfg = load_json(os.path.join(config_dir, 'history.json'), {'champions': []})
    schedule_cfg = load_json(os.path.join(config_dir, 'schedule.json'), {'events': []})
    photos_cfg = load_json(os.path.join(config_dir, 'photos.json'), {'photos': []})
    message_cfg = load_json(os.path.join(config_dir, 'message.json'), {'text': None})

    roster = roster_cfg.get('members', [])
    seasons = seasons_cfg.get('seasons', [])
    manual_games = load_json(manual_games_path, [])

    tdt_paths = glob.glob(os.path.join(tdt_dir, '*.tdt'))
    if not tdt_paths and not manual_games:
        print(f"No .tdt files found in {tdt_dir} and no data/manual_games.json", file=sys.stderr)
    if not roster:
        print("WARNING: config/roster.json has no members -- no one will count toward season stats", file=sys.stderr)
    if not seasons:
        print("WARNING: config/seasons.json has no seasons -- tournaments won't be bucketed", file=sys.stderr)

    season_data = build_season(tdt_paths, roster, seasons, manual_games)
    season_data['history'] = build_history(history_cfg)
    season_data['scheduled_games'] = build_schedule(schedule_cfg)
    season_data['photos'] = build_photos(photos_cfg)
    season_data['message'] = build_message(message_cfg)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(season_data, f, indent=2)

    print(f"Wrote {out_path}")
    for sid, s in season_data['seasons'].items():
        print(f"  Season {sid} ({s['label']}): {s['num_tournaments']} tournaments, {len(s['players'])} scoring players")
    if season_data['skipped_incomplete_files']:
        print(f"  Skipped (incomplete): {season_data['skipped_incomplete_files']}")


if __name__ == '__main__':
    main()
