---
name: tidskoll
description: Svara på hur användaren lägger sin tid vid datorn, utifrån Tidskoll (ActivityWatch-data, blockering av sajter och valfria skärmdumpar på den egna Macen). Använd vid "/tidskoll", "vart tog tiden vägen", "hur mycket tid la jag på X", "vad gjorde jag igår", "veckorapport", "kategorisera min tid", "vad kan jag effektivisera", "analysera min skärmtid", "pausa skärmdumparna", "blockera eller öppna en sajt", eller "tidskoll dag|vecka|kategorier|analysera|effektivisera|blockera|lyft|ater|status|paus|fortsatt".
---

# Tidskoll

All data ligger lokalt på datorn. Skripten ligger i `~/tidskoll/bin/` och använder bara
Pythons standardbibliotek. Kör dem med `python3`.

| Var | Vad |
|---|---|
| ActivityWatch, `localhost:5600` | tid per app, fönstertitel, kategori och närvaro. Webbläsaradresser i bucketen `aw-watcher-tidskoll-url_<dator>` |
| `~/tidskoll/kategorier.json` | kategorireglerna som fil. De regler som faktiskt används ligger i ActivityWatch |
| `~/tidskoll/rapporter/` | veckorapporterna som HTML |
| `~/tidskoll/blocklista.txt` | sajter som blockeras i alla webbläsare när blockeringen är på |
| `~/tidskoll/skarm/dagar/<datum>/` | skärmdumpar (`HH-MM-SS.webp`) och `log.jsonl`, en rad var femte sekund: `{t, epoch, app, window, url, img}`. Hela dagsmappen raderas efter 30 dagar |
| `~/tidskoll/anteckningar/<datum>.md` | dagsanteckningar från analysen, sparas för alltid |
| `~/tidskoll/observationer.md` | återkommande mönster och hur många gånger de setts |
| `~/tidskoll/pauslista.txt` | appar och adresser där ingen skärmdump tas |

Svara på svenska, i klartext och med siffror. Hitta aldrig på en siffra: saknas data, säg det.
Läs aldrig rå `log.jsonl` eller hela API-svar i kontexten. Låt skripten räkna och läs deras JSON.

## `dag [datum]` (standard när användaren frågar om en dag)

`python3 ~/tidskoll/bin/dag.py [datum|igår]` ger aktiv tid, appar, kategorier med
underkategorier, domäner och adresser. Berätta vad dagen gick åt till, störst först. Fråga
användaren om något ser fel kategoriserat ut.

## `vecka`

`python3 ~/tidskoll/bin/veckorapport.py --oppna` skriver och öppnar rapporten. Sammanfatta
sedan med egna ord: vad som tog mest tid, vad som ändrats sedan förra veckan och en sak
som sticker ut. För frågor om en viss dag i veckan, kör `dag.py` för den dagen.

## `kategorier`

Kategorierna avgör om rapporten säger något. Målet är att under fem procent av tiden
ska hamna i "Okategoriserat" eller "Webbläsning (okategoriserad)".

1. `python3 ~/tidskoll/bin/kategorier.py exportera > ~/tidskoll/kategorier.json`, så att
   filen utgår från de kategorier som används just nu.
2. `python3 ~/tidskoll/bin/kategorier.py visa --dagar 7` visar tid per kategori och
   de största posterna utan riktig kategori.
3. Gruppera posterna och fråga användaren vad de gäller, några i taget. Fönstertitlar
   räcker sällan för att gissa vilket jobb eller projekt något hör till.
4. Skriv reglerna i `~/tidskoll/kategorier.json`. Format per kategori:
   `{"name": ["Arbete", "Kund X"], "rule": {"type": "regex", "regex": "Kund X|kundx\\.se", "ignore_case": true}, "data": {"color": "#2e8b57"}}`.
   En överkategori utan egen regel får `{"type": "none"}`.
5. Provkör: `python3 ~/tidskoll/bin/kategorier.py visa --fil ~/tidskoll/kategorier.json`.
   Läs vad som faktiskt hamnade var. En regel som ser rätt ut kan fånga för mycket.
6. När användaren godkänt: `python3 ~/tidskoll/bin/kategorier.py tillampa ~/tidskoll/kategorier.json`.
   Den sparar en kopia av de gamla kategorierna i `~/tidskoll/kategorier-backup/` först.

Så väljer ActivityWatch: regexen söks i både appnamn och fönstertitel. Den djupaste
kategorin vinner, och vid lika djup den som står sist. Därför står Konsumtion sist:
"Kurs i Excel – YouTube" ska bli Konsumtion och inte Arbete.

ActivityWatch använder Rusts regexmotor, som skiljer sig från Pythons på två punkter:
- `\|` blir ett "eller" och matchar allt. Välj en annan del av titeln.
- `\b` fungerar inte som väntat. Använd mellanslag, `^` eller `$` som ankare.

Tomma Safari-titlar uppstår medan en sida laddas. De går inte att kategorisera, så låt dem vara.

## `analysera [datum]` (kräver skärmdumpsnivån; standard: igår om det finns data, annars idag)

Metadata först, bilder sedan. Mål: 10 till 30 bilder per dag, aldrig alla.
Kan du inte öppna bildfiler: säg det, och gör analysen på loggen och tiden i steg 1 och 2.
Mönster som bara syns på bilderna (menyer, fildialoger) kommer då inte med.

