# Tics-katalog

Ord och vändningar som lätt blir slentrian i svensk prosa, oavsett genre. `bok tics` räknar dem per kapitel och för hela boken. En träff är ingen dom: den är en fråga till texten. Bokens egna tics läggs i `bok/tics-tillagg.md`.

Format, en per rad: `namn | reguljärt uttryck | tak | kommentar`. Tak: `kapitel=N` (per kapitel), `bok=N` (hela boken), båda kommaseparerade, eller `-`. `kapitel=0` betyder att varje träff ska bort. Sökningen är skiftlägesokänslig och görs rad för rad.

```tics
nickade | \bnickade\b | kapitel=2 | Kroppsspråk i stället för reaktion. Låt repliken eller handlingen bära.
ryckte på axlarna | \bryckte på axlarna\b | kapitel=1 | Samma problem som nickade.
log | \b(log|smålog)\b | kapitel=3 | Ett leende ska betyda något.
suckade | \bsuckade\b | kapitel=1 | Sällan nödvändigt.
som om | \bsom om\b | kapitel=2 | Liknelseprefix som lätt blir vana.
plötsligt | \b(plötsligt|helt plötsligt)\b | kapitel=1, bok=10 | Plötsligheten ska märkas i rytmen, inte sägas.
började | \bbörjade (att )?[a-zåäö]+a\b | kapitel=3 | Låt handlingen börja direkt: hon sprang, inte hon började springa.
kände | \b(kände sig|kände hur)\b | kapitel=3 | Visa känslan genom kropp och handling.
tystnad | \b(det blev tyst|tystnaden|tystnade)\b | kapitel=1 | Tystnad som effekt slits snabbt.
andetag | \b(drog efter andan|tog ett djupt andetag|höll andan)\b | kapitel=1 | Andning som känslomarkör.
hjärtat | \bhjärtat (slog|bultade|hamrade|rusade)\b | kapitel=1 | Kliché för rädsla och förälskelse.
blicken | \bblick(en|ade)\b | kapitel=3 | Ögon som gör allt arbete.
utfyllnad | \b(på något sätt|på sätt och vis|liksom|faktiskt|egentligen)\b | kapitel=4 | Stryk om meningen klarar sig utan.
berättaren förklarar | ^(Sanningen var att|Faktum är att|I efterhand|Det fanns en tid då) | kapitel=0 | Författaren som förklarar. Stryk.
aforism i tanke | \b(Det enda som|Sanningen om|är värre än)\b | kapitel=0 | Visdomsord i en karaktärs tanke låter som författaren.
anglicism | \b(literally|basically|whatever)\b | kapitel=0 | Bara i repliker där personen faktiskt pratar så.
tre ord med bindestreck | [a-zåäö]+-[a-zåäö]+-[a-zåäö]+ | - | Ofta påhittade sammansättningar. Kontrollera mot SAOL.
```
