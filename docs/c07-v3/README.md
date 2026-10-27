# C-07 Design Review v3 — A valittu jatkokehityksen suunnaksi

Kaksi erillistä muotoiluvaihtoehtoa PR #13:n katselmoinnin pohjalta. **27.10.2026 käyttäjä valitsi A:n vain jatkosuunnittelun pohjaksi. A ei ole valmis eikä hyväksytty pelialus.** B säilyy vertailumallina ja mahdollisena myöhempänä erikoisaluksena. Nykyinen C-07, commit `764452a583c9c61a38ef8b229925247ad61aa2e6`, säilyy muuttumattomana tuotantomallipaikassaan. Uudet vaihtoehdot ovat erillisessä `design-review/c07-v3`-hakemistossa, eivät pelissä.

## Muotoiluerot

**A — kompakti teollinen kuriiri.** Keskitetty, selkeästi erottuva ohjaamo; matalat irrotettavat rahtimoduulit rungon molemmin puolin; näkyvä pitkittäinen kuormarunko ja levenevä kaksimoottorinen perä. Painotus on helposti luettavassa työaluksessa ja loogisissa pääosissa. Ohjaamo, rahti ja voimalaitteisto eivät enää ole saman suorakulmaisen kuoren sisällä.

**B — epäsymmetrinen huolto- ja rahtikuriiri.** Ohjaamo ja rahti vasemmalla, pitkä huolto-/voimalaiterunko oikealla. Yksi suuri ja yksi lyhyempi rahtimoduuli; erikokoiset, pituussuunnassa porrastetut moottorit; poikittaiset kuormarakenteet ja taitettu huoltopuomi. Painotus on erottuvassa siluetissa. Valinnan jälkeen etenkin massakeskiö ja työntövoiman tasapainotus vaativat suunnittelua — niitä ei ole tässä simuloitu.

Molemmat aloitettiin **samasta nykyisestä muokattavasta Blender-lähteestä**. Ohjaamo, etupainekuoren rajattu osa, kaksi rahtikasettia ja moottorikomponentit säilytettiin ja muotoiltiin uudelleen. Uudet kuormarungot muuttavat päämassoittelua. Referenssin ohjaamo–rahti–koneisto-jaottelu, tumma lasitus ja kaksimoottorinen kuriiritarkoitus säilyvät. B ottaa tarkoituksellisesti enemmän vapautta referenssin symmetriasta.

Materiaalit ovat **pelkistettyjä muotoilumateriaaleja**: ei uusia tuotantotekstuureja, kulumapassia tai mikroyksityiskohtien lisäyskierrosta. Aiemman lähteen joitakin moottoriyksityiskohtia on mukana. Nykyisessä vertailumallissa sen aiemmat tekstuurit ovat ennallaan; pintaviimeistelyn tasot eivät siten ole vertailukelpoisia. Päätös koskee muotoa ja pääosien sijoittelua.

## Oikeat Godot-kuvat — sama mittakaava ja kamera

Jokainen kuva on oikean GLB-geometrian **Godot 4.7.2 Compatibility** -viewport-tallenne, 1440 × 1000 pikseliä. Ei konseptikuvan projisointia, kuvagenerointia, Blender-renderiä tai retusointia. Kaikille kolmelle käytetään samaa kiinteää 13 × 9 × 31 metrin rajauslaatikkoa, kameran suuntia ja valoja. Yksittäistä mallia ei zoomata suuremmaksi.

| Nykyinen C-07 | A | B |
| --- | --- | --- |
| ![Nykyinen 3/4](baseline/studio/three-quarter.png) | ![A 3/4](A/studio/three-quarter.png) | ![B 3/4](B/studio/three-quarter.png) |
| ![Nykyinen takaviisto](baseline/studio/rear-quarter.png) | ![A takaviisto](A/studio/rear-quarter.png) | ![B takaviisto](B/studio/rear-quarter.png) |
| ![Nykyinen edestä](baseline/studio/front.png) | ![A edestä](A/studio/front.png) | ![B edestä](B/studio/front.png) |
| ![Nykyinen sivulta](baseline/studio/side.png) | ![A sivulta](A/studio/side.png) | ![B sivulta](B/studio/side.png) |
| ![Nykyinen ylhäältä](baseline/studio/top.png) | ![A ylhäältä](A/studio/top.png) | ![B ylhäältä](B/studio/top.png) |
| ![Nykyinen takaa](baseline/studio/rear.png) | ![A takaa](A/studio/rear.png) | ![B takaa](B/studio/rear.png) |

## Sama vertailu pelin omilla valoilla

Tässä tilassa studiovalot ja studioheijastus poistetaan. Kuvaaja kutsuu olemassa olevaa **`main.gd::_build_lights()`-funktiota** irrallaan pelin käynnistyksestä. Pelilogiikkaa tai tallennusta ei ajeta; itse pelin valoja ei muokata.

