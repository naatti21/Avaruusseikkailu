# Avaruusseikkailu · Android 3D docking test v0.3

Tämä on erillinen **Androidilla asennettava Godot 4.7.2 -koe**, ei vanhan selainpelin korjaus eikä vielä kokonainen peli.

### Mitä testataan
- **Todellisempi mittakaava:** noin 30 m rahtialus, noin 900 m suuraseman ulkorengas ja noin 180 m outpost.
- **Elokuvallinen perspektiivilähestyminen:** suuri asema kasvaa näkyviin; lyhyt siirtymä, jonka voi ohittaa.
- **Hallinnosta ja asemasta riippuva telakointi:** suur-aseman skannaus tai jäähdytys; outpostin jonotus tai kuluttava ulkotelakointi.
- **Lastityyppi:** laillinen tai rekisteröimätön tutkimusnäyte; vaikutus suur-aseman tulliin.
- Kokeen ajan säilyvät krediitit, jäähdyte, runko, lämpö ja peliaika.

### Asentaminen
GitHub Actions > Godot native 3D Android test > onnistunut uusin työajo > Artifacts > ladattava ZIP ja sen sisältämä APK. Testi käyttää vain ARM64-debugallekirjoitusta ja on erillinen vanhasta navigaatiokokeilusta.

### Koe näin
1. Valitse SUURASEMA. Katso, muuttuuko mittakaava matkalla. Kokeile toisella kierroksella OHITA LÄHESTYMINEN.
2. Suorita avoin skannaus laillisella lastilla. Valitse seuraavalla kierroksella rekisteröimätön lasti ja vertaa.
3. Kokeile jäähdytettyä sisääntuloa ja seuraa jäähdytteen ja lämmön muutosta.
4. Avaa OUTPOST. Valitse turvallinen odotus tai nopea ulkotelakointi ja vertaa runkokuntoa.
5. Arvioi: onko kaksi päätöstä mielekästä, vai pitäisikö tavalliset telakoinnit automatisoida ja näyttää vain poikkeamat?

### Rajat
Ei onlinea, ei varsinaisia kauppatehtäviä, ei laajaa tähtijärjestelmää, ei fysiikkaan perustuvaa 6DoF-ohjausta, ei vielä Android-laitetesteissä hyväksyttyä käyttöliittymää. Päätösten numerot ovat testiparametreja, eivät lopullisen pelin tasapainoa. Suhdeluku säilyy paikallisessa 3D-tilassa; tähtijärjestelmien etäisyyksiä ei renderöidä suoraan.

Määrittely ja hyväksymisportti: docs/DOCKING-PROCEDURES-v0.1.md.

### Julkaisuportti
Vain erillinen testikehityshaara. GitHubin vanha Pages-versio ja main pidetään ennallaan; ei mergeä tai myyntijulkaisua ilman käyttäjän GO:ta.

### Erillinen Hero Station v0.2 -vertailu

6 km siirtokunta ja noin 30 m kuriiri ovat erillisessä benchmark-skenessä;
tämä Docking 0.3 -oletusprojekti säilyy ennallaan. [V0.2-raportti ja testirajat](../docs/HERO-STATION-v0.2.md).
