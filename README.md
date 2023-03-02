# Docker-application-for-Tumor-detection
Tumor detection app using: Docker, Flask, Jinja, MariaDB, and HTML, CSS, JS basics.




{%hackmd @themes/orangeheart %}

# UMS završni ispit - predviđanje tumora #
Vedran Orešković, Dominik Kinkela, Erik Bašić


## Koraci izvođenja projekta ##

#### **1. Postavljanje virtualnog okruženja u terminalu**

```shell=
conda create -n breast_cancer python=3.7
```

Stvaramo novo virtualno okruženje, dajemo mu ime breast_cancer i odabiremo python 3.7

Listu trenutnih aktivnih okruženja provjeravamo naredbom

```shell=
conda env list
```

Na izlazu dobijemo:

```shell=
conda env list
# conda environments:
#
base                  *  /home/erik/anaconda3
breast_cancer            /home/erik/anaconda3/envs/breast_cancer
```

Gdje zvjezdica označava trenutno aktivno okruženje te se moramo prebaciti na novo kreirano okruženje.

Aktiviramo okruženje sljedećom naredbom:

```shell=
conda activate breast_cancer
```

U ovom okruženju instaliramo Pandas:
```shell=
pip install pandas
```

Te ponavljamo isto za sklearn i seaborn matplotlib.

```shell=
pip install sklearn
pip install seaborn matplotlib
```
Trenutne biblioteke koje koristi naše virtualno okruženje možemo pregledati sljedećom naredbom:

```shell=
conda list
```

#### **2. Pokretanje breast cancer modela**

Potrebno je instalirati Jupyter notebook, to radimo sljedećom naredbom:
```shell=
pip install jupyter notebook
```

Lokalno pokrećemo Jupyter notebook naredbom:
```shell=
jupyter notebook
```

Dobivamo sučelje u kojem lokalno možemo pokretati ipynb datoteke. 

