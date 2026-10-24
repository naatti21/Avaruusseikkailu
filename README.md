# Avaruusseikkailu

Mobiilille suunniteltu avaruusseikkailu – ensimmäinen pieni peliprototyyppi (v0.1).

Pelin ydinsilmukka: ota kuljetustehtävä, hyppää tähtikartalta, lennä vapaasti lähialueella, telakoidu; tutki kauempana tuntematon planeetta, skannaa ja anna sille oma nimi.

## Kokeilu paikallisesti
Tarvitset Node.js:n ja paikallisen HTTP-palvelimen (esimerkiksi python3 -m http.server 8000). Avaa http://localhost:8000/ selaimessa. Pelitila tallentuu selaimen localStorageen.

## Testaus
npm test

## Rajaukset
Tämä on kevyt HTML Canvas -pelattavuuskokeilu, ei vielä varsinainen 3D-moottori tai MMO. Neljä järjestelmää, yksi kertaluonteinen kuljetustehtävä, kaksi löydettävää planeettaa, tutkiskelua ja yksinkertainen kehitys. Nimet ovat tässä versiossa vain paikallisia. Online-ensisijainen löytö ja moderointi toteutetaan myöhemmin auktoritatiivisesti palvelimella.

Kehityksen sovitut rajaukset ja laadunvarmistus: APP-SPEC.md. Sovelluksen yhteinen playbook: v1.9.2.

## Julkaisu
Kehitystä tehdään feature-haarassa ja draft-PR:ssä. Älä yhdistä mainiin tai käynnistä GitHub Pages -julkaisua ennen käyttäjän hyväksyntää.