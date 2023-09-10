# Opeapu
Opeapu on Tietokannat ja Web-ohjelmointi-kurssin harjoitustyö. Sovellus on tarkoitettu peruskouluopettajan
apuvälineeksi etenkin tuntiaktiivisuusarvostelujen tekemiseksi. Google Class Room on yleisesti käytössä
opettajilla, mutta siitä puuttuu ominaisuus tuntiarvostelujen syöttämiseen helposti.

Sovellus vaatii kirjautumisen, joten sovelluksen käyttäjät ja salasanat täytyy tallettaa yhteen tietokantatauluun.
Muita sovelluksen toiminnallisuuksia on uuden oppilaan lisääminen ja kaikkien oppilaiden listaus omalla sivullaan. 
Omalla sivullaan on myös kurssien (tai ryhmien) lisääminen. Ryhmiin voi lisätä tai poistaa aiemmin luotuja 
oppilaita. Tämän lisäksi on tuntiarvostelu omalla sivullaan, jossa voi valita kurssin, jolloin kurssin 
oppilaat listataan ja kunkin oppilaan perässä on kenttä, johon voi kirjata tuntiarvostelun (arvosana 4-10). 
Tallennusnapilla kaikkien oppilaiden tuntiarvostelut tallentuvat tietokantaan. Samalla tallentuu päivämäärä.
Poissaolot saa myös jälkikäteen selville puuttuvan tuntiarvostelun perusteella.

Kurssin arvosanan voi antaa omalla sivullaan. Tällä sivulla oppilaiden listauksen perään voi laskea myös 
tuntiaktiivisuusarvosanojen keskiarvon sekä poissaolojen lukumäärän.

Harkinnan alla sovellukseen on vielä lisäksi viestisivu ja onko sovellus vain opettajan käyttöön. Jos oppilaille 
sallitaan myös kirjautuminen, niin tällöin oppilas pääsee vain omiin tietoihinsa käsiksi.

Tarvittavia tietokantatauluja sovelluksessa ovat siis ainakin Käyttäjät (Users), Oppilaat (Students), Kurssit 
(Courses), Tuntiaktiivisuus (Activity) ja Arvosanat (Grades). Mahdollisesti myös Viestit (Notes).
