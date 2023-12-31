# OpeApu
## Johdanto
OpeApu on Tietokannat ja Web-ohjelmointi-kurssin harjoitustyö. Sovellus on tarkoitettu peruskouluopettajan
apuvälineeksi tuntiaktiivisuus- ja kurssiarvostelujen tekemiseksi. Google Class Room on yleisesti käytössä
opettajilla, mutta siitä puuttuu ominaisuus tuntiarvostelujen syöttämiseen helposti. Sovellus on toteutettu Flaskilla.

Sovelluksen toiminnot:
* Sovellus vaatii kirjautumisen, joten sovelluksen käyttäjät ja salasanat tallennetaan yhteen tietokantatauluun
* Sovellukseen voi rekisteröityä useita käyttäjiä. Kukin käyttäjä näkee vain itse lisäämänsä oppilaat ja kurssit.
* Yläosassa on navigointipalkki: Etusivu, Oppilaat, Kurssit, Tuntiaktiivisuus, Arvosanat ja Kirjaudu ulos
* Etusivu sisältää tietoa sovelluksen toiminnoista
* Oppilaat-välilehti sisältää uuden oppilaan lisäämisen ja kaikkien oppilaiden on listauksen. Lisäksi sivulta löytyy oppilaan hakutoiminto.
* Oppilasta klikkaamalla pääsee oppilaan omalle sivulle, jossa voi tarkastella oppilaan kursseja ja tallennettuja tuntiaktivisuusmerkintöjä sekä poissaoloja. Jos oppilas ei osallistu millekään kurssille, oppilaan voi myös poistaa.
* Kurssit-sivu sisältää uuden kurssin lisäämisen. Kursseihin voi lisätä tai poistaa aiemmin luotuja oppilaita. Kurssin voi poistaa, jos sille ei osallistu yhtään oppilasta.
* Tuntiaktiivisuus-sivulla voi valita kurssin, jonka jälkeen kurssille osallistuvat oppilaat listataan ja heille voi antaa tuntiaktiivisuus arvosanan. Samalla tallentuu päivämäärä.
* Tuntiaktiivisuudelle lasketaan keskiarvo, jota voi käyttää hyväksi kurssiarvosteluvaiheessa.
* Myös poissaolot saa selville joltain päivältä puuttuvan tuntiarvostelun perusteella.
* Arvosanat-sivulla voi valita kurssin, jonka jälkeen kurssille osallistuvat oppilaat, heidän poissaolonsa ja tuntiaktiivisuuskeskiarvonsa listataan.
* Kullekin oppilaalle voi antaa kurssiarvosanan ja tallentaa sen tietokantaan.

## Sovelluksen kehitystilanne
* OpeApulle on luotu tietokantataulut: käyttäjät (users), oppilaat (students), kurssit 
(courses), tuntiaktiivisuus (activity) ja arvosanat (course_students).
* Rekisteröityminen toimii
* Kirjautuminen toimii
* Etusivu toimii
* Oppilaat-sivulla voi luoda uusia oppilaita ja luodut oppilaat listataan
* Hakutoiminnon avulla oppilaiden listausta voi rajata
* Oppilaan nimeä klikkaamalla pääsee oppilaan tarkempiin tietoihin. Kaikki kurssit, joille oppilas osallistuu näytetään taulukoina, jotka sisältävät tuntiaktiivisuusarvosanat. Näille lasketaan myös keskiarvo ja poissaolojen määrä sekä näytetään kurssiarvosana (jos annettu). 
* Oppilaan voi poistaa ellei häntä ole liitetty millekään kurssille.
* Kurssit-sivulla voi luoda uusia kursseja ja kurssit listataan
* Kunkin kurssin perässä on ominaisuus 'Näytä tiedot', joka ohjaa uudelle sivulle, jossa kurssiin voi liittää oppilaita. Jos joku oppilas on jo rekisteröitynä kurssille, valintaruutu on valmiiksi merkitty. Oppilaan voi myös poistaa kurssilta.
* Kurssin voi poistaa, jos siihen ei ole liitetty oppilaita
* Tuntiaktiivisuus-sivulla voi valita kurssin, jolloin kurssin oppilaat listataan. Oppilaille voi antaa päivittäisen aktiivisuusarvosanan ja tallentaa ne. Jättämällä kenttä tyhjäksi oppilaalle tallentuu poissaolo. Jos päivälle on jo annettu tuntiaktiivisuusarvosana, annettu arvosana on valmiiksi näkyvissä kentässä.
* Arvosanat-sivulla voi valita kurssin ja sen oppilaille voi antaa kurssiarvosanan. Tuntiaktiivisuuden keskiarvo ja poissaolot näytetään arvosanan antamisen helpottamiseksi. Jos arvosana on jo annettu, se on valmiina kentässä. Tarvittaessa arvosanaa voi myös muuttaa.
* Kirjautuminen ulos sovelluksesta toimii

Sovellus on valmis. Jatkokehitys vaatisi palautetta sovellusta käyttäviltä opettajilta, jonka jälkeen sovelluksen voisi viedä esim. fly.io:hon.

## Sovelluksen testaaminen paikallisesti
* Python3 ja PostgreSQL asennettuna
* Kloonaa repositorio:
  ```
  git clone https://github.com/Ethervortex/opeapu.git 
  ```
* Luo .env tiedosto ja sinne muuttujat DATABASE_URL ja SECRET_KEY:
  ```
  DATABASE_URL=<database-local-address> (minulla: postgresql+psycopg2:///user)
  SECRET_KEY=<your_secret_key>
  ```
* Aktivoi virtuaaliympäristö ja asenna riippuvudet:
  ```
  python3 -m venv venv
  ```
  ```
  source venv/bin/activate
  ```
  ```
  pip install -r ./requirements.txt
  ```
* Luo sovelluksen tarvitsemat taulut:
  ```
  psql < schema.sql
  ```
* Käynnistä tietokanta:
  ```
  start-pg.sh
  ```
* Käynnistä sovellus: flask run
  ```
  flask run
  ```
* Sovellus käynnistyy osoitteeseen: localhost:5000
