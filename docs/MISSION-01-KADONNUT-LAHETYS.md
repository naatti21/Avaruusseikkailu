# Avaruusseikkailu — MISSION 01: Kadonnut lähetys

Versio: suunnitteluluonnos 0.1 / 25.10.2026
Tila: hyväksymätön game-design. Ei toteutuksen tai julkaisun GO.
Kohdealusta: Android-natiivipeli. iOS myöhemmin mahdollinen.
Pelimalli: isometrinen 3D, kohteen napauttaminen ja aluksen automaattinen paikallisliike. Pitkät siirtymät automaattisesti.

## Päätavoite

Todista, että 3–6 minuutin kuljetustehtävä kiinnostaa ilman turhaa lentokontrollia, jatkuvaa näpäyttelyä, turhia välinäyttöjä ja pakotettua taistelua.

Pelaaja tekee 3–4 päätöstä, joiden aika-, resurssi- tai mainevaikutukset ovat näkyviä. Alus liikkuu oikeassa 3D-tilassa, mutta animaation on palveltava ymmärrettävää toimintaa. Merkittävillä löydöillä on näyttävämpi lähempi kamerakuva.

## Tausta ja alkutila

Lähtöasema: Kestrel Port.
Kohde: Sable Mining Colony, kaivossiirtokunta.
Tehtävä: toimita kiireellinen laillinen lääkintälasti.
Polttoaine: 5 yksikköä; kumpikin reitti mahdollinen.
Palkkio ajallaan: 450 cr. Myöhässä: 300 cr.
Aikaisen toimituksen bonus, enintään 3 peliaikayksikköä: +120 cr.
Määräaika: 6 peliaikayksikköä. Tämä EI ole oikean maailman ajastin; sovelluksen sulkeminen ei aiheuta viivettä.

Numerot ovat vain ensimmäisen tehtävän pelitestitasapainotusta.

## Käyttötilanteet, kosketukset ja seuraukset

| Näyttö | Käyttäjä näkee | Käyttäjän teko | Seuraus |
|---|---|---|---|
| Asema | Iso tehtäväkortti: lääkkeet, kohde, palkkio, aika | Hyväksyy kuljetuksen | Lasti ja tehtävä tallentuvat, tähtikartta avautuu |
| Reittikartta | Kaksi vaihtoehtoa; aika, polttoaine, erityisriski | Valitsee ja vahvistaa reitin | Päätös kirjataan; matkustaminen alkaa |
| 3D-sektori | Alus liikkuu väylällä; kohde näkyy suoraan | Ei turhia komentoja. Napauttaa vain toiminnallista kohdetta | Tullaan seuraavaan kiinnostavaan päätökseen |
| Valinta A | Virallinen rahtitarkastus | Tavallinen tarkastus tai maksullinen pikakäsittely | Aika tai raha muuttuu |
| Valinta B | Epätavallinen signaali asteroidivyöhykkeessä | Jatkaa tai poikkeaa tutkimaan | Viive, tutkimismahdollisuus |
| Tutkimus B | Kaksi signaalia ja ymmärrettävä havainto | Valitsee todennäköisen keinotekoisen signaalin | Löytö tai virhetulkinta |
| Määränpää | Lyhyt lähestyminen / toimituskortti | Toimittaa lastin | Maksu kerran, loki ja seuraukset |
| Yhteenveto | Raha, viive, löydöt sekä niiden syyt | Jatkaa | Tieto tallessa seuraavia keikkoja varten |

### Reitti A: valvottu kuljetuskäytävä

Matka: 3 aikayksikköä, 2 polttoainetta. Varmempi ja lyhyempi matka, pakollinen tarkastus.
- Tavallinen tarkastus +1 aikayksikkö: toimitus hetkellä 4, palkkio 450 cr.
- Pikakäsittely maksaa 70 cr: toimitus hetkellä 3, palkkio 450+120−70 = 500 cr nettomäärä.
Tässä tehtävässä ei tutkimuspoijua tällä reitillä.

### Reitti B: ulkovyöhyke

Matka: 4 aikayksikköä, 3 polttoainetta. Ei tarkastusta. Rajatulla sektorilla voidaan havaita poikkeava signaali.
- Ohita signaali: toimitus hetkellä 4, palkkio 450 cr.
- Tutki signaali onnistuneesti: +2 aikayksikköä, +80 cr tutkimusdatasta; toimitus hetkellä 6, yhteensä 530 cr ja tutkimusvihje.
- Virhetulkinta: +1 ylimääräinen aikayksikkö; toimitus myöhästyy ja peruspalkkio on 300 cr. Löytöä ei kirjata onnistuneeksi.

Ulkoreitti ei ole yksiselitteisesti paras: se kuluttaa enemmän polttoainetta, sisältää virhetulkinnan riskin ja voi vaatia myöhemmin lisähuoltoa. Pelaajalle näytetään tärkeimmät erot ennen reittivalintaa.

## Tutkimistehtävän pieni oivallus

Nähdään kaksi lähdettä:
- A: kapea signaali, joka toistuu täsmälleen 17 sekunnin välein;
- B: leveä, epäsäännöllinen kohina kaasupilvestä.