1. `python3 ~/tidskoll/bin/dag.py <datum>` ger tiden per kategori och app.
2. `python3 ~/tidskoll/bin/arbetspass.py <datum>` ger arbetspassen, antalet appbyten,
   perioder med täta byten (`tata_byten`) och `bilder_att_titta_pa`, de bilder som är
   värda att titta på.
3. Öppna bara bilderna i `bilder_att_titta_pa` (`<dagmapp>/<fil>`). Leta efter konkreta tecken:
   - menyer eller högerklick där det finns ett kortkommando
   - manuellt letande i fildialoger, eller scrollning för att hitta något
   - att samma sak kopieras och klistras in mellan samma två appar, om och om igen
   - att något kollas för hand som kunde ha kommit som en notis
   - ett verktyg som är dyrare, långsammare eller äldre än alternativen
4. Skriv `~/tidskoll/anteckningar/<datum>.md`: en kort tidslinje med pass och klockslag, vad
   som gjordes, vilka verktyg som användes, och "Observerat" med bevis (bildfilernas namn).
   Notera också det som fungerar bra.
5. Uppdatera `~/tidskoll/observationer.md`. Finns mönstret redan: öka antalet med ett och
   uppdatera datumet. Annars lägg till en rad:
   `- [antal: 1, senast: 2026-10-08] Öppnar kalkylarket via Finder varje morgon; ett bokmärke eller kortkommando sparar ungefär 20 s per gång. (Sett: 2026-10-08/09-14-20.webp)`

Integritet: bilderna du öppnar skickas till leverantören av modellen du kör på. Öppna aldrig
en bild vars loggrad visar en bank, en lösenordshanterare eller annat som borde ha stått på
pauslistan. Föreslå i stället att appen eller adressen läggs till i `~/tidskoll/pauslista.txt`.

## `effektivisera [fokus]`

1. Läs `~/tidskoll/observationer.md` och de senaste sju dagarnas anteckningar.
2. Ett mönster som setts tre gånger eller fler är bekräftat. Färre än så är brus, ta inte med dem.
3. Gör varje bekräftat mönster till ett konkret förslag: det exakta kortkommandot, ett
   bättre verktyg (kontrollera med en sökning att det finns och vad det kostar i dag),
   eller en automatisering du kan bygga direkt.
4. Sortera efter hur mycket tid förslaget beräknas spara per vecka och visa de tre till fem
   största. Erbjud att bygga dem som går att automatisera.
5. Med `fokus` (till exempel "mejl" eller "webbläsare"): bara det området.

## `blockera`, `lyft <domän>`, `ater <domän>`

Blockeringen pekar sajterna i `~/tidskoll/blocklista.txt` mot 0.0.0.0 i `/etc/hosts`, så att
de inte går att öppna i någon webbläsare. Kräver att `bash installera.sh blockera` har körts.

- Läget: `bash ~/tidskoll/bin/blockera.sh status`
- Slå på eller stäng av: `bash ~/tidskoll/bin/blockera.sh pa` eller `av`
- Öppna en sajt tillfälligt: `bash ~/tidskoll/bin/blockera.sh lyft youtube.com` (gäller även
  underdomäner). Blockera den igen: `bash ~/tidskoll/bin/blockera.sh ater youtube.com`.
- Lägga till en sajt: skriv domänen i listan och kör `pa` igen. `www.` och `m.` läggs till
  automatiskt, andra underdomäner måste stå på egna rader.

Varje ändring visar macOS lösenordsruta, och användaren skriver datorns lösenord där. Be
aldrig om det i chatten. Vill användaren öppna en blockerad sajt: gör det, men säg först hur
mycket tid sajten fick de senaste sju dagarna enligt `dag.py` eller veckorapporten, så att
användaren har siffran framför sig när hen bestämmer sig.

Går en blockerad sajt ändå att öppna i Safari: kontrollera Privat reläservice (iCloud
Private Relay) först, den skickar trafiken förbi `/etc/hosts`. Flikar som redan var öppna
kan också fortsätta fungera en stund efter att blockeringen slagits på. Cmd+Q på
webbläsaren löser det.

## Dölja flöden

Skript som döljer flöden i Safari ligger i mappen `Userscripts` i iCloud Drive (eller i
`~/tidskoll/userscripts`) och körs av appen Userscripts. `linkedin-dolj-flode.user.js` döljer
flödet på LinkedIns startsida.

- Visas flödet igen: LinkedIn har troligen ändrat sidan. Öppna linkedin.com, ta reda på vilken
  del av sidan som nu innehåller flödet och uppdatera väljarna i skriptet. Bygg hellre på
  fasta märkningar som `data-testid` än på klassnamn, som LinkedIn slumpar.
- Vill användaren dölja flödet på en annan sajt: skriv en ny fil i samma mapp med LinkedIn-
  skriptet som mall. Byt `@match`, hur startsidan känns igen och vilka delar som döljs.
  Användaren behöver sedan tillåta den nya sajten i Userscripts.

## `status`, `paus`, `fortsatt`

- Läget: `bash ~/tidskoll/bin/installera.sh status`. Visar ActivityWatch, bakgrundsjobben,
  blockeringen, dagens antal skärmdumpar och de senaste felen. Är skärmdumpsjobbet igång
  men antalet bilder 0, saknas nästan alltid behörigheten att spela in skärmen.
- Pausa skärmdumparna: `bash ~/tidskoll/bin/installera.sh paus`
- Fortsätt: `bash ~/tidskoll/bin/installera.sh fortsatt`