![](https://i.imgur.com/aMgxKur.png)

Model koji ćemo koristiti u aplikaciji zove se breastCancer.ipynb. To je model koji prima veliku količinu parametara te na izlazu daje rezultat radi li se o benignom ili malicioznom tumoru. Prima parametre poput polumjera, teksture, perimetre, površine, glatkoće, kompaktnosti, konkavnosti, simetrije i fraktalne dimenzije.

Pokrećemo svaku čeliju u modelu koristeći Shift i Enter. Ispisom matrice konfuzije možemo vidjeti da model ima visoku preciznost od čak 98%.

Model stvara datoteke *model.pkl* i *scale.pkl* koji će nam služiti u aplikaciji. *model.pkl* prikazuje vrijednost modela od 0 do 1 u decimalnom zapisu. *scale.pkl* zaokružuje vrijednost na 0 ili 1, ovisno o tome gdje je rezultat bliži.


#### **3. Dockerfile**

Prije pokretanja aplikacije potrebno je napraviti Dockerfile u kojemu se nalaze instrukcije za stvaranje Docker image-a.
Naš Dockerfile:
```dockerfile=
FROM python:3.7.9

WORKDIR /app

RUN pip install requests==2.26.0 SQLAlchemy==1.3.24 PyMySQL==0.9.3 itsdangerous==1.1.0 certifi==2020.6.20 click==7.1.2 Flask==1.1.4 Jinja2==2.11.2 joblib==0.17.0 MarkupSafe==1.1.1 numpy==1.19.3 pandas==1.1.4 scikit-learn==0.23.2 scipy==1.5.3 sklearn==0.0

ENTRYPOINT ["python"]

CMD ["app.py"]

```

U prvoj liniji definiramo osnovni image koji ćemo koristiti kako bi stvorili kontejner. U ovom slučaju radi se o Python-u 3.7.9 
U drugoj liniji postavljamo direktorij u kojemu će se nalaziti aplikacija. 
U trećoj liniji pokreće se instalacija svih potrebnih Python paketa koristeći *pip*. Također su specificirane i verzije. 
U liniji ENTRYPOINT postavljamo komandu koju koristimo prilikom pokretanja kontejnera. 
U liniji CMD postavljamo program koji će se pokretati kada pokrećemo kontejner.

Kako bi pokrenuli Dockerfile potrebno je pozicionirati se u direktorij u kojem se nalazi. Zatim pokrećemo naredbu:

```shell=
docker build -t breast_cancer_class:1.0 .
```
Koristeći docker build stvaramo docker image naziva `breast_cancer_class`. Parametar -t je zapravo oznaka --tag te ovom image-u dodjeljujemo tag 1.0. 
`.` na kraju označava da image pokrećemo u trenutnom direktoriju.

Listu trenutnih docker image-a možemo provjeriti korištenjem naredbe
```shell=
docker images
```
Ili korištenjem aplikacije "Docker Desktop":

![](https://i.imgur.com/ZPqj0t5.png)

#### **4. Docker compose**

U docker compose datoteci definiramo sve kontejnere koje ćemo koristiti prilikom pokretanja aplikacije. Docker compose je `yml` oblika.

Naša docker-compose.yml datoteka:
```yml=
version: '3'
services:
  app:
    image: breast_cancer_class:1.0
    container_name: app
    ports:
      - "5000:5000"
    networks:
      - my-network
    depends_on:
      - db
    volumes:
      - .:/app
  db:
    image: mariadb
    environment:
      - MYSQL_DATABASE=bazaTumori
      - MYSQL_USER=vedran99
      - MYSQL_PASSWORD=vedran99
      - MYSQL_ROOT_PASSWORD=vedran99
    ports:
      - "3306:3306"
    networks:
      - my-network
    volumes:
      - db_data:/var/lib/mysql
networks:
  my-network:
    driver: bridge
volumes:
  db_data:
```

U prvoj liniji postavljamo verziju na `3`.
Zatim definiramo sve servise koje ćemo koristiti u aplikaciji. Naša aplikacija sastojati će se od kontejnera `app` i `db`.

U servisu `app` postavljamo prvi kontejner koji ćemo koristiti. Koristimo image koji smo prethodno izgradili u Dockerfile datoteci; `breast_cancer_class:1.0`. Ime kontejnera postavljamo na `app` a port kontejera postavljamo na 5000. Kontejner zatim spajamo u mrežu `my-network`. Postavljamo i ovisnost o drugom kontejneru (u ovom slučaju `db`) što znači da se `app` kontejner pokreće tek nakon što je `db` kontejner uspješno pokrenut. U `volumes` spajamo trenutni direktorij s `app` direktorijem unutar kontejnera.

U servisu `db` postavljamo drugi kontenjer. Ovaj kontejner je baza podataka u kojoj ćemo zapisivati sve upite i rezultate upita. Koristimo bazu MariaDB. U image dijelu koristimo službeni Docker image `mariadb` U enviromenut postavljamo ime baze, ime korisnika, password i root password. Port ovog kontejnera je 3306. Kontejner spajamo u mrežu `my-network`. Zatim stvaramo volume `db_data` koji spajamo na `/var/lib/mysql` unutar kontejnera.

Uz servise potrebno je definirati i network. Stvaramo mrežu `my-network` te kao driver postavljamo `bridge` kako bi ovi servisi mogli komunicirati.

U zadnjem djelu definiramo `volume` koji koristi naša baza podataka. 

Kako bi pokrenuli docker compose datoteku koristimo sljedeću naredbu:
```shell=
docker compose up
```

Ukoliko je došlo do problema docker compose naredba će izbaciti grešku. Listu trenutno aktivnih kontejnera možemo provjeriti naredbom 
```shell=
docker ps
```

Te dobijemo ispis aktivnih kontenjera:
![](https://i.imgur.com/0pUsFHv.png)


Također, istu stvar možemo vidjeti i u Docker Desktop aplikaciji

![](https://i.imgur.com/mnMoGR9.png)

#### **5. app.py**

Slijedi opis programa app.py koji prihvaća parametre sa sučelja, šalje ih u pkl datoteke te vraća predikciju nazad na sučelje.

```python=
import pandas as pd
from flask import Flask, jsonify, request, render_template, redirect, url_for
import requests
import joblib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
import time
import logging
```

Importanje biblioteka. 

```python=
app = Flask(__name__)

engine = create_engine('mysql+pymysql://vedran99:vedran99@db:3306/bazaTumori')
Session = sessionmaker(bind=engine)
Base = declarative_base()
```
Stvaramo Flask instancu aplikacije. Zatim se spajamo na bazu koristeći `create_engine` funkciju sqlalchemy-a. Potrebno je unijeti prethodno definirano korisničko ime, lozinku, port,, naziv servisa i naziv baze kako bi se uspješno spojili na bazu. Zatim stvaramo sesiju pomoću koje ćemo izvoditi operacije nad bazom. 


```python=
class RequestLog(Base):
    __tablename__ = 'request_log'
    id = Column(Integer, primary_key=True)
    request_time = Column(DateTime, default=None)
    calculation_time = Column(Integer, default=None)
    prediction_label = Column(String(length=12), default=None)
```

U klasi RequestLog stvaramo tablicu u kojoj ćemo vršiti zapise. Prvo dodjeljujemo ime tablici koristeći `__tablename__`. Definiramo stupac `id` koji će nam predsatvljati redni broj upita u bazi, postavljamo ga kao integer i kao primarni ključ tablice. Stupac `request_time` predstavlja vrijeme u kojem je korisnik poslao upit modelu. Stupac `calculation_time` predstavlja vrijeme koje je bilo potrebno modelu kako bi izveo predikciju. To vrijeme je iskazano u mikrosekundama. Stupac `prediction_label` predstavlja rezultat predviđanja modela, u slučaju ovog modela to će biti benigni ili maliciozni tumor. 

```python=
@app.route('/predictJson', methods=['POST'])
def predict():
    req = request.get_json()
    input_data = req['data']

    input_data_df = pd.DataFrame.from_dict(input_data)

    model = joblib.load('model.pkl')

    scale_obj = joblib.load('scale.pkl')

    input_data_scaled = scale_obj.transform(input_data_df)

    prediction = model.predict(input_data_scaled)

    if prediction[0] == 1:
        cancer_type = 'Malignant'
    else:
        cancer_type = 'Benign'

    return jsonify({'output': {'cancer_type': cancer_type}})
```

U ovom djelu koda nalazi se metoda predictJson. Koristi metodu POST jer na kraju funkcije vraća rezultat u JSON body-u. Metoda kreće definiranjem funkcije predict koja prima parametre. `req` prima podatke poslane POST naredbom u obliku JSON objekta. Zatim izvlačimo ključ `data` iz JSON objekta te dictionary spremamo u varijablu `input_data`. U sljedećem koraku dictionary pretvaramo u Pandas dataframe. Slijedi učitavanje *model.pkl* i *scale.pkl* datoteke. Dataframe se prvo skalira korištenjem `scale_obj.transform()` metode. Zatim se ti sklairani podaci šalju na *model.pkl* koji predviđa vrstu tumora. Ukoliko je predviđanje jednako 1 tada model tvrdi da se radi o malicioznom tumoru a ukoliko je 0  tada se radi o benignom tumoru. Funkcija vraća rezultat predviđanja u JSON formatu koristeći jsonify funkciju. 

```python=
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        dbQuery = session.query(RequestLog).all()
        db = []
        for row in dbQuery:
            d = {}
            for column in row.__table__.columns:
                d[column.name] = str(getattr(row, column.name))
            db.append(d)
        # app.logger.info(db)

        return render_template('index.html', db=db)
```

Prikazan je prvi dio home metode. Kada korisnik pošalje GET zahtjev home stranici, server dohvaća sve zapise iz RequestLog tablice. U varijabli `db` spremiti će se formatirani redovi tablice. Slijedi for petlja u kojoj definiramo novu varijablu d. Zatim dinamički dohvaćamo vrijednost svakog stupca. Slijedi učitavanje index.html-a na kojem je prikazana i tablica upita i rezultata.

```python=
 else:
        request_time = datetime.utcnow()
        start_time = time.perf_counter()

        mean_radius = request.form.get('mean radius')
        mean_texture = request.form.get('mean texture')
        mean_perimeter = request.form.get('mean perimeter')
        ...
        
```
Ukoliko korisnik pošalje POST zahtjev tada ulazimo u else dio petlje. Korisnik upisuje parametre te tada započinje mjerenje vremena. U varijabli `request_time` bilježimo trenutak slanja upita. Također počinje i mjerenje vremena izvođenja koje spremamo u varijablu `start_time`. S html-a dohvaćamo redom parametre koristeći `request.form.get()` funkciju. 

```python=
  obj = {
                "data": [
                    {
                        "mean radius": mean_radius,
                        "mean texture": mean_texture,
                        "mean perimeter": mean_perimeter,
                        "mean area": mean_area,
                        "mean smoothness": mean_smoothness,
                        ...
                        
```

Dohvaćene parametre spremamo u JSON body format koji spremamo u `obj` varijablu.

```python=
        res = requests.post('http://app:5000/predictJson', json=obj, headers={'Content-Type': 'application/json'})

        cancer = res.json()['output']['cancer_type']

        end_time = time.perf_counter()
        calculation_time = int((end_time - start_time) * 1000000)
        request_log = RequestLog(request_time=request_time, calculation_time=calculation_time, prediction_label=cancer)
        session.add(request_log)
        session.commit()

        return render_template('prediction.html', cancer=cancer)
```

Stvaramo POST zahtjev u kojem šaljemo JSON body u `predictJson` metodu. U `cancer` varijabli spremamo output predictJson metode. Nakon toga u varijablu `end_time` spremamo vrijeme kraja izvođenja predikcije. Slijedi izračun trajanja predikcije koji je kranje vrijeme oduzeto sa početnim vremenom. Podatke zatim spremamo u bazu koristeći `RequestLog` te commitamo promjene. Nakon toga učitavamo prediction.html u kojemu korisniku prikazujemo rezultat predikcije.

```python=
if __name__ == '__main__':
    Base.metadata.create_all(engine)
    session = Session()
    app.run(host='0.0.0.0', port='5000', debug=True)
```

U ovom djelu koda `metadata.create.all(engine)` kreira instancu baze i sve tablice. Zatim kreira i sesiju. `app.run` je Flask development server koji se inicijalizira. Debug omogućuje pregled napredne konzole pomoću generiranog pina za pregled stanja. 



#### **6. Pristup MariaDB bazi**

Ulaz u docker konjetenjer sa bazom (koji sadrži bazu)


```shell=
docker exec -it <ID db-1 docker containera> bash
``` 

Uspješno ste ušli u shell baze. Sada je potrebno ući u MarijaDB

```shell=
root@7b5d6b0e136e:/# mysql -h db -u vedran99 -pvedran99 bazaTumori
```

Ispis tablice:

```shell=
MariaDB [bazaTumori]> select * from request_log;
```

Ispis tablice:

![](https://i.imgur.com/gWHTGr5.png)


#### **7. Izgled sučelja**

![](https://i.imgur.com/wwUZm6o.png)

Prikazano je sučelje u kojem korisnik unosi sve parametre. Nakon što je korisnik unjeo parametre potrebno je stisnuti dugme "Predict". Sa desne strane nalazi se prikaz tablice iz RequestLog baze. 

![](https://i.imgur.com/tE5L2F1.png)

Ovisno o predikciji prikazati će se različite stranice. 


