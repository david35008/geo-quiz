#!/usr/bin/env python3
"""Generate COUNTRIES array for geo-quiz.html from mledoze/countries data."""

from __future__ import annotations

import json
import re
from pathlib import Path

COUNTRIES_JSON = Path("/tmp/countries.json")

# Globally famous — household names worldwide
FAME_1 = {
    "US", "CN", "GB", "FR", "DE", "JP", "IN", "BR", "RU", "IT", "ES", "CA", "AU", "MX",
    "KR", "EG", "SA", "TR", "AR", "ZA", "NG", "IR", "IL", "PK", "UA", "NL", "SE", "CH",
    "GR", "PT", "TH", "VN", "PH", "ID", "NZ", "IE", "CO", "AE", "TW", "HK", "MY", "SG",
}

# Well-known but not top-tier global icons (~50)
FAME_2 = {
    "PL", "BE", "AT", "CU", "PE", "CL", "VE", "DK", "FI", "NO", "CZ", "HU", "RO", "BD",
    "MA", "KE", "ET", "IQ", "AF", "MM", "KH", "NP", "LK", "KZ", "RS", "HR", "BG", "SK",
    "SI", "LT", "LV", "EE", "IS", "JO", "TN", "DZ", "LY", "GH", "TZ", "UG", "ZW", "AO",
    "CM", "CI", "SN", "CR", "PA", "BO", "PY", "UY", "EC", "FJ", "PG", "UZ", "KP", "LB",
    "GT", "DO", "JM", "TT", "PR", "SD", "YE", "OM", "QA", "KW", "BH", "SY", "ML", "MN",
    "LA", "BN", "CY",
}

# Obscure / rarely recognized (~25)
FAME_4 = {
    "TV", "NR", "KI", "MH", "FM", "PW", "TO", "WS", "VU", "ST", "CV", "KM", "SC", "SS",
    "SO", "ER", "GW", "GQ", "CF", "TD", "NE", "BF", "BJ", "TG", "NU",
}

# Microstates & hardest
FAME_5 = {
    "VA", "MC", "AD", "LI", "SM", "MT", "LU",
}