| Nykyinen C-07 | A | B |
| --- | --- | --- |
| ![Nykyinen pelivalossa](baseline/game/three-quarter.png) | ![A pelivalossa](A/game/three-quarter.png) | ![B pelivalossa](B/game/three-quarter.png) |
| ![Nykyinen perä pelivalossa](baseline/game/rear-quarter.png) | ![A perä pelivalossa](A/game/rear-quarter.png) | ![B perä pelivalossa](B/game/rear-quarter.png) |

## Lähteet ja mittarit

| Tieto | Nykyinen | A | B |
| --- | ---: | ---: | ---: |
| Pituus × leveys × korkeus (m) | 29,86 × 12,043 × 7,96 | 29,86 × 11,44 × 7,875 | 29,86 × 11,505 × 7,875 |
| Kolmiot, LOD0 | 87 572 | 23 024 | 22 992 |
| Runtime-surfacet | 13 | 13 | 13 |
| Materiaalit | 1 | 7 | 7 |
| Tekstuurikartat | 4 | 0 | 0 |

Pienempi kolmiomäärä ei todista parempaa Android-suorituskykyä: materiaalien määrä, varjot, LOD ja muu näkymä vaikuttavat myös. Kuvakohtaiset rendererin draw call / primitive -laskurit ovat kunkin hakemiston `metrics.json`:ssa, eivät puhelimen FPS-tuloksia.

- **A:** [Blender-lähde](../../native-prototype/art/c07-v3/source/c07_option_a.blend), [GLB](../../native-prototype/design-review/c07-v3/c07_option_a.glb).
- **B:** [Blender-lähde](../../native-prototype/art/c07-v3/source/c07_option_b.blend), [GLB](../../native-prototype/design-review/c07-v3/c07_option_b.glb).
- [Muuttumaton nykyinen lähde](../../native-prototype/art/c07/source/c07_courier.blend), [nykyinen GLB](../../native-prototype/production/models/c07_courier.glb).
- [Alkuperä, lähdeobjektit, tarkisteet ja valintaportit](../../native-prototype/design-review/c07-v3/manifest.json).
- [Toistamisohjeet](../../native-prototype/art/c07-v3/README.md), [testit ja kuvien tarkisteet](validation.json).

## Todennus ja avoimet rajat

**Paikalliset tulokset:** Python 17 PASS / 0 FAIL / 0 SKIP; Node 9 PASS / 0 FAIL / 0 SKIP. Molemmat Blender-lähteet, Godot-tuonti, kaikkien kolmen mallin studio-/pelivalon tarkistukset ja olemassa olevat preview-, docking- ja hero-smoke-testit PASS. Kaikki 24 kuvaa tuotettiin onnistuneesti. GitHubin tämän haaran CI:tä ei ole varmennettu.

Tekniset testit tarkistavat lähdetiedostojen uudelleenavauksen, säilyneen lähdeyhteyden, oikeat GLB-meshit, metrimittakaavan, materiaalit, kamerarajauksen ja nykyisen mallin tavutarkan säilymisen. Godot tarkistaa myös todellisista vertexeistä, että A:n ohjaamo ja moottoripari ovat keskitetyt, kun taas B:n ohjaamo on sivussa ja moottorit pituussuunnassa porrastetut. Tätä eroa ei päätellä vain tiedostonimistä.

Kehityksen aikana lähdetesti pysähtyi tarpeettomiin perittyihin tekstuurimateriaaleihin; ne poistettiin lähteistä. Ensimmäiset renderit paljastivat lisäksi yläikkunan runkoleikkauksen, laskutukien puuttuvat liitokset ja huoltopuomin liian ulkona olevan juuren. Geometria korjattiin ja lopulliset kuvat otettiin korjatuista GLB-tiedostoista. Materiaalien sRGB-värit muunnettiin lineaarisiksi shader-arvoiksi; valaistus pysyi yhteisenä kaikille.

Nämä ovat päämuotoilun vaihtoehtoja. Sisustusta, rahtimekaniikkaa, massakeskiötä, työntövoiman tasapainoa, törmäysgeometriaa tai Android-frame-timea ei ole varmennettu. Lopullinen teksturointi ja tekninen detaljointi alkavat vasta valinnan jälkeen. Kaikki paikalliset kuvat ovat desktop/Mesa-ohjelmistorenderöintejä; eivät Android- tai Mobile-renderöijän hyväksyntää.

**Käyttäjän päätös 27.10.2026: A suunnittelupohjaksi, ei julkaisu-/pelimallihyväksyntää.** `selected_option=A`, `review_status=selected_for_design`, `release_approved=false` ja `can_integrate=false`. Valintatieto on dokumentoitu tiedostossa `native-prototype/design-review/c07-v3/selection.json`, ja seuraavan kierroksen ohjeet ovat tiedostossa `docs/c07-v4/C07-A-DESIGN-BRIEF.md`. Ei mergeä, julkaisua, gameplay-integraatiota tai asemamallinnusta.
