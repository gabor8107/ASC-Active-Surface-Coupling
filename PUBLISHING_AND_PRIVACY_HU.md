# Feltöltési útmutató – ASC v0.6 PUBLIC

A ZIP a GitHubra feltölthető **fájlokat és mappákat** tartalmazza; a ZIP-et önmagában **ne** töltsd fel a repóba egyetlen fájlként. Kibontás után a tartalmat másold a meglévő nyilvános ASC-repozitórium gyökerébe, az azonos fájlnevek és mappák tudatos ellenőrzésével.

**Mit tartalmaz:** 28 oldalas publikus Preprint 0.2; a helyesen ASC-001, ASC-002, ASC-003 számozott három koncepciórajz; a v0.5 számítási mappa; az új v0.6 21 oldalas angol PDF, 7 ábra, 7 CSV eredménytábla, kód, tesztek és a felhasznált feltételezések JSON-fájlja.

**Mit NEM tartalmaz:** bizalmas v0.3 ZIP, az 1000+ oldalas belső dokumentáció, tényleges transzducer-kiosztás, vezérlési beállítások, titkos gyártási terv, API-kulcsok vagy jelszavak.

**Az első lépés legyen a jogi/IP-ellenőrzés.** Egy már publikált műszaki részlet későbbi szabadalmaztathatósága korlátozott lehet. A 288 cella kizárólag feltételezett számlálási példa: amennyiben ez valódi nem nyilvános paraméterre utalna, publikálás előtt módosítsd egy ettől független, illusztratív számra. A LICENSE_DECISION.md miatt jelenleg ne nevezd open source kiadásnak.

**A PDF fő üzenete:** fizikailag számolható, hogy mekkora hatásfok-javulás kellene a szektorált rendszer önköltségének ellensúlyozásához; ezt a javulást az ASC jelenleg még nem bizonyítja. A 100 000 és 300 000 km/h számok csak klasszikus elektromos rakétaegyenletből származó feltételes sebességváltozási példák.

**Zenodo:** a korábbi Preprint 0.2 DOI-ját nem írja felül ez a dokumentum. Az új v0.6 PDF külön kiegészítőként hivatkozható, szükség esetén később külön verzióval és DOI-val.

**GitHub ellenőrzés:** felmásolás után nézd meg, hogy a `numerical_envelope_v0.6/docs/ASC_Public_Engineering_Research_v0.6_EN.pdf` megnyílik-e, a `figures/` és `results/` mappák láthatók-e, és a README összes linkje működik-e. A CI-ellenőrzés az új tesztcsomagot futtatja.