PHRASES: dict[str, dict[str, str]] = {
    "eng": {"hello": "Hello", "thankYou": "Thank you", "yes": "Yes", "no": "No", "goodbye": "Goodbye"},
    "fra": {"hello": "Bonjour", "thankYou": "Merci", "yes": "Oui", "no": "Non", "goodbye": "Au revoir"},
    "spa": {"hello": "Hola", "thankYou": "Gracias", "yes": "Sí", "no": "No", "goodbye": "Adiós"},
    "deu": {"hello": "Hallo", "thankYou": "Danke", "yes": "Ja", "no": "Nein", "goodbye": "Auf Wiedersehen"},
    "ita": {"hello": "Ciao", "thankYou": "Grazie", "yes": "Sì", "no": "No", "goodbye": "Arrivederci"},
    "por": {"hello": "Olá", "thankYou": "Obrigado", "yes": "Sim", "no": "Não", "goodbye": "Adeus"},
    "rus": {"hello": "Privet", "thankYou": "Spasibo", "yes": "Da", "no": "Net", "goodbye": "Do svidaniya"},
    "zho": {"hello": "Nǐ hǎo", "thankYou": "Xièxiè", "yes": "Shì", "no": "Bù", "goodbye": "Zàijiàn"},
    "jpn": {"hello": "Konnichiwa", "thankYou": "Arigatou", "yes": "Hai", "no": "Iie", "goodbye": "Sayonara"},
    "kor": {"hello": "Annyeonghaseyo", "thankYou": "Gamsahamnida", "yes": "Ne", "no": "Aniyo", "goodbye": "Annyeonghi gaseyo"},
    "ara": {"hello": "Marhaba", "thankYou": "Shukran", "yes": "Na'am", "no": "La", "goodbye": "Ma'a salama"},
    "hin": {"hello": "Namaste", "thankYou": "Dhanyavaad", "yes": "Haan", "no": "Nahin", "goodbye": "Alvida"},
    "tur": {"hello": "Merhaba", "thankYou": "Teşekkürler", "yes": "Evet", "no": "Hayır", "goodbye": "Hoşça kal"},
    "nld": {"hello": "Hallo", "thankYou": "Dank je", "yes": "Ja", "no": "Nee", "goodbye": "Tot ziens"},
    "swe": {"hello": "Hej", "thankYou": "Tack", "yes": "Ja", "no": "Nej", "goodbye": "Hej då"},
    "nor": {"hello": "Hei", "thankYou": "Takk", "yes": "Ja", "no": "Nei", "goodbye": "Ha det"},
    "dan": {"hello": "Hej", "thankYou": "Tak", "yes": "Ja", "no": "Nej", "goodbye": "Farvel"},
    "fin": {"hello": "Hei", "thankYou": "Kiitos", "yes": "Kyllä", "no": "Ei", "goodbye": "Näkemiin"},
    "pol": {"hello": "Cześć", "thankYou": "Dziękuję", "yes": "Tak", "no": "Nie", "goodbye": "Do widzenia"},
    "ces": {"hello": "Ahoj", "thankYou": "Děkuji", "yes": "Ano", "no": "Ne", "goodbye": "Na shledanou"},
    "slk": {"hello": "Ahoj", "thankYou": "Ďakujem", "yes": "Áno", "no": "Nie", "goodbye": "Dovidenia"},
    "hun": {"hello": "Szia", "thankYou": "Köszönöm", "yes": "Igen", "no": "Nem", "goodbye": "Viszlát"},
    "ron": {"hello": "Bună", "thankYou": "Mulțumesc", "yes": "Da", "no": "Nu", "goodbye": "La revedere"},
    "bul": {"hello": "Zdravey", "thankYou": "Blagodarya", "yes": "Da", "no": "Ne", "goodbye": "Dovizhdane"},
    "hrv": {"hello": "Bok", "thankYou": "Hvala", "yes": "Da", "no": "Ne", "goodbye": "Doviđenja"},
    "srp": {"hello": "Zdravo", "thankYou": "Hvala", "yes": "Da", "no": "Ne", "goodbye": "Doviđenja"},
    "bos": {"hello": "Zdravo", "thankYou": "Hvala", "yes": "Da", "no": "Ne", "goodbye": "Doviđenja"},
    "ukr": {"hello": "Pryvit", "thankYou": "Dyakuyu", "yes": "Tak", "no": "Ni", "goodbye": "Do pobachennya"},
    "bel": {"hello": "Privet", "thankYou": "Dzyakuyu", "yes": "Tak", "no": "Ne", "goodbye": "Da pabachennya"},
    "ell": {"hello": "Yassou", "thankYou": "Efharistó", "yes": "Nai", "no": "Ochi", "goodbye": "Antío"},
    "heb": {"hello": "Shalom", "thankYou": "Toda", "yes": "Ken", "no": "Lo", "goodbye": "Lehitra'ot"},
    "tha": {"hello": "Sawatdee", "thankYou": "Khob khun", "yes": "Chai", "no": "Mai chai", "goodbye": "La gorn"},
    "vie": {"hello": "Xin chào", "thankYou": "Cảm ơn", "yes": "Vâng", "no": "Không", "goodbye": "Tạm biệt"},
    "ind": {"hello": "Halo", "thankYou": "Terima kasih", "yes": "Ya", "no": "Tidak", "goodbye": "Selamat tinggal"},
    "msa": {"hello": "Selamat pagi", "thankYou": "Terima kasih", "yes": "Ya", "no": "Tidak", "goodbye": "Selamat tinggal"},
    "fil": {"hello": "Kumusta", "thankYou": "Salamat", "yes": "Oo", "no": "Hindi", "goodbye": "Paalam"},
    "swa": {"hello": "Jambo", "thankYou": "Asante", "yes": "Ndiyo", "no": "Hapana", "goodbye": "Kwaheri"},
    "amh": {"hello": "Selam", "thankYou": "Ameseginalehu", "yes": "Aw", "no": "Aydelem", "goodbye": "Dehna hun"},
    "som": {"hello": "Salaam", "thankYou": "Mahadsanid", "yes": "Haa", "no": "Maya", "goodbye": "Nabad gelyo"},
    "afr": {"hello": "Hallo", "thankYou": "Dankie", "yes": "Ja", "no": "Nee", "goodbye": "Totsiens"},
    "zul": {"hello": "Sawubona", "thankYou": "Ngiyabonga", "yes": "Yebo", "no": "Cha", "goodbye": "Hamba kahle"},
    "xho": {"hello": "Molo", "thankYou": "Enkosi", "yes": "Ewe", "no": "Hayi", "goodbye": "Sala kakuhle"},
    "sot": {"hello": "Lumela", "thankYou": "Ke a leboha", "yes": "Ee", "no": "Tjhe", "goodbye": "Sala hantle"},
    "tsn": {"hello": "Dumela", "thankYou": "Ke a leboga", "yes": "Ee", "no": "Nnyaa", "goodbye": "Tsamaya sentle"},
    "nso": {"hello": "Thobela", "thankYou": "Ke a leboga", "yes": "Ee", "no": "Aowa", "goodbye": "Šala gabotse"},
    "nya": {"hello": "Moni", "thankYou": "Zikomo", "yes": "Inde", "no": "Ayayi", "goodbye": "Pitani bwino"},
    "sna": {"hello": "Mhoro", "thankYou": "Ndatenda", "yes": "Hongu", "no": "Kwete", "goodbye": "Sara mushe"},
    "lin": {"hello": "Mbote", "thankYou": "Matondi", "yes": "Iyo", "no": "Te", "goodbye": "Kende malamu"},
    "kon": {"hello": "Mbote", "thankYou": "Matondi", "yes": "Iyo", "no": "Te", "goodbye": "Kende malamu"},
    "run": {"hello": "Amahoro", "thankYou": "Urakoze", "yes": "Yego", "no": "Oya", "goodbye": "Murabeho"},
    "kin": {"hello": "Muraho", "thankYou": "Murakoze", "yes": "Yego", "no": "Oya", "goodbye": "Murabeho"},
    "mlg": {"hello": "Salama", "thankYou": "Misaotra", "yes": "Eny", "no": "Tsia", "goodbye": "Veloma"},
    "fas": {"hello": "Salam", "thankYou": "Merci", "yes": "Bale", "no": "Na", "goodbye": "Khoda hafez"},
    "prs": {"hello": "Salam", "thankYou": "Tashakur", "yes": "Bale", "no": "Na", "goodbye": "Khuda hafiz"},
    "pus": {"hello": "Salam", "thankYou": "Manana", "yes": "Ho", "no": "Na", "goodbye": "Khuda hafiz"},
    "urd": {"hello": "Assalam-o-alaikum", "thankYou": "Shukriya", "yes": "Haan", "no": "Nahin", "goodbye": "Khuda hafiz"},
    "ben": {"hello": "Nomoshkar", "thankYou": "Dhonnobad", "yes": "Haan", "no": "Na", "goodbye": "Biday"},
    "sin": {"hello": "Ayubowan", "thankYou": "Istuti", "yes": "Ow", "no": "Naha", "goodbye": "Gihin ennam"},
    "nep": {"hello": "Namaste", "thankYou": "Dhanyabaad", "yes": "Ho", "no": "Hoina", "goodbye": "Namaste"},
    "mya": {"hello": "Mingalaba", "thankYou": "Kyay tzu tin bar tal", "yes": "Ho", "no": "Ma ho bu", "goodbye": "Thwa bi"},
    "khm": {"hello": "Sous-dey", "thankYou": "Aw kohn", "yes": "Baat", "no": "Ot te", "goodbye": "Li hi"},
    "lao": {"hello": "Sabaidee", "thankYou": "Khob chai", "yes": "Doi", "no": "Bo", "goodbye": "La gon"},
    "mon": {"hello": "Sain baina uu", "thankYou": "Bayarlalaa", "yes": "Tiim", "no": "Ugui", "goodbye": "Bayartai"},
    "kaz": {"hello": "Salem", "thankYou": "Rakhmet", "yes": "Ia", "no": "Zhok", "goodbye": "Sau bol"},
    "uzb": {"hello": "Salom", "thankYou": "Rahmat", "yes": "Ha", "no": "Yo'q", "goodbye": "Xayr"},
    "tgk": {"hello": "Salom", "thankYou": "Rahmat", "yes": "Bale", "no": "Ne", "goodbye": "Khayr"},
    "tuk": {"hello": "Salam", "thankYou": "Sag bol", "yes": "Hawa", "no": "Yok", "goodbye": "Sag bol"},
    "aze": {"hello": "Salam", "thankYou": "Təşəkkür", "yes": "Bəli", "no": "Xeyr", "goodbye": "Sağ ol"},
    "kat": {"hello": "Gamarjoba", "thankYou": "Madloba", "yes": "Ki", "no": "Ara", "goodbye": "Nakhvamdis"},
    "hye": {"hello": "Barev", "thankYou": "Shnorhakalutyun", "yes": "Ayo", "no": "Voch", "goodbye": "C'tesutyun"},
    "sqi": {"hello": "Përshëndetje", "thankYou": "Faleminderit", "yes": "Po", "no": "Jo", "goodbye": "Mirupafshim"},
    "mkd": {"hello": "Zdravo", "thankYou": "Blagodaram", "yes": "Da", "no": "Ne", "goodbye": "Doviduvanje"},
    "slv": {"hello": "Zdravo", "thankYou": "Hvala", "yes": "Da", "no": "Ne", "goodbye": "Adijo"},
    "est": {"hello": "Tere", "thankYou": "Aitäh", "yes": "Jah", "no": "Ei", "goodbye": "Head aega"},
    "lav": {"hello": "Sveiki", "thankYou": "Paldies", "yes": "Jā", "no": "Nē", "goodbye": "Uz redzēšanos"},
    "lit": {"hello": "Labas", "thankYou": "Ačiū", "yes": "Taip", "no": "Ne", "goodbye": "Viso gero"},
    "isl": {"hello": "Halló", "thankYou": "Takk", "yes": "Já", "no": "Nei", "goodbye": "Bless"},
    "gle": {"hello": "Dia dhuit", "thankYou": "Go raibh maith agat", "yes": "Tá", "no": "Níl", "goodbye": "Slán"},
    "cym": {"hello": "Helo", "thankYou": "Diolch", "yes": "Ie", "no": "Na", "goodbye": "Hwyl"},
    "mlt": {"hello": "Bonġu", "thankYou": "Grazzi", "yes": "Iva", "no": "Le", "goodbye": "Saħħa"},
    "cat": {"hello": "Hola", "thankYou": "Gràcies", "yes": "Sí", "no": "No", "goodbye": "Adéu"},
    "glg": {"hello": "Ola", "thankYou": "Grazas", "yes": "Si", "no": "Non", "goodbye": "Adeus"},
    "eus": {"hello": "Kaixo", "thankYou": "Eskerrik asko", "yes": "Bai", "no": "Ez", "goodbye": "Agur"},
    "hat": {"hello": "Bonjou", "thankYou": "Mèsi", "yes": "Wi", "no": "Non", "goodbye": "Orevwa"},
    "pap": {"hello": "Bon dia", "thankYou": "Danki", "yes": "Si", "no": "No", "goodbye": "Ayo"},
    "tet": {"hello": "Ola", "thankYou": "Obrigadu", "yes": "Sim", "no": "Lae", "goodbye": "Até logo"},
    "smo": {"hello": "Talofa", "thankYou": "Fa'afetai", "yes": "Ioe", "no": "Leai", "goodbye": "Tōfā"},
    "fij": {"hello": "Bula", "thankYou": "Vinaka", "yes": "Io", "no": "Sega", "goodbye": "Moce"},
    "hif": {"hello": "Namaste", "thankYou": "Dhanyavaad", "yes": "Haan", "no": "Nahin", "goodbye": "Alvida"},
    "mri": {"hello": "Kia ora", "thankYou": "Thank you", "yes": "Ae", "no": "Kāo", "goodbye": "Haere rā"},
    "tpi": {"hello": "Gude", "thankYou": "Tenkyu", "yes": "Yes", "no": "Nogat", "goodbye": "Bai bai"},
    "bis": {"hello": "Halo", "thankYou": "Tangkyu", "yes": "Yes", "no": "No", "goodbye": "Gudbae"},
    "cal": {"hello": "Hafa adai", "thankYou": "Si Yu'os ma'åse'", "yes": "Hunggok", "no": "Tåya'", "goodbye": "Adios"},
    "cha": {"hello": "Håfa adai", "thankYou": "Si Yu'os ma'åse'", "yes": "Hunggok", "no": "Tåya'", "goodbye": "Adios"},
    "div": {"hello": "Assalaamu alaikum", "thankYou": "Shukuriyaa", "yes": "Aan", "no": "Noon", "goodbye": "Vakivelan"},
    "dzo": {"hello": "Kuzuzangpo", "thankYou": "Kadrin chhe", "yes": "In", "no": "Men", "goodbye": "Log jay ge"},
    "kal": {"hello": "Aluu", "thankYou": "Qujanaq", "yes": "Aap", "no": "Naaga", "goodbye": "Baaj boht"},
    "mah": {"hello": "Iokwe", "thankYou": "Kommol", "yes": "E", "no": "Jab", "goodbye": "Yokwe"},
    "nau": {"hello": "Buongiorno", "thankYou": "Regaru", "yes": "Eow", "no": "Bo", "goodbye": "Mo otemmo"},
    "niu": {"hello": "Fakaalofa", "thankYou": "Fakaaue", "yes": "E", "no": "Nai", "goodbye": "Mae logologo"},
    "pau": {"hello": "Alii", "thankYou": "Komengmokl", "yes": "Chochoi", "no": "Ng diak", "goodbye": "Mekurouro"},
    "tvl": {"hello": "Talofa", "thankYou": "Fakafetai", "yes": "Ioe", "no": "Sega", "goodbye": "Fafetai"},
    "aym": {"hello": "Kamisaraki", "thankYou": "Yuspagara", "yes": "Jïsa", "no": "Janiwa", "goodbye": "Kamisaki"},
    "que": {"hello": "Allinllachu", "thankYou": "Sulpayki", "yes": "Arí", "no": "Manam", "goodbye": "Tupananchikkama"},
    "grn": {"hello": "Mba'éichapa", "thankYou": "Aguyje", "yes": "Heẽ", "no": "Nahániri", "goodbye": "Jajoecha peve"},
    "gil": {"hello": "Mauri", "thankYou": "Ko rabu", "yes": "E", "no": "Ai nga", "goodbye": "Kam na bane"},
    "cnr": {"hello": "Zdravo", "thankYou": "Hvala", "yes": "Da", "no": "Ne", "goodbye": "Doviđenja"},
    "arc": {"hello": "Shlama", "thankYou": "Basima", "yes": "E", "no": "La", "goodbye": "Push bshak"},
    "ber": {"hello": "Azul", "thankYou": "Tanmmirt", "yes": "Ih", "no": "Uhu", "goodbye": "Ar tufat"},
    "lua": {"hello": "Mbote", "thankYou": "Matondi", "yes": "Ee", "no": "Te", "goodbye": "Kende malamu"},
    "ven": {"hello": "Ndaa", "thankYou": "Ndo livhuwa", "yes": "Ee", "no": "Hai", "goodbye": "Salani gavhuti"},
    "tso": {"hello": "Avuxeni", "thankYou": "Inkomu", "yes": "Ina", "no": "E-e", "goodbye": "Sala kahle"},
    "ssw": {"hello": "Sawubona", "thankYou": "Ngiyabonga", "yes": "Yebo", "no": "Cha", "goodbye": "Hamba kahle"},
    "nbl": {"hello": "Sawubona", "thankYou": "Ngiyabonga", "yes": "Yebo", "no": "Cha", "goodbye": "Hamba kahle"},
    "nrf": {"hello": "Bonjour", "thankYou": "Merci", "yes": "Oui", "no": "Non", "goodbye": "Au revoir"},
    "gsw": {"hello": "Grüezi", "thankYou": "Danke", "yes": "Ja", "no": "Nein", "goodbye": "Uf Wiederluege"},
    "ltz": {"hello": "Moien", "thankYou": "Merci", "yes": "Jo", "no": "Nee", "goodbye": "Äddi"},
    "bar": {"hello": "Servus", "thankYou": "Danke", "yes": "Ja", "no": "Nein", "goodbye": "Auf Wiedersehen"},
    "cnr": {"hello": "Zdravo", "thankYou": "Hvala", "yes": "Da", "no": "Ne", "goodbye": "Doviđenja"},
}

