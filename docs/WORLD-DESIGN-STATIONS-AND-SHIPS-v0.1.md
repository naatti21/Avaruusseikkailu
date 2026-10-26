# Avaruusseikkailu — Asemien ja alusten Shape Bible v0.1

**Päivitetty:** 2026-10-26  
**Tila:** Luova suuntapäätös ja avoimet konseptit. Ei hyväksyttyä 3D-mallia eikä toteutuslupaa.  
**Projekti:** `naatti21/Avaruusseikkailu` (Android/Godot, mobiili ensin).

## 1. Mitä käyttäjän kanssa päätettiin

- Peli ei saa täyttyä samanlaisista avaruusasemista. **Asemien muoto, rakenne, koko ja tunnelma vaihtelevat niiden tarkoituksen, historian, tekniikan ja hallinnon mukaan.**
- Mukaan halutaan **jättimäisiä monikulmaisia asemia, pyöriviä rengashabitaatteja, asutuspintaisia renkaiden/sylinterien sisäosia** sekä täysin uusia siluetteja. Innovointia ei rajata perinteisiin sci-fi-kuvastoihin.
- Asema voi olla pitkä, leveä, paksu, kerroksellinen, ontto, epäsymmetrinen tai vähitellen yhteen kasvanut. Ei vain saman rakenteen pidentämistä tai kopiointia.
- Myös **aluksista rakennetaan eri luokkia ja tunnistettavia malliperheitä**, ei yhtä skaalattavaa rahtialusta joka tehtävään.
- Ulkonäön tavoite on **uskottava, yksityiskohtainen, elokuvallinen teollinen sci-fi**, ei puhtaan geometrinen low-poly-prototyyppi.
- **Ensin konseptikuva ja hyväksyntä, vasta sitten 3D-mallinnus ja Android-optimointi.** Aiemmat Godot-prototyypit todistavat työkaluketjua, eivät tavoitellun grafiikan toteutumista.

## 2. Ensimmäinen visuaalinen tyylisuunta — Orbital Colony

Keskustelussa 26.10.2026 nähty ja käyttäjän myönteisesti vastaanottama konseptitaulu:

- Noin **8 km pitkä** aksiaalinen yhdyskunta: **kaksi pyörivää, asuttua sylinteriä**, raskas keskusrunko, huolto-/teollisuus-/liikenneverkostot ja useita telakoita.
- Yleisnäkymä, 30 m rahtialuksen lähestyminen, **~200 m syvä** teollinen telakointihalli sekä aluksen sivu-, ylä- ja takaprofiilit.
- Ulkonäkö: näkyviä asuin-/vihervyöhykkeitä, ikkunapintoja, modulaarista koneistoa, valoja, pieniä aluksia mittakaavan havainnollistamiseen; vaalea kulutettu metalli, tummat rakenteet ja hillityt toimintavalot.
- Konseptin **rahtialus on noin 30 m × 12 m × 8 m**, toiminnallisesti ja visuaalisesti selkeä (ohjaamo, lastitila, kaksi takamoottoria).
- **Tärkeä raja:** tämä on **yksi hyväksytty tyylisuunta**, ei jokaisen jättiaseman pakollinen muoto tai lopullinen mittapiirustus. Konseptikuva ei sellaisenaan ole pelimoottorin 3D-malli. Koko ja mittasuhteet ovat konseptiarvoja.
- Viitteenä on keskusteluun ladattu konseptitaulu "01 KOKONAISUUS — ORBITAL COLONY / 02 LÄHESTYMINEN / 03 TELAKOINTIALUE / RAHTIALUS 30 m". Taulun kuvallinen kopio ei vielä kuulu tähän GitHub-tiedostoon.

## 3. Asema-arkkityypit — monimuotoinen galaksi

Seuraavat ovat **suunnitteluperheitä, eivät lukittuja lopullisia asema- tai kaupunkimalleja**.

