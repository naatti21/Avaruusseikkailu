# C-07 A v4 — Issue #15:n tarkastettava mallikandidaatti

**A on valittu muotoilusuunta, ei hyväksytty pelimalli.** Tämä ehdotus jatkaa PR #14:n lähdettä ja [lukittua briiffiä](C07-A-DESIGN-BRIEF.md). A v3, B ja alkuperäinen tuotantomalli ovat tavutarkasti ennallaan. Uusi malli on erillisessä `design-review/c07-v4`-hakemistossa, ei pelissä. Käyttäjän visuaalinen päätös tarvitaan ennen seuraavaa vaihetta.

## Päämuodon ja rakenteen muutokset

- **Ohjaamo:** korkean tasaisen etulasin tilalla kapeneva sensorinokka ja painekuoren taitetta seuraava viisto kattolasitus. Keskitetty miehistötila liittyy takana huoltokaulaan; suljettu telakointiluukku ja rengas ovat selkäpuolella. Lasituksen ja varsinaisen kuoren välys tarkistetaan Blenderin geometriasta.
- **Rahti:** kaksi erillistä paineistamatonta moduulia, viistetyt päädyt, suojakehykset, nostolenkit, sivuluukut ja erikokoiset ylähuoltokannet. Rungon ja moduulin välissä näkyy välys ja neljä lukituskohtaa. Lukitustappien yhteys runko- ja moduulivastakkeisiin tarkistetaan todellisista mesh-rajoista. Mekanismia ei ole animoitu tai kuormitustestattu.
- **Runko:** A:n köli, moottorikehdot ja laskutuet jatkuvat mukana. Kaksi pitkittäistä työntöpalkkia, poikkipalkit ja vinotuet muodostavat luettavan kuormareitin. Peittävä suuri peräkotelo korvattiin pienemmällä koneistorungolla, jolloin huoltoalue ja tankit erottuvat.
- **Moottorit:** A:n kaksimoottorisuus säilyy. Lisätty kiinnitysrenkaat, huoltoluukut, säiliöt, suojatut syöttölinjat, saranoidut jäähdytyspinnat ja asennonsäätösuutinten ryhmät. Suuttimet esitetään lepotilassa tummina lämpösuojattuina rakenteina, eivät suurina hohtavina putkina.
- **Materiaalit:** yksi 1024² PBR-atlasjoukko, neljä karttaa. Työ- ja navigointilinssit ovat hillittyjä emissiivisiä materiaaleja; rungon materiaali ei hohda eikä pelin päävaloa ole kirkastettu. UV-kartoitus käyttää jaettuja pinta-alueita, ei vielä yksilöllistä tuotantotason kuluma- tai tekstitarra-atlasta.

## Samat kuusi Godot-kamerakulmaa

Kaikki kuvat ovat oikean GLB:n Godot 4.7.2 Compatibility -viewport-tallenteita, 1440 × 1000. Sama 13 × 9 × 31 metrin rajauslaatikko, kameran suunta, projektio ja valaistus kummallekin. Ei retusointia tai konseptikuvan projisointia.

| A v3 | A v4 -ehdotus |
| --- | --- |
| ![A3 3/4](A3/studio/three-quarter.png) | ![A4 3/4](A4/studio/three-quarter.png) |
| ![A3 sivu](A3/studio/side.png) | ![A4 sivu](A4/studio/side.png) |
| ![A3 ylä](A3/studio/top.png) | ![A4 ylä](A4/studio/top.png) |
| ![A3 edestä](A3/studio/front.png) | ![A4 edestä](A4/studio/front.png) |
| ![A3 takaa](A3/studio/rear.png) | ![A4 takaa](A4/studio/rear.png) |
| ![A3 takaviisto](A3/studio/rear-quarter.png) | ![A4 takaviisto](A4/studio/rear-quarter.png) |

## Pelin todellinen valaistus

Kuvaaja kutsuu samaa `main.gd::_build_lights()`-funktiota irrallisessa tarkistusnäkymässä, ilman studiolisävaloja tai pelilogiikan käynnistämistä. Varjopuolen moottorit ja keskirunko jäävät edelleen tummiksi. Tämä on näkyvä jatkoarvioinnin kohta, ei piilotettu valotuksen muutoksella. Emissiiviset työvalolinssit eivät tässä renderöijässä valaise viereistä geometriaa.

| A v3 | A v4 -ehdotus |
| --- | --- |
| ![A3 pelivalo](A3/game/three-quarter.png) | ![A4 pelivalo](A4/game/three-quarter.png) |
| ![A3 pelivalo takaa](A3/game/rear-quarter.png) | ![A4 pelivalo takaa](A4/game/rear-quarter.png) |

## Samoista kohdista otetut lähikuvat

Lähikuvien kamerat ja kohdepisteet ovat kummallekin mallille samat; muu alus rajautuu tarkoituksella kuvan ulkopuolelle.

