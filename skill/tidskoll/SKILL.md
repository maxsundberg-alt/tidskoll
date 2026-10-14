---
name: tidskoll
description: Svara på hur användaren lägger sin tid vid datorn, utifrån Tidskoll (ActivityWatch-data och valfria skärmdumpar på den egna Macen). Använd vid "/tidskoll", "vart tog tiden vägen", "hur mycket tid la jag på X", "vad gjorde jag igår", "veckorapport", "kategorisera min tid", "vad kan jag effektivisera", "analysera min skärmtid", "pausa skärmdumparna", eller "/tidskoll dag|vecka|kategorier|analysera|effektivisera|status|paus|fortsatt".
---

# Tidskoll

All data ligger lokalt på datorn. Skripten ligger i `~/tidskoll/bin/` och använder bara
Pythons standardbibliotek. Kör dem med `python3`.

| Var | Vad |
|---|---|
| ActivityWatch, `localhost:5600` | tid per app, fönstertitel, kategori, borta-tid. Webbläsaradresser i bucketen `aw-watcher-tidskoll-url_<dator>` |
| `~/tidskoll/kategorier.json` | kategorireglerna som fil. Det som körs ligger i ActivityWatch |
| `~/tidskoll/rapporter/` | veckorapporterna som HTML |
| `~/tidskoll/skarm/days/<datum>/` | skärmdumpar (`HH-MM-SS.webp`) och `log.jsonl`, en rad var femte sekund: `{t, epoch, app, window, url, img}`. Bilderna rensas efter 30 dagar |
| `~/tidskoll/anteckningar/<datum>.md` | dagsanteckningar från analysen, sparas för alltid |
| `~/tidskoll/observationer.md` | återkommande mönster med antal gånger de setts |
| `~/tidskoll/pauslista.txt` | appar och adresser där ingen skärmdump tas |

Svara på svenska, i klartext och med siffror. Hitta aldrig på en siffra: saknas data, säg det.
Läs aldrig rå `log.jsonl` eller hela API-svar i kontext. Låt skripten räkna och läs deras JSON.

## `dag [datum]` (standard när användaren frågar om en dag)

`python3 ~/tidskoll/bin/dag.py [datum|igår]` ger aktiv tid, appar, kategorier med
underkategorier, domäner och adresser. Berätta vad dagen gick åt till, i den ordning
tiden faktiskt fördelades. Fråga användaren om något ser fel kategoriserat ut.

## `vecka`

`python3 ~/tidskoll/bin/veckorapport.py --oppna` skriver och öppnar rapporten. Sammanfatta
sedan med egna ord: vad som tog mest tid, vad som ändrats mot förra veckan, och en sak
som sticker ut. För frågor om en viss dag i veckan, kör `dag.py` på den dagen.

## `kategorier`

Kategorierna avgör om rapporten säger något. Målet är att under fem procent av tiden
ska hamna i "Okategoriserat" eller "Webbläsning (oklassad)".

1. `python3 ~/tidskoll/bin/kategorier.py visa --dagar 7` visar tid per kategori och
   de största posterna utan riktig kategori.
2. Gruppera posterna och fråga användaren vad de gäller, några i taget. Fönstertitlar
   räcker sällan för att gissa vilket jobb eller projekt något hör till.
3. Skriv reglerna i `~/tidskoll/kategorier.json`. Format per kategori:
   `{"name": ["Arbete", "Kund X"], "rule": {"type": "regex", "regex": "Kund X|kundx\\.se", "ignore_case": true}, "data": {"color": "#2e8b57"}}`.
   En förälder utan egen regel får `{"type": "none"}`.
4. Provkör: `python3 ~/tidskoll/bin/kategorier.py visa --fil ~/tidskoll/kategorier.json`.
   Läs vad som faktiskt hamnade var. En regel som ser rätt ut kan fånga för mycket.
5. När användaren godkänt: `python3 ~/tidskoll/bin/kategorier.py tillampa ~/tidskoll/kategorier.json`.
   Den sparar en kopia av de gamla kategorierna i `~/tidskoll/kategorier-backup/` först.

