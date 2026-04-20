from textwrap import dedent


def scene(image, text, *choices):
    """Pomocná funkce pro vytvoření struktury scény."""
    return {
        "image": image,
        "text": dedent(text).strip(),
        "choices": [{"label": c[0], "target": c[1]} for c in choices]
    }


SCENES = {
    "plan": scene(
        "plan.png",
        """
        Ticho. Sníh se rozprostírá do všech stran.
        Nad plání visí těžké šedé nebe a vzduch je nehybný.

        Pak si jich všimneš. Stop ve sněhu. Nejsou tvoje.
        """,
        ("Rozhlédnout se", "plan"),
        ("Vydat se ke skalám", "jeskyne"),
        ("Zamířit k lesu", "les")
    ),

    "jeskyne": scene(
        "cave_entrance.png",
        """
        Stopy tě dovedou až ke skalám. Mezi nimi se otevírá tmavý vchod.
        Z nitra vane chlad, který se liší od mrazu venku.
        """,
        ("Vrátit se na pláň", "plan"),
        ("Vejít hlouběji", "nikol_setkani")
    ),

    "les": scene(
        "okraj_lesa.png",
        """
        Okraj lesa se z mlhy vynořuje jen pomalu.
        Úzké tmavé kmeny stojí nehybně ve sněhu a pohlcují zvuky.
        """,
        ("Vrátit se na pláň", "plan"),
        ("Vejít mezi stromy", "nikol_setkani")
    ),

    "nikol_setkani": scene(
        "setkani_s_nikol.png",
        """
        Mezi stromy sedí u vyhasínajícího ohniště postava. Žena.
        Hledí do popela. Pach je teď silnější — únava a dým.
        """,
        ("Přiblížit se", "nikol_ustup"),
        ("Zůstat v úkrytu", "plan")
    ),

    "nikol_ustup": scene(
        "setkani_s_nikol.png",
        """
        Sníh pod tlapami křupne. Žena prudce zvedne hlavu.
        Ztuhne a upřeně se na tebe dívá. Pak natáhne ruku.
        Ticho znovu ztěžkne.
        """,
        ("Zkusit to znovu", "nikol_setkani"),
        ("Ustoupit dál", "plan")
    ),

    "nikol_hrabani": scene(
        "setkani_s_nikol.png",
        """
        North začne tlapami hrabat do sněhu. Kousky ledu lítají kolem.
        Žena se zarazí a v koutcích úst se jí objeví úsměv.
        Pomalu k tobě natahuje ruku.
        """,
        ("Podejít blíž", "k1_konec")
    ),

    "k1_konec": scene(
        "trust_ch1end.png",
        """
        Už tě neodhání. North dojde až k ní.
        Nikol nic neříká, jen tě nechá cítit teplo ohně.
        První křehké pouto bylo navázáno.
        """,
        ("Konec kapitoly", "main_menu")
    )
}