Lyhyt vihje: täsmällinen, toistuva pulssi voi olla keinotekoinen lähetin. Pelaaja valitsee kumman tutkii; ei arvontaa eikä yhtä nappia, josta saa palkinnon. Oikea valinta A paljastaa hylätyn tutkimuspoijun, +80 cr ja vihjeen tulevaa tehtävää varten. Virhe B aiheuttaa viiveen. Pelaaja näkee perustelun jälkeenpäin.

Tätä poikkeamaa ei tule jokaiseen myöhempään keikkaan. Hiljaiset matkat kuuluvat peliin.

## Neljä pääasiallista näkymää

1. **Asema ja tehtäväkortti:** yksi asia kerrallaan. Kohde, palkkio, kiire, hyväksy.
2. **Reitti:** isometrinen tai tähtikarttatason kuva, valittava reitti, alareunan yhteenveto. Näpäytä valinta, vahvista.
3. **Paikallinen 3D-sektori:** hieman ylhäältä vino kamera, helposti erottuva alus, pari selkeää toiminnallista kohdetta (asema, poiju). Kohteen napautus käynnistää 3–5 s autopilottilähestymisen; ohitus sallittu. Ei vapaan avaruuden jatkuvaa naputtelua tai pakollista virtuaalista ohjaussauvaa.
4. **Tulokset ja loki:** näkyvä syy–seuraus; toimituspalkkio, tutkimustieto ja mahdollinen myöhästyminen.

Kameran tarkka kulma, zoom ja taidetyyli testataan oikealla laitteella, eikä niitä lukita tässä suunnitelmassa.

## Reunatapaukset ja pelin reiluus

- Pelaajan keskeyttäessä sovelluksen peliaika pysähtyy, tehtävä ja valittu reitti säilyvät.
- Palkkiota ei voi kerätä uudelleen palaamalla näkymään.
- Väärä tutkimusvalinta ei tuhoa edistymistä, vaan aiheuttaa näkyvän kustannuksen.
- Polttoaine on kummallekin reitille riittävä; myöhemmin estetään mahdottomat reitit jo valintanäkymässä.
- Animaation ohitus ei muuta aikaa, rahaa tai löydön tulosta.
- Ei salakuljetusta tässä laillisessa lääketoimituksessa; oma erillinen myöhempi tehtävä.
- Planeetan löytäminen ja nimeäminen säilyvät suunnittelussa, mutta eivät kuormita ensimmäistä tehtävää. Online-ensisijaisuus ratkaistaan myöhemmin palvelimella, ei paikallisella tallennuksella.

## Ensimmäisen toteutettavan 3D-testin minimirajaus

Godot 4 on moottoriehdokas, ei vielä lopullisesti vahvistettu valinta. Kokeillaan Androidilla: yksi alus, yksi isometrinen 3D-ympäristö, selkeä kosketettava kohde, sujuva autopilottiliike, valittava kamera/lähikuva ja keskeytyksen hallinta.

Tämä tekninen testi edeltää kaupankäyntiä, fraktioita, koko galaksia ja onlinea. Ei tarvetta kauniille viimeistellylle grafiikalle, mutta myös paljas siirtyvä piste on liian heikko lentotuntuman arviointiin.

## Hyväksymiskriteerit

1. Tehtävän ymmärtää ilman ohjekirjaa; reittivaihtoehdon hinta/aika näkyy ennen päätöstä.
2. Kolme testipolkua tuottavat toistettavasti eri lopputulokset: A/tarkastus, B/oikea tutkimus, B/väärä tutkimus.
3. Tehtävä on läpäistävissä 3–6 minuutissa; ei yli 5–8 sekunnin turhaa odottelua, animaatio ohitettavissa.
4. Toiminnot sopivat 360–430 px puhelinnäytölle, myös yhdellä kädellä.
5. Oikeaa Android-koetta EI ole vielä ajettu; suorituskykyä tai käyttömukavuutta ei väitetä testatuksi.
6. Pelitila säilyy keskeytyksestä; palkkio vain kerran.
7. Pelaajalla on vähintään kolme aitoa päätöstä ja hän ymmärtää niiden seuraukset.
8. Jos autopilotti on vain koriste, sitä lyhennetään — ei lisätä väkisin manuaalista lentelyä.

## Rajaukset ja työjärjestys

Tässä työpaketissa: pelisilmukka, kosketukset, päätökset, resurssit, 3D-kameran koekriteerit.
Seuraavaksi: natiivi Android 3D-kosketus- ja autopilottikoe erilliseen kehityshaaraan. Sitten pelitehtävän toteutus.
Myöhemmin: muut kuljetukset, salakuljetus, planeettalöydöt ja nimeäminen, jatkuvuus, talous, fraktiot ja online.

Ei nyt: MMO, PvP, planeetalle laskeutuminen, FPS, rakennusjärjestelmät, proseduraalinen valtava galaksi.

Julkaisuportti: ei main-mergeä tai releaseä ilman erillistä hyväksyntää ja laitetestausta.