Så väljer ActivityWatch: regexen söks mot både appnamn och fönstertitel. Djupaste
kategorin vinner, vid lika djup den som står sist. Därför står Konsumtion sist:
"Kurs i Excel – YouTube" ska bli Konsumtion och inte Arbete.

Fällor i ActivityWatchs regexmotor (Rust, inte Python):
- `\|` blir ett "eller" och matchar allt. Välj en annan del av titeln.
- `\b` fungerar inte som väntat. Använd mellanslag, `^` eller `$` som ankare.
- Tomma Safari-titlar uppstår medan en sida laddar. De går inte att kategorisera, låt dem vara.

## `analysera [datum]` (kräver skärmdumpsnivån; standard: igår om det finns data, annars idag)

Metadata först, bilder sedan. Mål: 10 till 30 bilder per dag, aldrig alla.

1. `python3 ~/tidskoll/bin/dag.py <datum>` ger tiden per kategori och app.
2. `python3 ~/tidskoll/bin/block.py <datum>` ger arbetspass, appbyten, perioder med
   täta byten (`churn_bursts`) och `frames_to_view`, bilderna värda att titta på.
3. Öppna bara bilderna i `frames_to_view` (`<day_dir>/<fil>`). Leta efter konkreta tecken:
   - menyer eller högerklick där ett kortkommando finns
   - manuell navigering i fildialoger, handscrollning för att hitta något
   - samma kopiera och klistra in mellan samma två appar, om och om igen
   - att gå in och kolla något för hand som kunde komma som notis
   - ett verktyg som är dyrare, långsammare eller äldre än alternativen
4. Skriv `~/tidskoll/anteckningar/<datum>.md`: kort tidslinje med pass och klockslag, vad
   som gjordes, vilka verktyg som användes, och "Observerat" med bevis (bildfilnamn).
   Notera också det som fungerar bra.
5. Uppdatera `~/tidskoll/observationer.md`. Finns mönstret redan: räkna upp och byt datum.
   Annars lägg till en rad:
   `- [antal: 1, senast: 2026-10-08] Öppnar kalkylarket via Finder varje morgon; ett bokmärke eller kortkommando sparar ungefär 20 s per gång. (Sett: 2026-10-08/09-14-20.webp)`

Integritet: bilderna du öppnar skickas till Anthropic. Öppna aldrig en bild vars
loggrad visar bank, lösenordshanterare eller annat som borde ha stått på pauslistan.
Föreslå i stället att raden läggs till i `~/tidskoll/pauslista.txt`.

## `effektivisera [fokus]`

1. Läs `~/tidskoll/observationer.md` och de senaste sju dagarnas anteckningar.
2. Ett mönster med antal 3 eller mer är bekräftat. Lägre antal är brus, ta inte med dem.
3. Gör varje bekräftat mönster till ett konkret förslag: det exakta kortkommandot, ett
   bättre verktyg (kontrollera med en sökning att det finns och vad det kostar i dag),
   eller en automation du kan bygga direkt.
4. Sortera efter uppskattad tid sparad per vecka och visa de tre till fem största.
   Erbjud att bygga dem som går att automatisera.
5. Med `fokus` (till exempel "mejl" eller "webbläsare"): bara det området.

## `status`, `paus`, `fortsatt`

- Status: `for l in webblasare veckorapport skarm nattanalys; do printf '%s: ' $l; launchctl print gui/$(id -u)/com.tidskoll.$l 2>/dev/null | grep -m1 'state =' || echo 'inte installerad'; done`,
  plus `curl -s localhost:5600/api/0/info`, dagens antal bilder och `tail -5 ~/tidskoll/skarm/daemon.log`.
  0 bilder fast skärmjobbet kör betyder nästan alltid att behörigheten för skärminspelning saknas.
- Paus: `launchctl bootout gui/$(id -u)/com.tidskoll.skarm`
- Fortsätt: `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.tidskoll.skarm.plist`
