# Avaruusseikkailu — toteutuspilotti 01: Twin Cylinder + C-07

**26.10.2026 — ART INTAKE / NO-GO.** Tämä ei ole uusi peliversio eikä väite valmiista 3D-grafiikasta.

## Miksi juuri tämä pari?

Valittu Shape Bible v0.1:n konseptikuvista:
- **Twin Cylinder Colony:** kaksi erottuvaa pyörivää asuinsylinteriä ja niiden välissä ei-pyörivä huolto-/telakointirunko, pituustavoite noin 8 km.
- **C-07 Courier:** noin 30 × 12 × 8 m, selvästi hahmotettava ohjaamo, rahti, huolto, asennonsäätö ja moottorit.
- **Telakointisektori:** yksi uskottavasti rakennettu lähiympäristö, suuntaa antava 200–250 m syvä teollinen satama.

Nämä ovat **konseptista johdettuja tuotantotavoitteita**, eivät teknisiä faktoja tai hyväksyttyjä lopullisia assetteja.

## Varsinainen työjärjestys — älä ohita laatukynnystä

1. **C-07 tuotantokelpoinen mallikandidaatti ensin.** Blender-hard-surface / todellinen 3D-taide, ei vain satunnaistettuja laatikoita. Malli sisältää edestä/sivulta/takaa tunnistettavan siluetin, toiminnalliset rungon/lastin/moottorien muodot, materiaalit ja UV:t. Samasta *oikeasta* mallista kolme Godot-kuvakaappausta. Hyväksyntä erikseen.
2. **Yksi telakointisektori** C-07:n mittakaavassa: rakenteellisesti ymmärrettävä 200–250 metrin pääsy, huoltotasot, rahtikäytävät, tarkoituksenmukaiset valot. Ei tyhjää laatikkohallia.
3. **Koko Twin Cylinder -kaukaa luettava siluetti**, vähäisemmällä detaljilla: kaksi erillistä asuinsylinteriä, rotaation logiikka, ei-pyörivä keskusrunko, telakointi staattisessa osassa, erilliset lämpösäteilijät ja liikenne. Kauniit asutusnäkymät ovat inspiroivia leikkauskuvia, eivät peruste tehdä koko painekuoresta läpinäkyvä.
4. Renderöijävertailu Androidilla **samasta GLB:stä**. Performance tavoitteet: lämmin ~30 FPS keskiluokassa, ~60 FPS tehokkaassa puhelimessa, ei hyväksyntää ilman todellista testiä.
5. Jos kuva muistuttaa jälleen low-poly-varastoa, **STOP**. Palataan malliin eikä lisätä ominaisuuksia tai piiloteta ongelmaa tekstuureilla.

## Koodipohja, joka tässä haarassa todella valmisteltiin

- `native-prototype/production/asset_manifest.json` yksilöi kolme hyväksyntää odottavaa mallipaikkaa.
- `native-prototype/tools/check_production_art.py` tarkastaa polut, mittojen määrittelyt, lähdetiedot, GLB/PBR-sisällön ja estää hyväksynnän ilman varsinaista mallia.
- `native-prototype/scenes/production_art_preview.tscn` ja `scripts/production_art_preview.gd` näyttävät myöhemmin tuotavat mallit omassa pyörivässä tarkastusnäkymässä. **Ei piilotettuja varamalleja.** Puuttuva malli näkyy rehellisesti puuttuvana.
- `native-prototype/tools/production_art_preview_smoke.gd` ja CI tarkistavat näkymän perustan.
- Päähaaran julkaistu selainpeli, v0.2 Blender-prototyyppi, telakointisäännöt ja tuotanto-APK:t **ennallaan**.

## Mallinnuksen palautus ja tiedostovaatimukset

| Slot | Mallitiedosto | Luokka | Suuntaa antava koko |
| --- | --- | --- | --- |
| C-07 | `native-prototype/production/models/c07_courier.glb` | Pelaajan alus | 30 × 12 × 8 m |
| Colony | `native-prototype/production/models/twin_cylinder_colony.glb` | Yhdyskunta, kaukomalli | 8 km pituus |
| Dock | `native-prototype/production/models/twin_cylinder_berth.glb` | Lähiympäristön sektori | 250 × 140 × 120 m |

Kun aito mallikandidaatti toimitetaan, sen lähde, tekijä, lisenssi, SHA256 ja `candidate`-tila merkitään manifestiin. Yhteiset vaatimukset: **GLB 2.0**, metreissä, UV/PBR (base color / metallic-roughness / normal), upotetut tekstuurit tai dokumentoitu muutostyö, toimivat kamerat/LOD ja alkuperäloki. Näiden automaattitesti ei korvaa visuaalista arviointia.

Älä merkitse `approved`, ennen kuin käyttäjä on tarkastanut oikeat Android-kuvat. Myöskään `approved`-merkintä ei yksin muuta `release_approved=false`-estettä.

**Älä käynnistä vielä täyden 8 km kaupungin geometriaa automaattisesti.** Ensin C-07, sitten toimiva telakka, lopuksi kaukaa nähtävä asutusrakenne. Tämä katkaisee v0.1/v0.2:ssa toistuneen epäonnistuneen tuotantomallin.