LANG_FALLBACK: dict[str, str] = {
    "aym": "spa", "que": "spa", "grn": "spa", "cat": "spa", "glg": "spa",
    "cnr": "srp", "bos": "srp", "mkd": "srp", "bar": "deu", "gsw": "deu",
    "ltz": "fra", "nrf": "fra", "pap": "nld", "hif": "hin", "ber": "ara",
    "arc": "ara", "lua": "fra", "ven": "tsn", "tso": "tsn", "ssw": "zul",
    "nbl": "zul", "cal": "eng", "cha": "eng", "niu": "eng", "tvl": "smo",
    "gil": "eng", "bis": "eng", "tpi": "eng", "mah": "eng", "nau": "eng",
}


def js_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def fame_tier(code: str, region: str | None, area: float | None) -> int:
    if code in FAME_5:
        return 5
    if code in FAME_1:
        return 1
    if code in FAME_2:
        return 2
    if code in FAME_4:
        return 4
    if area is not None and area < 300:
        return 5
    if region == "Oceania" and area is not None and area < 20000:
        return 4
    return 3


def pick_language(languages: dict[str, str] | None) -> str:
    if not languages:
        return "eng"
    keys = sorted(languages.keys())
    for preferred in ("eng", "fra", "spa", "por", "deu", "ara", "zho", "rus"):
        if preferred in languages:
            return preferred
    return keys[0]


