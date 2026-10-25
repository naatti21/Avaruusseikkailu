# Avaruusseikkailu – Android 3D -navigoinnin koe

Erillinen oikean 3D-pelimoottorin koe mobiilille; ei vanhan HTML-selainpelin päivitys. Godot 4.7.2, GDScript ja GL Compatibility -renderöinti. Yläviisto kamera, oikea 3D-alus, avaruusasema ja tutkimuspoiju.

Näpäytä avaruudessa olevaa kohdetta tai alareunan ASEMA/POIJU-painiketta. Alus lentää todellisessa 3D-tilassa valittuun paikkaan. Saavuttuasi voit telakoitua tai analysoida poijun. Ei turhaa vapaan lentelyn pakkoa.

Tämä EI ole vielä Kadonnut lähetys -tehtävä, kaupankäyntipeli eikä viimeistelty grafiikkaprototyyppi. Koe mittaa kameran, kosketusosumien ja aluksen automaattisen liikkeen mielekkyyttä.

## Koonti ja asennus

Käytä GitHub Actionsin Godot native 3D Android test -työnkulun onnistuneen ajon APK-artifaktia. Android 64-bittiselle laitteelle debug-APK, joka asennetaan tietoisesti testikäyttöön. Älä käsittele sitä kauppajulkaisuna. Koontitesti ajaa ensin Godot-automaatiosavun ja vasta sitten muodostaa APK:n. Tähän ei tarvita API-avaimia eikä release-allekirjoitusta.

## Mobiilikokeessa arvioi

- Onko avaruusalus, asema ja tutkimuspoiju selkeästi hahmotettavissa puhelimen pystynäytöllä?
- Löytyykö 3D-kohteen kosketusalue ensimmäisellä yrityksellä?
- Tuntuuko automaattilähestyminen lyhyeltä, luontevalta ja tarkoitukselliselta?
- Onko kameran korkeus, kuvakulma tai kohteen koko huono?
- Sulaako näkymä Androidilla ilman suurta viivettä?
- Haluaisitko tähän lisää manuaalista ohjausta, vai riittääkö kohteen napautus?

## Rajaukset

Ei tehtävä-, talous-, tallennus-, planeetannimeämis- tai onlineominaisuuksia. Ei julkaistua APK:ta sovelluskaupassa. Godot-koe pysyy erillisessä kehityshaarassa, eikä PR:ää yhdistetä ilman käyttäjän erillistä julkaisuhyväksyntää.
