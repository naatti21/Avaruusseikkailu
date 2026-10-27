# C-07 A4 – automaattiset valaistuskuvat

**Godot 4.7.2 / Linux / GL Compatibility.** Nämä ovat **oikeasta GLB-3D-mallista** automaattisesti renderöidyt Godot-kuvat, **eivät Android-emulaattorin kuvankaappauksia** tai tekoälyn generoimia konseptikuvia. Kuvakulmat, kamera, malli ja materiaalit pysyivät muuttumattomina. Vain valotila muuttui.

| Valaistustila | Etuviisto | Takaviisto |
| --- | --- | --- |
| **PELI** (alkuperäinen) | ![Pelin valo, etuviisto](game-front.png) | ![Pelin valo, takaviisto](game-rear.png) |
| **TASAPAINO** (uusi kokeilu) | ![Tasapainotettu valo, etuviisto](balanced-front.png) | ![Tasapainotettu valo, takaviisto](balanced-rear.png) |
| **TARKASTUS** (vanha kirkkaampi tarkastus) | ![Tarkastusvalo, etuviisto](inspection-front.png) | ![Tarkastusvalo, takaviisto](inspection-rear.png) |
| **HERO** (vahvempi suunnattu valo) | ![Uusi HERO-valo, etuviisto](hero-front.png) | ![Uusi HERO-valo, takaviisto](hero-rear.png) |

### Ensimmäinen katselmointi
Edellinen TASAPAINO jäi liian tummaksi. HERO-testissä päävalo on selvästi vahvempi ja moottorien varjokoloa avataan tilapäisellä telakkamaisella heijastusvalolla. Valaistus on testiasetus, ei hyväksytty pelin pysyvä valaistus. Tuloksen arviointi tehdään kuvia vertaamalla. Erillinen Android Mobile -laitetesti tarvitaan suorituskyvyn ja mobiilin todellisen kuvan tarkistamiseen.

Kuvat tuotti [c07-a4-lighting-screenshots.yml](../../../.github/workflows/c07-a4-lighting-screenshots.yml). Kuvausparametrit, aluksen SHA256 ja renderöintialusta löytyvät [capture-manifest.json](capture-manifest.json)-tiedostosta.
