# C-07 A / Design Pass v4 — Detailed Design Brief
**Päätös:** 27.10.2026 käyttäjä valitsi vaihtoehdon **A** jatkosuunnittelun pohjaksi, **ei hyväksynyt valmista pelimallia**.
**Työkohde:** `naatti21/Avaruusseikkailu` — pohjana `feature/c07-v3-silhouette-options`, PR #14 ja A:n todelliset Godot-kuvat.
**Vain suunnitteluvaihe:** Ei peliin integrointia, yhdistämistä `main`-haaraan eikä 8 km aseman mallinnusta samalla kertaa.

## Lukittu suunta, ei lukittu lopputulos

- Tunnistettava *kompakti, teollinen 30-metrinen courier/utility freighter*.
- Keskitetty ohjaamo, pitkä kantava runko, **kaksi irrotettavaa sivurahtimoduulia**, kaksimoottorinen perä.
- Suuntaa antava mittaluokka **29,86 × 11,44 × 7,875 metriä** tämän A-tutkielman mukaan; älä pakota sentintarkaksi jos toimiva muoto tarvitsee säätöä.
- Aluksella oltava järkevä fyysinen järjestys: miehistön paineistettu tila, rahti ja lukitukset, kantavat kuormareitit, tankit/koneistot, moottorien kiinnitys, asennonsäätö, huoltokulku, telakointirakenne ja lämmön hallinta.
- **A/B-malleja ei enää yhdistellä tai arvota** ilman uutta nimenomaista päätöstä; B säilytetään koskemattomana erillisenä referenssinä. Alkuperäinen C-07 säilyy ennallaan vertailua varten.

## Korjattava ennen tuotantotason yksityiskohtia

1. **Ohjaamo ei saa näyttää maantiekuljetusajoneuvon hytistä irrotetulta.** Korjaa otsa/nokka, ikkunageometria, sensorit, huoltopaneelien ja telakoinnin sijainti. Ohjaamo ja painekuori ovat yhtenäinen avaruusalusratkaisu.
2. **Rahtimoduulit eivät saa jäädä kahdeksi oranssiksi tasaiseksi laatikoksi.** Näytä mekaaniset lukitukset, suojakehät, huolto- ja nostokohdat, rungon ja rahtimoduulien väli, liitoskohdat sekä irrotettava toiminto. Erota paineistettu tai paineistamaton kuljetus perustellusti.
3. **Kantava runko ja voimalinja pitää yhdistää uskottavasti.** Moottorityöntö välittyy vahvistettuihin rakenneosiin, eikä vain yhteen koristeelliseen keskipalkkiin. Rakenteen massajakauma pysyy tulkittavasti tasapainossa.
4. **Moottorien oikea toiminnallinen integraatio.** Kiinnitys, huoltopaneelit, polttoaine/energia, lämpösuojat, jäähdytyksen toteutus ja pienet asennonsäätösuuttimet; vältä pelkkiä suuria hehkuvia putkia.
5. **A:n suuri muoto jää pääasiaksi.** Kuvakulmissa 3/4, ylhäältä ja sivulta erotettava ohjaamo–kuormarunko–rahti–koneisto ilman tekstuuria tai valoefektejä. Vasta toimivan päämassan jälkeen geometrinen detaljointi, UV ja materiaali.
6. **Valotus myös pelin valoissa.** Näytä käytännölliset työ-/navigointivalot ja varjoon jäävä rakenne; materiaalit PBR base color + metallic/roughness + normal + harkittu AO/emissive. Ei pimeyden kompensointia pelkillä liian kirkkailla päävaloilla tai hohtavalla rungolla.
7. **Näkymä ja käyttäjän päätös.** Toimita realistiset *oikean GLB:n Godot-katselukuvat*: kuusi suunnasta vakioidulla kameralla + 2 pelin omassa valaistuksessa. Lisäksi rajatut lähikuvat ohjaamosta, rahtilukoista ja moottorirakenteesta. Esitä rinnakkain A v3 ja A v4 samoista kuvakulmista.

## Mallinnuksen rajattu toimintasuunnitelma

**Vaihe 1 – päätöksen jälkeinen muotoilutarkastus:** tee A:n päämassoittelun korjausehdotus, ei massiivista detaljipassia. 3/4, sivu ja yläkuvissa tulee näkyä erot vanhaan A:han. Tarkista rahtimoduulien lukitusten ja painopisteen periaatteet järkeväksi.

**Vaihe 2 – oikea A v4 Blender/GLB-mallikandidaatti:** säilytä A v3 ja B ennallaan. Tee muokattava .blend + GLB, UV/PBR kartat vain hyödyllisissä kohdissa, riittävä mutta perusteltu mesh- ja draw-call-budjetti. Ei pelkkiä uusi tekstuuri päälle -muutoksia.

**Vaihe 3 – Godot-katselmointi:** samat kuvakulmat + pelin valaistus; dokumentoi mittasuhteet, kolmio-/materiaalimäärät, tekstuurikoko, lähde/lisenssi/SHA-256, Blender → GLB → Godot -ketju. Testitulokset eivät ole vielä puhelimen FPS. Pyydä käyttäjän uusi **visuaalinen GO**.

**Vaihe 4 – vasta visuaalisen hyväksynnän jälkeen:** erillinen Android Mobile/Compatibility FPS/frametime/thermal-testi sekä ensimmäisen telakan geometria. Älä hyppää tähän ennen GO:ta.

## Laatuportit

- `selected_option = "A"` tarkoittaa vain muotoilusuuntaa.
- `owner_visual_approval=false`, `production_asset_approved=false`, `can_integrate=false` ja `release_approved=false` pysyvät, kunnes käyttäjä tekee kunkin hyväksynnän erikseen.
- Olemassa oleva PR #14 pysyy draftina eikä sitä yhdistetä automaattisesti. Toteutus seuraavaan **omaan draft-PR:ään** A v4:lle.
- **STOP**, jos A v4 näyttää edelleen tavalliselta kuorma-auton ohjaamolta, jossa on oranssit laatikot ja kaksi moottorikelloa. Palaa silloin päämassoitteluun, älä vain lisää pikkuyksityiskohtia.
