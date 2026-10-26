# C-07 — ensimmäinen arvioitava 3D-mallikandidaatti / issue #12

**Tila: visuaalista hyväksyntää odottava ehdokas. Ei julkaisuvalmis.** Pohja on PR #11, commit `6f8f95ce47527ffca76d1f911f3d4c880feef2e5`. Kehityshaara: `feature/issue12-c07-art-pilot`. Telakkaa tai Twin Cylinder -asemaa ei ole tässä vaiheessa mallinnettu.

Käyttäjän toimittaman ZIP-paketin C-07-referenssi luettiin ennen mallinnusta. Alus on uusi Blender-malli, ei aiemman courier-prototyypin päivitys. Viistetty painekuori, tummat ohjaamoikkunat, vaaleat irrotettavat suojakehät, oranssit rahtikasetit ja kaksimoottorinen perä tulkitsevat konseptia. Konseptin kuvakulmia ei ole käsitelty keskenään täsmällisinä CAD-projektioina.

## Oikeasta GLB:stä otetut Godot-kuvat

Kaikki kuusi kuvaa ovat saman tuotanto-GLB:n **Godot 4.7.2 Compatibility** -renderöintejä. Kuvausskripti käyttää PR #11:n mallipaikkaa ja tarkastusnäkymää, pysäyttää kierron ja asettaa mittoihin sovitetut kamerat. Kuvat ovat 1440 × 1000 pikseliä. Ei kuvageneraattoria, Blender-renderiä, konseptin päälle liimattua mallia tai kuvankäsittelyä. Studion ympäristöheijastus, avain-/täytevalo ja varjot kuuluvat vain katselmointiasetelmaan.

![C-07 edestä viistosti, Godot](three-quarter.png)
![C-07 takaa viistosti, Godot](rear-quarter.png)

| Etu | Taka |
| --- | --- |
| ![Edestä](front.png) | ![Takaa](rear.png) |

![Sivulta](side.png)
![Ylhäältä](top.png)

## Toimitus ja budjetti

- [Blender-lähde](../../native-prototype/art/c07/source/c07_courier.blend): 547 erillistä muokattavaa mesh-objektia, pakatut tekstuurit ja tarkastuskamerat.
- [GLB](../../native-prototype/production/models/c07_courier.glb): 13 rakenneosaa / surfacea, yksi jaettu PBR-materiaali, 84 744 kolmiota LOD0:ssa.
- Godotissa vertexeistä mitattu koko: **29,86 m pitkä × 12,036 m leveä × 7,96 m korkea**, importin skaala 1.
- Neljä 1024² karttaa: base color, metallic/roughness, tangent normal ja emissive. GLB noin 8,7 MiB. Godot käyttää upotettua Basis Universal -tuontia ja automaattisia mesh-LOD:eja. GPU-muistia tai Android-nopeutta ei ole mitattu.
- Geometriaan kuuluvat suojalevyjen oikeat tarkastusaukot, säteittäiset kiinnitystuet, syvät suuttimet, putkisto, jäähdyttimet, lastin kiinnikkeet, huoltokannet, docking-kiinnitys ja sisäänvedetyt tuet.
- [Alkuperä ja SHA-256](../../native-prototype/production/asset_manifest.json), [rakennusmittarit](../../native-prototype/art/c07/build_metrics.json), [Godot-mittarit](godot-metrics.json), [testinäyttö ja kuvien tarkisteet](validation.json).
- [Työkalut, toistaminen ja lähdeohje](../../native-prototype/art/c07/README.md).

## Todelliset testitulokset

| Tarkistus | Tulos |
| --- | --- |
| Python: vanha art contract + C-07:n riippumattomat GLB-/lähdetestit | 11 PASS, 0 FAIL, 0 SKIP |
| Node: olemassa oleva selainpelin logiikka | 9 PASS, 0 FAIL, 0 SKIP |
| Staattiset tiedostot ja manifesti | PASS |
| Blender 4.3.2: toimitetun `.blend`-tiedoston uudelleenavaus, rakenneosat, UV:t, materiaalikytkentöjen pakatut kartat, mittakaava | PASS |
| Godot 4.7.2: puhdas import erillisessä hakemistossa ilman aiempaa import-välimuistia | PASS |
| C-07:n aidon importin mitat, UV/normaalit, kaikki PBR-kytkennät, skaala, geometria-/materiaalibudjetti, kuvakulmien rajaus ja hyväksyntäportit | PASS |
| PR #11:n alkuperäinen preview smoke | PASS |
| Alkuperäinen telakointi-/scan-/outpost-smoke | PASS |
| Aiempi hero-smoke: oikeat mitat, LOD, 200 m aukko, kolme kameravaihetta, skip | PASS |
| Kuusi todellista Godot Compatibility -mallikuvaa | PASS, ei visuaalinen hyväksyntä |
| Koko kolmen mallin `--require-models` | Tarkoituksella estetty: telakka ja asema puuttuvat; vastatesti todistaa tämän |
| GitHub-hosted CI | EI VARMENNETTU tässä ympäristössä |
| Android / Mobile-renderöijä / FPS / lämpeneminen | EI AJETTU |

