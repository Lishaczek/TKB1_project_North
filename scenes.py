from textwrap import dedent

def choice(label, target, cid=None, condition=None, action=None, once=False, reaction=None, custom_text=None):
    """
    - reaction: Může být string nebo LAMBDA pro dynamickou změnu.
    """
    return {
        "label": label, "target": target, "cid": cid,
        "condition": condition, "action": action, "once": once,
        "reaction": reaction, "custom_text": custom_text
    }

def scene(image, text, choices):
    return {"image": image, "text": dedent(text).strip(), "choices": choices}

def get_exploration_reaction(s):
    """Vrací jinou reakci podle fáze průzkumu."""
    count = s["promenne"].get("rozhlizeni", 0)
    if count == 0: return "North se zastavila a zapojila liščí smysly."
    if count == 1: return "Liška větří změnu v povětří."
    return "North už zná každý záhyb této pláně."

def get_exploration_text(s):
    """Dynamicky vrací text průzkumu pro polární lišku North."""
    count = s["promenne"].get("rozhlizeni", 0)
    if count == 1:
        return (
            "North se přikrčí ke sněhu. Na východě vyčnívají ostré kamenné věže, "
            "které bičuje vítr. V jedné z nich liška vycítí závětří – vchod do jeskyně."
        )
    elif count == 2:
        return (
            "Liška lehce pohne ohonem a stočí pohled na západ. Mezi mraky se rýsuje "
            "temný masiv lesa. Úzké kmeny tam stojí v takovém klidu, že se tam dá snadno zmizet."
        )
    return "Svět v mrazu se už přestal schovávat. Cesty jsou jasné."

SCENES = {
    "plan": scene(
        "plan.png",
        "Ticho. Sníh se rozprostírá do všech stran. North stojí uprostřed prázdnoty.",
        [
            choice("Prozkoumat okolí", "plan", 
                   reaction=lambda s: get_exploration_reaction(s),
                   action=lambda s: s["promenne"].update({"rozhlizeni": s["promenne"].get("rozhlizeni", 0) + 1}),
                   custom_text=lambda s: get_exploration_text(s)),
            
            choice("Vydat se ke skalám", "jeskyne", 
                   condition=lambda s: s["promenne"].get("rozhlizeni", 0) >= 1,
                   reaction="Měkkými skoky zamíříš ke skalám."),
            
            choice("Zamířit k lesu", "les", 
                   condition=lambda s: s["promenne"].get("rozhlizeni", 0) >= 2,
                   reaction="Tichým klusem se vydáváš k lesu.")
        ]
    ),
    "jeskyne": scene("cave_entrance.png", "Vchod do jeskyně zeje jako temná tlama.", [
        choice("Vrátit se na pláň", "plan")
    ]),
    "les": scene("okraj_lesa.png", "Tmavé kmeny pohlcují veškerý zvuk.", [
        choice("Vrátit se na pláň", "plan")
    ])
}