| Tyyppi | Siluetti ja fyysinen idea | Käyttö, tunnelma |
|---|---|---|
| **Twin Cylinder Colony** | Kaksi tai useampi pyörivä, asuttu sylinteri, aksiaalinen selkäranka, eri painovoimavyöhykkeet | Suuri siviiliyhdyskunta, tuotanto, kauppa; ensimmäisen konseptin perhe |
| **Colony Ring** | Yksi tai useampi massiivinen rengas/torus; sisäpinnan asutusta, näkyvä ulkorungon kerroksellisuus | Siviilikaupungit, puistot, varakkaat hubit, vanhat asutusohjelmat |
| **Polyhedron Bastion** | Kulmikas monitahokas, suojatut sisätilat, suuret polygoniset rungot ja telakkakuilut | Hallinto-, turva-, tutkimus- tai linnoitusmainen asema; ei automaattisesti taistelupeli |
| **Industrial Spine** | Pitkä, raskaasti tuettu logistinen runko, irrotettavia jalostus-, rahti- ja telakkamoduuleja | Kaivos-, tehdas-, korjaamo- ja kaupankäyntisolmu |
| **Modular Cluster** | Eriaikaiset, erimuotoiset moduulit sidottu yhteen silloilla, putkilla ja kehikoilla; epäsymmetrinen kasvu | Vapaa satama, reunaseudun kasvava asutus, kauppayhteisö |
| **Shard Hive / Experimental** | Yllättävä, mutta toiminnallisesti perusteltu sirpale-/monikulmiokokonaisuus, ontto ydintila tai useita epäsymmetrisiä osia | Epätavallinen kulttuuri, kokeellinen tekniikka, arvoituksellinen löytö |

**Säännöt:**
1. Sama tehtävä (esim. satama) voi esiintyä monessa muodossa; muotoa ei arvota ilman syytä.
2. Jokaiselle suurelle asemalle tulee oma **kaukaa luettava siluetti**, selvästi erottuva keskietäisyyden rakenne ja lähikuvan mekaaninen logiikka.
3. Mittakaavan pitää näkyä vertaamalla aluksia, telakkoja, kulkuväyliä, asuntojen rakenteita ja huoltoliikennettä — **ei vain ruudun "6 000 m" -tekstissä**.
4. Pyörivä habitaatti ja ei-pyörivä telakka suunnitellaan niin, että sisäinen painovoima ja telakointi ovat kerronnallisesti ja rakenteellisesti ymmärrettäviä. Näennäisfysiikan tarkempi toteutus arvioidaan erikseen.
5. Jokaisella asemalla on käytännön rajat: energia, lämpö, rakenteet, kulkuväylät, satamakapasiteetti ja eri asukasryhmien käyttämät alueet. Sääntöjen tarkoitus on ohjata uskottavuutta, ei estää luovuutta.
6. Asemat saavat ikää, kulttuuria, materiaaleja, valaistusta ja korjauksia; ei vain saman 3D-mallin värivariaatioita.

## 4. Alusluokat — eri tehtävä, eri muoto

Suunniteltavat perheet, **mitat ovat toistaiseksi ehdotuksia**:

| Luokka | Suuntaa-antava koko | Visuaalinen ja pelillinen tehtävä |
|---|---:|---|
| **Courier / Small Freighter** | ~25–40 m | Pelaajan ensimmäinen alus, 30 m referenssi; ohjaamo, tavaratila, selkeät moottorit |
| **Service Tug / Shuttle** | ~8–20 m | Liikenteen skaala, telakkatyö, hinaaminen, huolto, henkilökuljetukset |
| **Explorer / Survey Vessel** | ~30–90 m | Sensorit, näytevarastot, pidempi toimintamatka, tutkimuslaitteet |
| **Medium Freighter** | ~60–180 m | Isommat kuljetukset, konttimoduulit, vaihteleva lasti, enemmän telakkatarvetta |
| **Heavy Hauler / Ore Carrier** | ~200–800 m | Kaivos- ja teollisuuskuljetus, rakenteellisesti avoimet kiinnitykset, massiivinen kapasiteetti |
| **Passenger / Colony Transport** | ~80–400 m | Matkustajia ja elinympäristöä, suuret ikkunat/habitointi, eri turvavaatimukset |
| **Patrol / Security Craft** | tapauskohtainen | Tunnistettavat turvallisuusalukset ja paikallishallinto; taistelu ei ole pääsilmukka |
| **Experimental / Unusual** | vapaa | Kokeellinen, muukalainen tai kulttuuriltaan omaperäinen malli; myöhemmin tarkennettava |

