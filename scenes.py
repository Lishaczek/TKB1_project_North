from textwrap import dedent

def choice(label, target, cid=None, condition=None, action=None, once=False, reaction=None, custom_text=None):
    """
    Všechny parametry zachovány:
    - cid/once: pro jednorázové akce.
    - condition: pro odemykání cest (např. po rozhlížení)[cite: 3].
    - action: pro změnu stavu (např. sebrání amuletu)[cite: 3].
    - reaction/custom_text: pro dynamické vyprávění[cite: 3].
    """
    return {
        "label": label, "target": target, "cid": cid,
        "condition": condition, "action": action, "once": once,
        "reaction": reaction, "custom_text": custom_text
    }

def scene(image, text, choices):
    """Vytvoří datovou strukturu pro scénu[cite: 3]."""
    return {"image": image, "text": dedent(text).strip(), "choices": choices}

def get_exploration_reaction(s):
    """Dynamická reakce na průzkum (zachováno)[cite: 3]."""
    count = s["promenne"].get("rozhlizeni", 0)
    if count == 0: return "North se zastavila a zapojila liščí smysly."
    if count == 1: return "Liška větří změnu v povětří."
    return "North už zná každý záhyb této pláně."

def get_exploration_text(s):
    """Dynamický text průzkumu (zachováno)[cite: 3]."""
    count = s["promenne"].get("rozhlizeni", 0)
    if count == 1:
        return (
            "North se přikrčí ke sněhu. Na východě vyčnívají ostré kamenné věže. "
            "V jedné z nich liška vycítí závětří – vchod do jeskyně."
        )
    elif count == 2:
        return (
            "Liška lehce pohne ohonem a stočí pohled na západ. Mezi mraky se rýsuje "
            "temný masiv lesa. Úzké kmeny tam stojí v hrobovém tichu."
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

    # --- JESKYNNÍ VĚTEV (Rozšířeno) ---
    "jeskyne": scene(
        "cave_entrance.png", 
        "Vchod do jeskyně zeje jako temná tlama. Z nitra vane pach starého kamene.",
        [
            choice("Vstoupit do hlubin", "jeskyne_labyrint", reaction="Tma tě obklopí jako studená deka."),
            choice("Vrátit se na pláň", "plan", reaction="Světlo venku je jistější.")
        ]
    ),
    "jeskyne_labyrint": scene(
        "cave_inside.png",
        "Chodba se větví. Slyšíš tiché kapání vody a ozvěnu vlastního dechu.",
        [
            choice("Sledovat proud vzduchu", "jeskyne_sachta", reaction="Liščí uši pátrají po sebemenším zvuku."),
            choice("Zkoumat kosti v rohu", "jeskyne_nalez", cid="bones", once=True),
            choice("Vrátit se ke vchodu", "jeskyne")
        ]
    ),
    "jeskyne_nalez": scene(
        "cave_inside.png",
        "Mezi kostmi najdeš starý amulet. North ho opatrně bere do tlamy.",
        [
            choice("Pokračovat dál", "jeskyne_labyrint", action=lambda s: s["promenne"].update({"ma_amulet": True}))
        ]
    ),
    "jeskyne_sachta": scene(
        "cave_shaft.png",
        "Do síně dopadá úzký paprsek světla z pukliny nahoře.",
        [
            choice("Vyskočit na římsu", "jeskyne_vychod", condition=lambda s: s["promenne"].get("rozhlizeni", 0) > 2),
            choice("Zůstat v bezpečí šera", "jeskyne_labyrint")
        ]
    ),
    "jeskyne_vychod": scene(
        "cave_exit.png",
        "Puklina tě vyvedla na vyvýšené místo. Odtud vidíš postavu u ohně.",
        [choice("Sestoupit k postavě", "nikol_setkani")]
    ),

    # --- LESNÍ VĚTEV (Rozšířeno) ---
    "les": scene(
        "okraj_lesa.png", 
        "První kmeny stromů jsou obalené námrazou. Les vypadá jako zkamenělá armáda.",
        [
            choice("Proniknout hlouběji", "les_stred", reaction="Sníh tu pod tlapami nekřupe tak nahlas."),
            choice("Vrátit se na pláň", "plan")
        ]
    ),
    "les_stred": scene(
        "forest_deep.png",
        "Větve nad tebou vytvářejí neprostupnou klenbu. Světlo tu má modravou barvu.",
        [
            choice("Sledovat cizí stopy", "les_stopy", reaction="Nos se dotýká studeného sněhu."),
            choice("Vylézt na padlý kmen", "les_vyhled"),
            choice("Vrátit se na okraj", "les")
        ]
    ),
    "les_stopy": scene(
        "forest_tracks.png",
        "Stopy jsou čerstvé. Patří někomu velkému. North cítí napětí v každém svalu.",
        [
            choice("Tiše sledovat", "nikol_setkani", reaction="Pohybuješ se jako duch."),
            choice("Ztratit se v podrostu", "les_stred")
        ]
    ),
    "les_vyhled": scene(
        "forest_view.png",
        "Z výšky vidíš nad vrcholky. V dálce u lesa stoupá tenký proužek kouře.",
        [
            choice("Seskočit a jít za kouřem", "nikol_setkani"),
            choice("Vrátit se do stínu", "les_stred")
        ]
    ),

    # --- SPOLEČNÝ CÍL ---
    "nikol_setkani": scene(
        "setkani_s_nikol.png", 
        "U malého ohně sedí postava. Žena. Hledí do plamenů a v mrazu bojuje o život.",
        [
            choice("Pozorovat z dálky", "plan"),
            choice("Odhalit se", "nikol_ustup", reaction="Tvé bílé tělo vystoupí ze stínů.")
        ]
    ),
    "nikol_ustup": scene(
        "setkani_s_nikol.png",
        "Žena prudce zvedne hlavu. Ztuhne a upřeně se na tebe dívá.",
        [choice("Zkusit se přiblížit", "plan")] # Tady se pak může větvit dál
    )
}