| Kohde / A v3 | A v4 -ehdotus |
| --- | --- |
| ![Ohjaamo A3](A3/closeups/cockpit.png) | ![Ohjaamo A4](A4/closeups/cockpit.png) |
| ![Rahtikiinnitys A3](A3/closeups/cargo-locks.png) | ![Rahtikiinnitys A4](A4/closeups/cargo-locks.png) |
| ![Moottorikoneisto A3](A3/closeups/propulsion.png) | ![Moottorikoneisto A4](A4/closeups/propulsion.png) |

## Lähteet, mittarit ja toistettavuus

| Mittari | A v3 | A v4 |
| --- | ---: | ---: |
| Pituus × leveys × korkeus, m | 29,86 × 11,44 × 7,875 | 29,55 × 11,60 × 7,41 |
| LOD0-kolmiot | 23 024 | 48 952 |
| GLB-surfacet | 13 | 9 |
| Materiaalit | 7 | 1 |
| Tekstuurikartat | 0 | 4 × 1024² |
| Mitatut draw callit, studiokuvat | 26 | 18 |
| Mitatut draw callit, pelivalokuvat | 13 | 9 |

Kolmiomäärä kasvoi toiminnallisen geometrian vuoksi, mutta materiaalit ja erilliset piirrettävät pinnat vähenivät. Godot tuottaa tuonnissa LODit. Tämä ei todista parempaa Android-suorituskykyä; kuvakohtaiset draw call / primitive -lukemat ovat `metrics.json`-tiedostoissa ja sisältävät renderöintipassit.

- [Muokattava Blender-lähde](../../native-prototype/art/c07-v4/source/c07_a_v4.blend)
- [Godotissa kuvattu GLB](../../native-prototype/design-review/c07-v4/c07_a_v4.glb)
- [SHA-256, lähtöcommit, säilytetyt komponentit ja suljetut hyväksyntäportit](../../native-prototype/design-review/c07-v4/manifest.json)
- [Mallinnusresepti, alkuperä ja toistamisohje](../../native-prototype/art/c07-v4/README.md)
- [A v3:n, B:n ja tuotantomallin suojatut tarkisteet](../../native-prototype/art/c07-v4/preserved-assets.json)
- [Suoritusten tulokset ja kuvien tarkisteet](validation.json)

Geometria ja atlas ovat omia projektikontribuutioita, lähtönä valittu muokattava A-malli. Ei ulkoisia mallipaketteja, tekstuurikirjastoja tai jaettuja referenssikuvia. ORM-kartan AO on maltillinen saumavarjostus, **ei geometrinen AO-bake**. Lisenssiltään tuntemattomia ulkoisia resursseja ei tuotu mukaan; konseptireferenssille ei oleteta uudelleenjakeluoikeutta.

## Todelliset testit ja rajoitteet

Lopulliset paikalliset tulokset: **Python 24 PASS / 0 FAIL / 0 SKIP**, **Node 9 PASS / 0 FAIL / 0 SKIP**, staattiset tarkistukset PASS. Blender-lähteen uudelleenavaus, lähdeyhteys, atlas/UV, lasituksen välys ja lukkotappien yhteys PASS. Godot-tuonti, A v3/B/tuotantomallin tarkistukset sekä olemassa olevat production-preview-, C-07-, docking- ja hero-smoke-testit PASS. **22 uutta oikeaa Godot-kuvaa** tuotettu ja sidottu kuvattujen GLB-tiedostojen tarkisteisiin.

Kehityksen ensimmäisissä kuvissa lasitus leikkasi painekuorta ja peräkotelo peitti koneistoa. Korjattiin lasipinnan geometria sekä perärunko. Erilaiset UV-kerrosten nimet saivat eräät yhdistetyt paneelit käyttämään väärää atlasaluetta; kerrokset yhtenäistettiin ja lähdetesti lisättiin. Nämä löydettiin renderöinneistä, vaikka ensimmäiset tekniset testit olivat vihreät. Vanhoja testejä tai niiden rajoja ei muutettu.

**Ei vielä todennettu:** käyttäjän visuaalinen hyväksyntä, GitHub CI:n suoritus, Android Mobile/Compatibility FPS ja lämpeneminen, sisätilat, törmäysmalli, moduulien irrotusliikkeet ja välykset, todellinen massakeskiö, työntövoima-, lämpö- tai painekuormitus. Erityisesti varjopuolen luettavuus pelivalaistuksessa ja jäljellä olevien suurten panelointipintojen viimeistely ovat näkyviä rajoitteita. Paikalliset kuvat ovat Mesa-ohjelmistorenderöintejä, eivät laitetesti.

**Seuraava päätös:** käyttäjän visuaalinen arvio A v4:stä suhteessa A v3:een. `owner_visual_approval`, `production_asset_approved`, `release_approved` ja `can_integrate` ovat kaikki `false`. Ei gameplay-integraatiota, asema-/telakkamallinnusta, mergeä tai julkaisua.