def words_for_lang(lang: str) -> dict[str, str]:
    if lang in PHRASES:
        return PHRASES[lang]
    fallback = LANG_FALLBACK.get(lang)
    if fallback and fallback in PHRASES:
        return PHRASES[fallback]
    return PHRASES["eng"]


def main() -> None:
    data = json.loads(COUNTRIES_JSON.read_text())
    entries: list[dict] = []

    for country in sorted(data, key=lambda c: c["name"]["common"]):
        if not country.get("independent"):
            continue
        capital = country.get("capital")
        if not capital:
            continue
        code = country["cca2"]
        name = country["name"]["common"]
        capital_name = capital[0] if isinstance(capital, list) else capital
        lang = pick_language(country.get("languages"))
        words = words_for_lang(lang)
        difficulty = fame_tier(code, country.get("region"), country.get("area"))
        entries.append({
            "code": code,
            "name": name,
            "capital": capital_name,
            "difficulty": difficulty,
            "words": words,
        })

    tiers = {i: 0 for i in range(1, 6)}
    for e in entries:
        tiers[e["difficulty"]] += 1

    lines = ["  const COUNTRIES = ["]
    for entry in entries:
        w = entry["words"]
        lines.append(
            "    {{ code: {code}, name: {name}, capital: {capital}, difficulty: {diff}, "
            "words: {{ hello: {hello}, thankYou: {ty}, yes: {yes}, no: {no}, goodbye: {bye} }} }},".format(
                code=js_str(entry["code"]),
                name=js_str(entry["name"]),
                capital=js_str(entry["capital"]),
                diff=entry["difficulty"],
                hello=js_str(w["hello"]),
                ty=js_str(w["thankYou"]),
                yes=js_str(w["yes"]),
                no=js_str(w["no"]),
                bye=js_str(w["goodbye"]),
            )
        )
    lines.append("  ];")

    output = "\n".join(lines)
    Path("/tmp/countries_generated.js").write_text(output, encoding="utf-8")
    print(f"Generated {len(entries)} countries")
    print("Tiers:", tiers)
    print("Output size:", len(output), "bytes")


if __name__ == "__main__":
    main()