Paikalliset renderit syntyivät Xvfb/Mesa-ohjelmistorenderöinnillä. Kuvamittarit kertovat tästä renderöintikerrasta, eivät puhelimen nopeudesta. Lopullisten tiedostojen testiajojen paluukoodit ja SHA-256-tarkisteet löytyvät `validation.json`:sta. CI-työnkulku toistaa importin ja kuvat sekä kokoaa lähteen ja GLB:n ladattavaksi artefaktiksi, kun työnkulku saadaan GitHubissa ajettua.

### Kehityksen aikana löytyneet ja korjatut epäonnistumiset

1. Godot yritti tuoda `.blend`-lähteen automaattisesti ja ilmoitti puuttuvasta Blender-polusta. Lähdekansioon lisättiin `.gdignore`; ainoa runtime-lähde on nyt eksplisiittinen GLB.
2. Ensimmäinen kuvaus peri pelin pystysuuntaisen ikkunan ja tuotti vain 562 × 1000 kuvat. Kuvausskripti asettaa oman maisemaviewportin ja testaa jokaisen PNG:n todellisen resoluution.
3. Studion heijastusasetuksessa käytettiin väärää Godot-enum-nimeä. API:n todellinen `REFLECTION_SOURCE_SKY` tarkistettiin ja korjattiin.
4. Blender-lähdetesti laski mukaan käyttämättömän `Render Result` -oletuskuvan. Nyt se tarkistaa täsmälleen neljä materiaalien käyttämää nimettyä ja pakattua kuvaa.
5. Ensimmäisen maisemakuvauksen yläkuva leikkasi rungon. Rajausvastatesti epäonnistui aidosti. Kamera sovitetaan nyt jokaisen projektion kaikkiin mittarajojen kulmiin; testin 20 pikselin marginaalia ei löysennetty.
6. Tekstuurien tuontitavan vaihto jätti vanhaan välimuistiin poistettujen johdannaisten UID-varoituksia. Lopullinen toimitus varmennettiin puhtaalla importilla; kartat eivät riipu näistä tiedostoista.

Ympäristön ADB:n automaattinen laitehaku ilmoitti kirjoitussuojatusta `/home/agent/.android`-hakemistosta. Se ei estänyt Godot-importtia tai testejä, eikä Android-laitetestausta väitetä tehdyksi.

## Jäljellä olevat puutteet ja hyväksyntä

Malli on konkreettinen tarkastettava ehdokas. Sitä ei merkitä automaattisesti korkealaatuiseksi testituloksilla. Suojalevyjen toisto, laajat tasaiset pinnat ja siisti materiaalipinta voivat edelleen vaatia taiteellista jalostamista suhteessa konseptiin. Ohjaamon lasi on tummaa opaakkia pintaa, ei valmista sisustusta. Materiaalit eivät sisällä käsin maalattua kulumaa tai baked-AO:ta. Tarkastelu on staattinen: ei moottorianimaatiota, pelifysiikkaa tai collision-integraatiota. Automaattisten LOD:ien siirtymät ja pienten yksityiskohtien välkkyminen on tarkastettava puhelimessa myöhemmin.

**Suositus: GO vain mallin visuaaliseen katselmointiin; NO-GO julkaisuun tai seuraavan asema-/telakkavaiheen hyväksyntään.** Käyttäjän seuraava päätös on, vastaavatko siluetti, ohjaamo, suojakehät, lastiosiot ja perä konseptin tyyliä. Mahdollinen jatkokorjaus kohdistetaan tämän saman `.blend`-lähteen havaittuihin puutteisiin. `review_status=candidate` ja `release_approved=false` säilyvät.
