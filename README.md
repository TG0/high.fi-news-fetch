# High.fi news fetch

The script fetches news titles from high.fi JSON feed and creates a filtered result HTML page of the news.

The user can define how the news are filterd and if some are highlighted with a star.

Finnish introduction text below, english one coming below that later on!

## Kuvakaappaus

![kuvakaappaus](https://drive.google.com/uc?id=1OkLIB4H79W2GDugQM0D756Im4vTBgMrj)
  
  

## Yleiskuvaus

Ohjelma noutaa uutisotsikoita high.fi -sivulta ja tallettaa ne tiedostoon results.html, joka voidaan avata internetselaimella.

```
Usage: python getNews.py [-c=<haettu sivumäärä>] [-o]
```  

Oletuksena ohjelma hakee 4 sivua uutisia ja käyttäjältä kysytään, haluaako hän avata tulostiedoston selaimella.

```
Example: python getNews.py -c=3

Example: python getNews.py -c=3 -o     // avaa myös tulostiedoston selaimella
```  

  


Asetukset:
--------------

Ao. asetustiedostoille käy kokonaisen sanan lisäksi myös osa sanasta, kunhan tämä löytyy uutisotsikosta tai median nimestä.
Esim: 'moottor' suodattaa: 'moottorit', 'moottoreja', 'moottoripyörä', 'moottoriajoneuvo', jne.  

```
avoid_media.txt - määritä mediat, joiden uutiset oletuksena ohitetaan

avoid_words.txt - määritä sanat** joita havaitessa otsikossa, uutinen ohitetaan (jollei ole jo ed. säännöllä ohitettu)

exception_words.txt - määritä sanat** joita otsikosta löydettäessä uutista ei ohiteta, 2 edellisestä säännöstä huolimatta

exception_media.txt - määritä mediat joiden uutisia ei koskaan ohiteta, edellisistä säännöistä huolimatta  

```  
  
  
** Huom: jos määrität tiedostoon sanan 'seat', ohjelma hakee kuitenkin ' seat' (välilyönnillä edessä). 
Ts. sana ' useat' ei jää filtteriin kiinni. Sen sijaan ' Seat-autoilija' jää. 
Jos otsikko kuitenkin alkaa sanalla, välilyöntiä edessä ei käytetä. Esim: 'Seat ei ole auto' suodattuu pois.  


```
highlighted_media.txt - määritä ne mediat, joiden otsikkojen eteen laitetaan tähti korostukseksi

highlighted_words.txt - määritä ne sanat, joiden löytyessä otsikosta, otsikon eteen laitetaan tähti korostukseksi  

```
  
  

Tulostiedoston ulkoasun voi muuttaa muokkaamalla css-tyylitiedostoa **style.css**  
