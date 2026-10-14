# Tidskoll — instruktioner till Claude

Du hjälper någon att sätta upp Tidskoll på sin Mac. Användaren har öppnat den här mappen
i Claude Code och vill veta hur hen lägger sin tid vid datorn. Hen behöver inte kunna
programmera. Förklara vad som händer i klartext, och kör alla kommandon själv.

Läs `README.md` för vad Tidskoll är. Den här filen beskriver hur du installerar.

## Innan du börjar

Kontrollera att det är en Mac (`uname` ger `Darwin`). Tidskoll fungerar inte på Windows
eller Linux. Säg det i så fall och avbryt.

Fråga sedan användaren, i ett och samma meddelande:

1. **Vilken nivå?** Grundnivån mäter tid per app, fönster, webbsida och kategori, och ger
   en veckorapport. Skärmdumpsnivån tar dessutom en bild av skärmen var femte sekund, så
   att du kan se hur hen arbetar och föreslå förbättringar. Rekommendera grundnivån först.
   Skärmdumparna kan läggas till senare.
2. **Om skärmdumpar:** förklara rakt att allt på skärmen fotas, även privata meddelanden,
   och att bilderna stannar på datorn. Undantaget är de 10 till 30 bilder per dag som du
   tittar på vid en analys. De skickas till Anthropic. Pauslistan stoppar bilder från
   banker, lösenordshanterare och betalsidor från början. Fråga om något mer ska läggas till.
3. **Har hen redan ActivityWatch?** Har hen egna kategorier där ska de inte skrivas över
   utan att hen sagt ja.

## Installera grundnivån

Kör `bash installera.sh bas` i den här mappen. Skriptet:
- installerar ActivityWatch med Homebrew om den saknas (finns inte Homebrew: be användaren
  ladda ner från https://activitywatch.net/downloads/, eller installera Homebrew först),
- startar ActivityWatch och lägger den bland inloggningsobjekten,
- kopierar skripten till `~/tidskoll/bin/` och startindelningen till `~/tidskoll/kategorier.json`,
- startar webbläsarbevakaren och schemalägger veckorapporten (söndag 20:00),
- installerar skillen `/tidskoll` i `~/.claude/skills/tidskoll/`.

Kategorier: har användaren inga egna kategorier i ActivityWatch, kör
`python3 ~/tidskoll/bin/kategorier.py tillampa ~/tidskoll/kategorier.json`. Den gamla
uppsättningen sparas först i `~/tidskoll/kategorier-backup/`.

Om macOS stoppar ActivityWatch första gången ("kan inte öppnas"): be användaren öppna
Systeminställningar → Integritet och säkerhet och klicka "Öppna ändå".

### Kontrollera grundnivån

Du är inte klar förrän det här stämmer:

1. `curl -s localhost:5600/api/0/info` svarar.
2. ActivityWatch har en bucket av typen `currentwindow` med händelser från de senaste
   minuterna, och fönstertitlarna är inte tomma:
   `curl -s "localhost:5600/api/0/buckets/" | python3 -m json.tool`, sedan
   `curl -s "localhost:5600/api/0/buckets/<bucket-id>/events?limit=5"`.
   Tomma titlar betyder att ActivityWatch saknar behörighet under Hjälpmedel
   (Accessibility). Be användaren slå på den och starta om ActivityWatch.
3. Webbläsaren: be användaren klicka i Safari eller Chrome och svara OK på frågan om att
   python3 får styra webbläsaren. Kör sedan `python3 ~/tidskoll/bin/webblasare.py --en-gang`
   medan webbläsaren är aktiv. Den ska skriva ut en adress. Firefox stöds inte, där finns
   ActivityWatchs eget tillägg aw-watcher-web.
4. `launchctl print gui/$(id -u)/com.tidskoll.webblasare` visar `state = running`.
5. `python3 ~/tidskoll/bin/veckorapport.py` skriver en fil utan fel (den är tom första dagen).

## Installera skärmdumpsnivån (bara om användaren sagt ja)

Kräver Xcode Command Line Tools: `xcode-select -p`. Saknas de, kör `xcode-select --install`
och vänta tills användaren klickat igenom installationen.

Kör `bash installera.sh skarm`. Skriptet bygger `~/Applications/Tidskoll.app`, en liten app
vars enda uppgift är att starta skärmdumpsloopen. Den behövs för att macOS ska kunna ge
behörighet att spela in skärmen: ett vanligt skript räknas som Apples egen bash och nekas tyst.

Sedan måste användaren själv ge behörigheter. Skicka hen direkt till rätt ställe:
Systeminställningar → Integritet och säkerhet → Skärm- och systemljudinspelning
(Screen & System Audio Recording) → + → tryck Cmd+Shift+G → skriv `~/Applications` → välj
Tidskoll.app. Samma sak under Hjälpmedel (Accessibility). Dialogrutor dyker sällan upp av
sig själva för bakgrundsprogram, så vänta inte på dem.

Starta om efter behörigheterna: `bash installera.sh fortsatt`.

Fällor:
- Bygg aldrig om appen efter att behörigheten getts. Den nya signaturen gör behörigheten
  ogiltig. Måste den byggas om (`installera.sh skarm --bygg-om`): användaren tar bort
  appen ur listan med minus och lägger till den igen.
- `screencapture` vägrar skriva till filnamn som börjar med punkt, med samma felmeddelande
  som när behörighet saknas. Skriptet undviker det redan.

### Kontrollera skärmdumpsnivån

1. `launchctl print gui/$(id -u)/com.tidskoll.skarm` visar `state = running`.
2. Efter en halv minut finns minst en bild i `~/tidskoll/skarm/days/<idag>/`, mellan 15 och 500 kB.
3. Senaste raden i `log.jsonl` har ett appnamn som inte är tomt.
4. Öppna en av bilderna själv och kontrollera att texten går att läsa.
5. Kontrollera pauslistan: öppna en sajt från listan, vänta tio sekunder, och se att
   loggraden har `"img": false`.

Fungerar något inte: felsök nu. Säg aldrig att det är klart på en halv installation.

## Erbjud nattlig analys (valfritt)

`bash installera.sh nattanalys` låter Claude Code analysera dagens skärmdumpar klockan 23:30
och fylla på `~/tidskoll/observationer.md`. Det är det som gör att `/tidskoll effektivisera`
får något att arbeta med efter en vecka. Varje körning använder användarens Claude-plan.
Fråga först.

## Avsluta

Berätta för användaren:
- Var datan ligger (`~/tidskoll/`) och att den aldrig lämnar datorn av sig själv.
- Att `/tidskoll` fungerar i Claude Code var som helst: "vart tog tiden vägen igår?",
  `/tidskoll vecka`, `/tidskoll kategorier`.
- Att kategorierna blir bra först med verklig data. Föreslå att hen kör `/tidskoll kategorier`
  efter en eller två dagar. Då går ni igenom det som saknar kategori tillsammans.
- Hur skärmdumparna pausas: `/tidskoll paus`, eller `bash installera.sh paus`.
- Att `bash installera.sh avinstallera` tar bort allt utom datan.
