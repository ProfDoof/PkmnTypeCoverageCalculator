from typing import NamedTuple
import itertools

class Interaction(NamedTuple):
    super_effective: set[str]
    not_very_effective: set[str]
    no_effect: set[str]

    def get_multiplier(self: 'Interaction', type_: str) -> float:
        if type_ in self.super_effective:
            return 2.0
        if type_ in self.not_very_effective:
            return .5
        if type_ in self.no_effect:
            return 0.0

        return 1.0

POKE_TYPES: set[str] = {
    'normal',
    'fire',
    'water',
    'grass',
    'electric',
    'ice',
    'fighting',
    'poison',
    'ground',
    'flying',
    'psychic',
    'bug',
    'rock',
    'ghost',
    'dragon',
    'dark',
    'steel',
    'fairy'
}

INTERACTIONS: dict[str, Interaction] = {
    'normal': Interaction(set(), {'rock', 'steel'}, {'ghost'}),
    'fire': Interaction({'grass', 'ice', 'bug', 'steel'}, {'fire', 'water', 'rock', 'dragon'}, set()),
    'water': Interaction({'fire', 'ground', 'rock'}, {'water', 'grass', 'dragon'}, set()),
    'grass': Interaction({'water', 'ground', 'rock'}, {'fire', 'grass', 'poison', 'flying', 'bug', 'dragon', 'steel'}, set()),
    'electric': Interaction({'water', 'flying'}, {'grass', 'electric', 'dragon'}, {'ground'}),
    'ice': Interaction({'grass', 'ground', 'flying', 'dragon'}, {'fire', 'water', 'ice', 'steel'}, set()),
    'fighting': Interaction({'normal', 'ice', 'rock', 'dark', 'steel'}, {'poison', 'flying', 'psychic', 'bug', 'fairy'}, {'ghost'}),
    'poison': Interaction({'grass', 'fairy'}, {'poison', 'ground', 'rock', 'ghost'}, {'steel'}),
    'ground': Interaction({'fire', 'electric', 'poison', 'rock', 'steel'}, {'grass', 'bug'}, {'flying'}),
    'flying': Interaction({'grass', 'fighting', 'bug'}, {'electric', 'rock', 'steel'}, set()),
    'psychic': Interaction({'fighting', 'poison'}, {'psychic', 'steel'}, {'dark'}),
    'bug': Interaction({'grass', 'psychic', 'dark'}, {'fire', 'fighting', 'poison', 'flying', 'ghost', 'steel', 'fairy'}, set()),
    'rock': Interaction({'fire', 'ice', 'flying', 'bug'}, {'fighting', 'ground', 'steel'}, set()),
    'ghost': Interaction({'psychic', 'ghost'}, {'dark'}, {'normal'}),
    'dragon': Interaction({'dragon'}, {'steel'}, {'fairy'}),
    'dark': Interaction({'psychic', 'ghost'}, {'dark', 'fairy'}, set()),
    'steel': Interaction({'ice', 'rock', 'fairy'}, {'fire', 'water', 'electric', 'steel'}, set()),
    'fairy': Interaction({'fighting', 'dragon', 'dark'}, {'fire', 'poison', 'steel'}, set()),
}


def get_types():
    type_chart: dict[str, dict[str, dict[str, float]]] = {}

    for a, d1, d2 in itertools.product(POKE_TYPES, POKE_TYPES, {'none'}.union(POKE_TYPES)):
        if a not in type_chart:
            type_chart[a] = {}

        def_chart = type_chart[a]

        if d1 not in def_chart:
            def_chart[d1] = {}
        
        att_inter = INTERACTIONS[a]
        def_chart[d1][d2] = att_inter.get_multiplier(d1) * att_inter.get_multiplier(d2)

    return type_chart


TYPE_CHART = get_types()


class Pokemon(NamedTuple):
    name: str
    type1: str
    type2: str
    tera: str
    level: int


def get_attacker_resistances(pokemon: Pokemon):
    resistances: dict[str, tuple[float, float]] = {}

    for att_type, att_chart in TYPE_CHART.items():
        att_inter = INTERACTIONS[att_type]

        base_multiplier = att_chart[pokemon.type1][pokemon.type2]
        tera_multiplier = att_inter.get_multiplier(pokemon.tera)
        resistances[att_type] = (base_multiplier, base_multiplier * tera_multiplier)

    return resistances

my_pokemon = [
    Pokemon('Sir Klark', 'water', 'fighting', 'water', 56),
    Pokemon('Trent', 'electric', 'none', 'electric', 43),
    Pokemon('Walter', 'fighting', 'flying', 'flying', 50),
    Pokemon('Eight', 'bug', 'dark', 'bug', 50),
    Pokemon('Dinner Bell', 'steel', 'psychic', 'psychic', 43),
    Pokemon('Ulfric', 'electric', 'none', 'normal', 44),
    Pokemon('Ferr', 'ground', 'none', 'rock', 41),
    Pokemon('Belton', 'electric', 'none', 'water', 55),
    Pokemon('Bounce', 'psychic', 'none', 'psychic', 51),
    Pokemon('Mustang', 'steel', 'poison', 'steel', 55),
    Pokemon('Quentin', 'bug', 'flying', 'flying', 51),
    Pokemon('Freddy', 'psychic', 'none', 'psychic', 51),
    Pokemon('Grenwich', 'ground', 'none', 'normal', 45),
    Pokemon('Fish Fry', 'water', 'none', 'water', 53),
    Pokemon('Nemo', 'dragon', 'water', 'water', 52),
    Pokemon('Cerberus', 'dark', 'fire', 'ghost', 43),
    Pokemon('Stewie', 'fire', 'none', 'fire', 55)
]

combo_scores: list[tuple[list[str], int, int]] = []
for combination in itertools.combinations(my_pokemon, 6):
    not_resisted = POKE_TYPES.copy()
    assert len(not_resisted) == 18
    for pokemon in combination:
        attacker_resistances = get_attacker_resistances(pokemon)
        for att_type, (base_resist, tera_resist) in attacker_resistances.items():
            if att_type in not_resisted and base_resist < 1.0:
                not_resisted.remove(att_type)

    combo_scores.append(([p.name for p in combination], len(not_resisted), sum(p.level for p in combination)))

from operator import itemgetter

combo_scores = sorted(combo_scores, key=itemgetter(1))
useful_combos = [(combo, level) for combo, score, level in combo_scores if score == 0]
useful_combos = sorted(useful_combos, key=itemgetter(1), reverse=True)
for combo, level in useful_combos[0:10]:
    print(combo)