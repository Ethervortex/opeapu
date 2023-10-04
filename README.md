# OpeApu
## Johdanto
OpeApu on Tietokannat ja Web-ohjelmointi-kurssin harjoitustyö. Sovellus on tarkoitettu peruskouluopettajan
apuvälineeksi tuntiaktiivisuus- ja kurssiarvostelujen tekemiseksi. Google Class Room on yleisesti käytössä
opettajilla, mutta siitä puuttuu ominaisuus tuntiarvostelujen syöttämiseen helposti. Sovellus on toteutettu Flaskilla.

Sovelluksen toiminnot:
* Sovellus vaatii kirjautumisen, joten sovelluksen käyttäjät ja salasanat tallennetaan yhteen tietokantatauluun
* Yläosassa on navigointipalkki: Etusivu, Oppilaat, Kurssit, Tuntiaktiivisuus, Arvosanat ja Kirjaudu ulos
* Etusivu sisältää tietoa sovelluksen toiminnoista
* Oppilaat-välilehti sisältää uuden oppilaan lisäämisen ja kaikkien oppilaiden on listauksen. Oppilasta klikkaamalla pääsee oppilaan omalle sivulle, jossa voi tarkastella oppilaan kursseja ja tallennettuja tuntiaktivisuusmerkintöjä sekä poissaoloja.
* Kurssit-sivu sisältää uuden kurssin (tai ryhmän) lisäämisen. Kursseihin voi lisätä tai poistaa aiemmin luotuja oppilaita
* Tuntiaktiivisuus-sivulla voi valita kurssin, jonka jälkeen kurssille osallistuvat oppilaat listataan ja heille voi antaa tuntiaktiivisuus arvosanan. Samalla tallentuu päivämäärä.
* Tuntiaktiivisuudelle voi laskea keskiarvon, jota voi käyttää hyväksi kurssiarvosteluvaiheessa.
* Myös poissaolot saa selville joltain päivältä puuttuvan tuntiarvostelun perusteella.
* Arvosanat-sivulla voi valita kurssin, jonka jälkeen kurssille osallistuvat oppilaat, heidän poissaolonsa ja tuntiaktiivisuuskeskiarvonsa listataan.
* Kullekin oppilaalle voi antaa kurssiarvosanan ja tallentaa sen tietokantaan.

## Sovelluksen kehitystilanne
* OpeApulle on luotu tietokantataulut: käyttäjät (users), oppilaat (students), kurssit 
(courses), tuntiaktiivisuus (activity) ja arvosanat (course_students).  
* Sovelluksen luonne ei salli kenen tahansa rekisteröitymistä, joten uusia käyttäjiä ei voi luoda kirjautumissivulla. Yksi testikäyttäjä
sovellukselle luodaan koodissa (Käyttäjätunnus: 'testiope', Salasana: 'salasana')
* Kirjautuminen toimii
* Etusivu toimii
* Oppilaat-sivulla voi luoda uusia oppilaita ja luodut oppilaat listataan
* Oppilaan nimeä klikkaamalla pääsee oppilaan tarkempiin tietoihin. Kaikki kurssit, joille oppilas osallistuu näytetään taulukoina, jotka sisältävät tuntiaktiivisuusarvosanat. Näille lasketaan myös keskiarvo ja poissaolojen määrä. 
* Oppilaan voi poistaa ellei häntä ole liitetty millekään kurssille.
* Kurssit-sivulla voi luoda uusia kursseja ja kurssit listataan
* Kunkin kurssin perässä on ominaisuus 'Lisää oppilaita', joka ohjaa uudelle sivulle, jossa kurssiin voi liittää oppilaita (toimii)
* Tuntiaktiivisuus-sivulla voi valita kurssin, jolloin kurssin oppilaat listataan. Oppilaille voi antaa päivittäisen aktiivisuusarvosanan ja tallentaa ne. Jättämällä kenttä tyhjäksi oppilaalle tallentuu poissaolo. Sivu toimii, mutta testit kesken.
* Arvosanat-sivu melko hyvässä vaiheessa: kurssin voi valita ja oppilaalle voi antaa kurssiarvosanan. Tuntiaktiivisuuden ja poissaolojen näyttäminen kuitenkin puuttuu
* Kirjautuminen ulos sovelluksesta toimii

Puuttuvia toiminnallisuuksia on siis ainakin tuntiaktiivisuuden keskiarvon näyttö Arvosanat-sivulla, mahdollisuus kurssien poistamiseen, yksittäisen oppilaan tiedot (kurssiarvosanat ja tuntiaktiivisuus), virheentarkistuksia,
ulkoasua ja muuta hienosäätöä.

## OpeApun testaaminen
* Kloonaa repositorio
* Asenna PostgreSQL
* Luo .env tiedosto ja sinne muuttujat DATABASE_URL ja SECRET_KEY
* Asenna riippuvudet: pip install -r requirements.txt
* Käynnistä tietokanta
* Luo sovelluksen tarvitsemat taulut: psql < schema.sql
* Tarvittaessa voi luoda testidataa (10 oppilasta ja 2 kurssia): psql < test_data.sql
* Käynnistä sovellus: flask run
* Sovellus käynnistyy osoitteeseen: localhost:5000
* Kirjautuminen (ominaisuus poistettaisiin jos joku oikeasti käyttäisi sovellusta): testiope: salasana
