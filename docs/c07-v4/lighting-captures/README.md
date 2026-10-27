# C-07 A4 – automaattiset valaistuskuvat

**Godot 4.7.2 / Linux / GL Compatibility.** Nämä ovat **oikeasta GLB-3D-mallista** automaattisesti renderöidyt Godot-kuvat, **eivät Android-emulaattorin kuvankaappauksia** tai tekoälyn generoimia konseptikuvia. Kuvakulmat, kamera, malli ja materiaalit pysyivät muuttumattomina. Vain valotila muuttui.

| Valaistustila | Etuviisto | Takaviisto |
| --- | --- | --- |
| **PELI** (alkuperäinen) | ![Pelin valo, etuviisto](game-front.png) | ![Pelin valo, takaviisto](game-rear.png) |
| **TASAPAINO** (uusi kokeilu) | ![Tasapainotettu valo, etuviisto](balanced-front.png) | ![Tasapainotettu valo, takaviisto](balanced-rear.png) |
| **TARKASTUS** (vanha kirkkaampi tarkastus) | ![Tarkastusvalo, etuviisto](inspection-front.png) | ![Tarkastusvalo, takaviisto](inspection-rear.png) |

### Ensimmäinen katselmointi
Tasapainotettu tila avaa moottorikehiä ja kiiltävän metallin reunoja hieman enemmän, mutta laivan varjoiset osat jäävät edelleen tummiksi. Ei lopullista valaistushyväksyntää. Erillinen Android Mobile -laitetesti tarvitaan suorituskyvyn ja mobiilin todellisen kuvan tarkistamiseen.

Kuvat tuotti [c07-a4-lighting-screenshots.yml](../../../.github/workflows/c07-a4-lighting-screenshots.yml). Kuvausparametrit, aluksen SHA256 ja renderöintialusta löytyvät [capture-manifest.json](capture-manifest.json)-tiedostosta.
