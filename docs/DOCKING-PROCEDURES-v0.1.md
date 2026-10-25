# Avaruusseikkailu – osallistava telakointi, 0.3 suunnittelu- ja testiversio

2026-10-25 · Android/Godot 4.7.2 · erillinen kehityshaara

## Käyttäjän havainto ja tavoite

Edellinen Godot-koe todisti APK-prosessin ja 3D-pisteiden välillä liikkumisen mutta ei pelattavuutta. Alus liikkui vain muutaman sentin ruudulla, asema oli liian pieni ja telakointi oli käytännössä yksi automaattinen toiminto. Päätavoite on luoda **avaruuden mittakaava ilman tylsää matkustusaikaa** sekä selvästi eri tuntuiset telakoinnit hallinnon ja aseman mukaan.

## Koe 0.3: toiminnallinen rajaus

- **Suur-asema:** noin 900 m ulkorengas (90 maailman yksikköä); pieni testirahtialus noin 30 m. Valvottu yhtiösektori.
- **Outpost:** noin 180 m leveä (18 yksikköä), kevyempi infrastruktuuri.
- Etäisyydet ja 3D-objektit ovat oikeassa suhteessa paikallisesti (koeyksikkö 10 m). Valtavaa tähtijärjestelmää ei renderöidä yhdessä koordinaatistossa.
- Kameralla on selvä perspektiivi ja iso asema *kasvaa* näkyvästi 4,5 sekunnin lyhennetyssä lähestymisessä. Pelaaja voi ohittaa animaation heti.
- Molemmissa on telakointia edeltävä tilannepäätös. Ei muistettavaa monivaiheista checklistiä, ei taistelua, ei joystickia.
- Kaksi kokeiltavaa lastia: laillinen/rekisteröimätön tutkimusnäyte. Tämän demon tulokset ovat deterministisiä, eivät ole väite tulevan pelin lopullisesta salakuljetustasapainosta.
- Resurssit ovat vain kokeen sisäisiä: 300 cr, 2 jäähdytettä, runko 100 %, lämpö 0, peliaika 0.
- **Ei palvelinta eikä käyttäjätiliä; testi nollautuu sovelluksen sulkemisesta.**

## Hallinto määrää säännöt

| Konteksti | Vaihtoehto | Pelillinen vaikutus |
|---|---|---|
| Suurasema, yhtiövalvonta | Avoin skannaus | +2 aikaa. Laillinen lasti läpi; rekisteröimätön lasti takavarikoidaan, −90 cr |
| Suurasema, yhtiövalvonta | Jäähdytetty lähestyminen | −1 jäähdyte, +1 aika ja +1 lämpö. Rekisteröimätön näyte menee ohi skannauksen |
| Pieni outpost, vanha ulkolaituri | Odota laituria | +2 aikaa, ei vauriota |
| Pieni outpost | Nopea ulkotelakointi | +0 aikaa, −8 runko, −20 cr |

Kaikki kustannukset kerrotaan pelaajalle **ennen valintaa**. Jäähdytys tai nopea telakointi ei ole käytettävissä, kun resurssi ei riitä. Suuraseman skannaus ei automaattisesti vaadi kilpien sammuttamista; jäähdytystila toteuttaa lyhyen, tilanteeseen liittyvän poikkeuksen.

Kokeessa päätökset ovat varmoja ja opittavia. Myöhemmässä pelissä lisätään eritelty, näkyvä riskitaso vain jos se tuottaa aidosti parempia valintoja. Ei piilorangaistuksia eikä joka aseman identtistä menettelyä.

## Ruudun kulku

1. Aseman valinta: “Suurasema / Outpost”; valinnainen lastityypin vaihto.
2. Lyhyt, oikea 3D-perspektiivilähestyminen, jossa alus pysyy pienenä suhteessa kohteeseen. Ohitus käytettävissä.
3. Tilannekortti: aseman hallinto / paikallinen rajoite; kaksi mahdollista toimintatapaa.
4. Valittu toimenpide ja sen tulos: aika, kreditit, jäähdyte, runko ja lämpö päivittyvät. Pelaaja näkee miksi.
5. Kokeile uudelleen toisessa asemassa; resurssit seuraavat testikertojen yli, joten päätöksillä on vaikutusta.

## Hyväksymiskriteerit

- Godot-kohtaus latautuu ja Android ARM64 debug-APK rakentuu vihreäksi GitHubissa.
- Skaalasuhde on eksplisiittinen: testialus 3 yksikköä, rengas 90 yksikköä, outpost noin 18 yksikköä.
- 3D-suur-asema on eri kokoluokkaa ja kuva kasvaa lähestymisen aikana. Puhelimen oikea visuaalinen havainto on erikseen arvioitava (NOT RUN).
- Suuraseman laillisen ja rekisteröimättömän lastin skannaukset tuottavat eri tulokset.
- Outpostin nopea telakointi säästää aikaa mutta maksaa runkokuntoa ja krediittejä.
- Turhat joystick-, nappipainallus- ja lentelyrutiinit puuttuvat. Animaatio voidaan ohittaa.
- Testin tila- ja resurssilaskenta on automaattisesti toistettavissa (headless smoke).
- Käyttökelpoisuus, ruudun tekstikoko, ohitusnapin peukalokäyttö ja graafinen mittakaavatunne testataan käyttäjän Android-puhelimessa.

## Seuraava testin jälkeinen päätös

Jos lähestymisen mittakaava toimii mutta päätösvaihe tuntuu pop-up-viidakolta, päätöksiä harvennetaan ja erotellaan poikkeamiin. Normaali laillinen telakointi on myöhemmin usein avustettu ja lyhyt. Salakuljetuksessa ja poikkeustilanteissa menetelmiä aktivoidaan enemmän.

Koe **ei vielä ole valmis mobiilipeli** eikä osoita, että kaikkien telakointien pitäisi vaatia päätöstä. Sen tehtävä on testata näitä kahta asiaa erikseen: avaruuden visuaalinen mittakaava ja menettelyjen mielekkyys.
