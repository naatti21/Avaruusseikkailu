# C-07 A4 – Android-grafiikan laitetesti

27.10.2026: käyttäjä hyväksyi A4-mallin vain Android-grafiikkatestin pohjaksi. Malli ei ole valmis eikä hyväksytty peliin.

## Testiversiot
- c07-a4-mobile-arm64.apk: Godot Mobile -renderöijä.
- c07-a4-compat-arm64.apk: Godot GL Compatibility -renderöijä.
- Sama alkuperäinen C-07 A4 GLB ja PBR-materiaalit kummassakin. Pakettitunnukset ovat erilaiset.

## Painikkeet
- KULMA vaihtaa etuviiston, sivun, takaviiston ja ylhäältä katsotun näkymän.
- VALO vaihtaa nykyisen pelivalaistuksen ja kirkkaamman tarkastusvalon välillä. Se ei muuta mallia tai lopullista peliä.
- KIERRÄ käynnistää tai pysäyttää kameran kierron.
- NOLLAA MITTAUS aloittaa ajan ja FPS/ruutuaikamittaukset alusta.

Mittarit näyttävät renderöijän, hetkellisen FPS:n, enintään 600 ruudun keskiarvon, p99-ruutuajan millisekunteina, piirtokutsut ja ajan minuutteina. Ruutuaika perustuu Godotin _process(delta)-näytteisiin eikä ole erillistä GPU-profilointia.

## Ohje puhelimella
1. Lataa GitHub Actionsin onnistuneesta ajosta c07-a4-mobile-vs-compat-apks -artefakti. Pura ZIP ja asenna molemmat APK:t.
2. Kuvaa etuviisto, sivu ja takaviisto pelin valaistuksella sekä etuviisto tarkastusvalolla.
3. Tarkastele ohjaamoa, rahtimoduulien kiinnityksiä, materiaalien tummuutta ja koneistoa.
4. Anna molempien versioiden pyöriä noin 10 minuuttia samoilla kirkkaus- ja virransäästöasetuksilla. Kirjaa keski-FPS, p99, lämpeneminen ja nykiminen.
5. Lähetä kuvat/luvut katselmointiin. Ota päätös lopullisesta mallihyväksynnästä erikseen.

Vähimmäistavoite on vakaa 30 FPS Android-keskiluokassa, tehokkailla laitteilla tavoite 60 FPS. Nämä eivät ole mitattuja tuloksia.

## Turvarajat
- C-07 A4:n hyväksyntäarvot pysyvät false.
- Pelin main_scene, telakointikoe, muut alukset, asemat, kauppa ja tehtävät pysyvät ennallaan.
- Android APK:t tehdään väliaikaisissa lähdekoodikopioissa ja testisignataan; niitä ei julkaista kauppaan.
- GitHub CI-tulos vahvistaa vain rakentamisen ja automaattisen smoketestin, ei oikean puhelimen grafiikkaa tai lämpötilaa.
- Testiartefaktin säilytys GitHubissa 7 päivää.

## Valaistuksen vertailukierros (27.10.2026)

Uusi kokeiluhaara tuo kolmannen tilan **TASAPAINO**. Painike kiertää nyt järjestyksessä **PELI → TASAPAINO → TARKASTUS → PELI**.

- **PELI** on sama aikaisempi tumma lähtötaso. Se on säilytetty vertailukelpoisena.
- **TASAPAINO** tuo metallille rajatut ympäristöheijastukset, hieman voimakkaamman päävalon, hillityn kylmän reunavalon ja täytevalon. Tausta pysyy tummana; tarkoitus ei ole valottaa koko avaruutta harmaaksi.
- **TARKASTUS** pysyy aiemman APK:n kirkkaampana tarkastustilana. Mallia tai sen materiaaleja ei muuteta tilojen välillä.

Ota puhelimella **KIERRÄ: EI**, sama **ETUVIISO** ja **TAKAVIISO** kaikilla kolmella valolla. Vertaile erityisesti moottorikehiä, keskirungon rakennetta, tavaramoduulien kylkiä ja sitä, säilyykö avaruuden kontrasti. Tarkista mahdollinen ylimääräinen pintahehku; jos metallista tulee muovinen tai kuvan varjot katoavat, uusi tila ei läpäise. Aiempi 0,1–0,4 minuutin FPS on vain lyhyt havainto. Vasta 10 minuutin saman laitteen testi kertoo lämpö- ja suorituskykyriskeistä.