- Jokainen aluksen siluetti kertoo **mitä se tekee**. Eri luokat eivät ole vain pienennettyjä tai kasvatettuja kopioita.
- Aluksella on ohjaus/asutus, lasti tai varusteet, energiarakenne, huollettavat koneistot, moottori-/asenneohjaus, kiinnityspisteet ja telakointitapa sen tehtävän vaatimalla tarkkuudella.
- Aluksen tekniset ratkaisut ja estetiikka voivat vaihdella valmistajan, aikakauden ja taloudellisen taustan mukaan.
- Ensimmäisen ~30 m courierin lähtökohtana on yllä mainittu konseptitaulu; **pelin nykyistä low-poly-courieria ei hyväksytä tuotantotason visuaaliseksi malliksi**.

## 5. Mitä ei lukita vielä

- Ei yhtä kanonista asemamuotoa, tarkkaa kokonaisasemien lukumäärää eikä lopullisia kilometrejä jokaiselle luokalle.
- Ei yhtä lentokaluston valmistajaa, yhtä kansainvälistä nimeä tai täydellistä aluslistaa.
- Ei MMO-/online-, talous-, taistelu- tai sisätilapelimekaniikan laajennusta osana tätä konseptityötä.
- Ei väitettä, että generoidun 2D-konseptin kaikki osat voidaan suoraan toteuttaa Androidissa identtisellä tarkkuudella.

## 6. Seuraava sovittu työjärjestys

1. **Shape Bible -konseptikuvat:** 4–6 erilaista isoa asemasiluettia rinnakkain. Erojen pitää näkyä jo mustina ääriviivoina; vähintään rengas/asutuspinta, monikulmio, aksiaalinen asutus, teollisuus ja villi kokeellinen rakenne.
2. **Alusperheiden konseptit:** ensin ~30 m courierista kunnon 3-suunnan mallilehti; lisäksi vertailuna pieni huoltoalus, tutkimusalus ja 1–2 suurempaa rahtialusta.
3. **Valitaan yksi asema ja yksi alus pilotoitavaksi:** hyväksytään ulkoasu, rakenteiden logiikka, materiaalit, mittakaava ja kolme kamerakuvaa; vasta sen jälkeen Blender/Godot-tuotanto.
4. **Yksi laadukas 3D-vertical slice:** mallien luettavuus ja uskottavuus prioriteetiksi; optimoidaan todellisella Android-puhelimella, ei yksinkertaisteta ensimmäisenä takaisin harmaiksi laatikoiksi.
5. **QA-portti:** käyttäjän erillinen visuaalinen GO + laitetesti + toistettavat tekniset tarkistukset ennen yhdistämistä tai julkaisemista.

## 7. Jatkuvuus suhteessa vanhoihin prototyyppeihin

- `PR #8`: vanha 1,8 km Blender/Godot-mittakaavakoe.
- `PR #9`: 6 km aksiaalinen v0.2, alkuperäistä parempi tekniikka ja mobiilimittaus, mutta **käyttäjä ei hyväksynyt visuaalista tasoa** (liian prototyyppimäinen, varastomainen yhdyskunta, laatikkomainen alus).
- `26.10.2026 konseptitaulu`: ensimmäinen käyttäjän mielestä houkuttelevampi tyylisuunta; **ei vielä hyväksytty tuotantoassetti**.
- Tämä dokumentti on vain luovan maailmankuvauksen muistipohja. **Ei muuta lähdekoodia, ei mergeä, ei julkaise sovellusta.**

## 8. Käytännön muistilause

**Älä pyydä Codexia arvaamaan "kaunista 6 km asemaa" pelkällä proseduraalisella geometriasäännöllä.** Konseptoi ja hyväksytä identiteetti ensin. Galaksin asema- ja alusperheille on jätettävä tilaa olla oikeasti erilaisia.
