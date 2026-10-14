# Tidskoll — instruktioner till AI-agenten

Du hjälper någon att sätta upp Tidskoll på sin Mac. Användaren har öppnat den här mappen
i en AI-agent som kan köra terminalkommandon (Claude Code, Codex, Cursor, Gemini CLI eller
någon annan) och vill veta hur hen lägger sin tid vid datorn. Hen behöver inte kunna
programmera. Förklara vad som händer i klartext, och kör alla kommandon själv.

Läs `README.md` för vad Tidskoll är. Den här filen beskriver hur du installerar.

## Innan du börjar

Kontrollera att det är en Mac (`uname` ger `Darwin`). Tidskoll fungerar inte på Windows
eller Linux. Säg det i så fall och avbryt.

Fråga sedan användaren, i ett och samma meddelande:

1. **Vilka delar?** Tidskoll har fyra delar, och bara den första är nödvändig:
   - Grundnivån mäter tid per app, fönster, webbsida och kategori, och ger en veckorapport.
   - Blockeringen gör att utvalda sajter inte går att öppna i någon webbläsare. Veckorapporten
     visar sedan om någon av dem ändå laddades.
   - Dölja flöden döljer flödet på LinkedIns startsida i Safari, så att LinkedIn går att
     använda för meddelanden och profiler utan att fastna i flödet.
   - Skärmdumpsnivån tar en bild av skärmen var femte sekund, så att du kan se hur hen
     arbetar och föreslå förbättringar.
   Rekommendera grundnivån först. Resten kan läggas till senare.
2. **Om skärmdumpar:** säg rakt ut att allt på skärmen fotas, även privata meddelanden,
   och att bilderna stannar på datorn. Undantaget är de 10 till 30 bilder per dag som du
   tittar på vid en analys. De skickas till leverantören av AI-modellen du kör på. Pauslistan
   är ifylld från början och stoppar skärmdumpar av banker, lösenordshanterare och
   betalsidor. Fråga om något mer ska läggas till.
3. **Har hen redan ActivityWatch?** Om hen har egna kategorier där får de inte skrivas över
   utan att hen har sagt ja.

## Grundnivån

Kör `bash installera.sh bas` i den här mappen. Skriptet:
- installerar ActivityWatch med Homebrew om den saknas (finns inte Homebrew: be användaren
  ladda ner ActivityWatch från https://activitywatch.net/downloads/, eller installera Homebrew först),
- startar ActivityWatch och lägger den bland inloggningsobjekten,
- kopierar skripten och en kopia av `installera.sh` till `~/tidskoll/bin/`, och startindelningen
  till `~/tidskoll/kategorier.json`,
- startar webbläsarbevakaren och schemalägger veckorapporten (söndag 20:00),
- installerar skillen `tidskoll` i `~/.agents/skills/` (standardmappen, som bland andra
  Codex, Cursor och Gemini CLI läser) och `~/.claude/skills/` (Claude Code), och lägger
  samma instruktioner som vanlig fil i `~/tidskoll/SKILL.md`.

Läser du inte skills från någon av de mapparna: kontrollera i din dokumentation var du läser
dem och kopiera `skill/tidskoll/SKILL.md` dit. Saknar du stöd för skills helt, säg till
användaren att hen kan be dig "läsa ~/tidskoll/SKILL.md" när hen vill fråga om sin tid.

Kategorierna:
- Har användaren inga egna kategorier i ActivityWatch: kör
  `python3 ~/tidskoll/bin/kategorier.py tillampa ~/tidskoll/kategorier.json`.
- Har hen egna kategorier och vill behålla dem: kör
  `python3 ~/tidskoll/bin/kategorier.py exportera > ~/tidskoll/kategorier.json`, så att
  filen speglar det hen redan har.

Den gamla uppsättningen sparas alltid i `~/tidskoll/kategorier-backup/` innan något skrivs över.

Om macOS stoppar ActivityWatch första gången ("kan inte öppnas"): be användaren öppna
Systeminställningar → Integritet och säkerhet och klicka på "Öppna ändå".

### Kontrollera grundnivån

Du är inte klar förrän det här stämmer:

1. `curl -s localhost:5600/api/0/info` svarar.
2. ActivityWatch har en bucket av typen `currentwindow` med händelser från de senaste
   minuterna, och fönstertitlarna är inte tomma:
   `curl -s "localhost:5600/api/0/buckets/" | python3 -m json.tool`, sedan
   `curl -s "localhost:5600/api/0/buckets/<bucket-id>/events?limit=5"`.
   Tomma titlar betyder att ActivityWatch saknar behörighet under Hjälpmedel
   (Accessibility). Be användaren slå på den och starta om ActivityWatch.
3. Webbläsaren: be användaren klicka i Safari eller Chrome och svara OK när macOS frågar om
   python3 får styra webbläsaren. Kör sedan `python3 ~/tidskoll/bin/webblasare.py --en-gang`
   medan webbläsaren är aktiv. Den ska skriva ut en adress. Firefox stöds inte. Där finns i
   stället ActivityWatchs eget tillägg aw-watcher-web.
4. `launchctl print gui/$(id -u)/com.tidskoll.webblasare` visar `state = running`.
5. `python3 ~/tidskoll/bin/veckorapport.py` skriver en fil utan fel (den är tom första dagen).

## Blockeringen (bara om användaren sagt ja)

Kör `bash installera.sh blockera`. Det kopierar `blockera.sh` till `~/tidskoll/bin/` och
listan till `~/tidskoll/blocklista.txt`, men slår inte på något.

Gå igenom listan med användaren först. Den innehåller video, sociala medier, forum och
svenska nyhetssajter. Fråga vad hen behöver i jobbet. En sajt som används i arbetet ska inte
blockeras. Där är det bättre att dölja flödet med ett tillägg som SocialFocus (se
`minska-skarmtiden.md`). Sätt `#` framför det som inte ska med.

Slå på: `bash ~/tidskoll/bin/blockera.sh pa`. macOS visar en ruta där användaren skriver
datorns lösenord. Be aldrig om lösenordet i chatten och skriv det aldrig någonstans.

Kontrollera:
1. `bash ~/tidskoll/bin/blockera.sh status` säger att blockeringen är på.
2. `curl -sI --max-time 5 https://<en blockerad sajt>` misslyckas.
3. Be användaren öppna en blockerad sajt som inte redan var öppen i någon flik. Går den ändå
   att öppna i Safari är det nästan alltid Privat reläservice (iCloud Private Relay), som
   skickar trafiken förbi `/etc/hosts`. Inställningen finns under Systeminställningar → ditt
   namn högst upp → iCloud → Privat reläservice. Användaren väljer själv om den ska stängas
   av. Annars fungerar blockeringen bara i andra webbläsare.

Säg också att en sajt öppnas tillfälligt med `blockera.sh lyft <domän>` och blockeras igen
med `blockera.sh ater <domän>`, och att båda kräver datorns lösenord. Det är meningen.

## Dölja flöden (bara om användaren sagt ja)

Kör `bash installera.sh floden`. Det lägger skripten från `dolj-floden/` i mappen
`Userscripts` i iCloud Drive (eller i `~/tidskoll/userscripts` om iCloud Drive saknas).
Har användaren redan en Userscripts-mapp: kopiera filen dit i stället.

Resten är inställningar som användaren gör själv. Gå igenom stegen i `dolj-floden/README.md`
med hen: installera Userscripts från App Store, välj mappen, slå på tillägget i Safari och
tillåt linkedin.com. På iPhone även "Behåll nedladdad" på mappen i Filer-appen.

Kontrollera genom att be användaren öppna linkedin.com i Safari och säga vad hen ser. Under
rutan för att skriva inlägg ska det stå "Flödet är dolt." Har hen ett annat tillägg som
döljer flöden, till exempel SocialFocus, ska det stängas av för linkedin.com så att de inte
krockar.

## Skärmdumpsnivån (bara om användaren sagt ja)

Kräver Xcode Command Line Tools. Kontrollera med `xcode-select -p`. Saknas de, kör
`xcode-select --install` och vänta tills användaren klickat igenom installationen.

Kör `bash installera.sh skarm`. Skriptet bygger `~/Applications/Tidskoll.app`, en liten app
vars enda uppgift är att starta skärmdumpsloopen. Den behövs för att macOS ska kunna ge
behörighet att spela in skärmen: ett vanligt skript räknas som Apples egen bash och nekas tyst.

Sedan måste användaren själv ge behörigheter. Skicka hen direkt till rätt ställe:
Systeminställningar → Integritet och säkerhet → Skärm- och systemljudinspelning
(Screen & System Audio Recording) → + → tryck Cmd+Shift+G → skriv `~/Applications` → välj
Tidskoll.app. Samma sak under Hjälpmedel (Accessibility). Dialogrutor dyker sällan upp av
sig själva för bakgrundsprogram, så vänta inte på dem.

Starta om skärmdumparna när behörigheterna är givna: `bash installera.sh fortsatt`.

Fällor:
- Bygg aldrig om appen efter att behörigheten getts. Den nya signaturen gör behörigheten
  ogiltig. Måste den byggas om (`installera.sh skarm --bygg-om`): användaren tar bort
  appen ur listan med minus och lägger till den igen.
- `screencapture` vägrar skriva till filnamn som börjar med punkt, med samma felmeddelande
  som när behörighet saknas. Skriptet undviker det redan.

### Kontrollera skärmdumpsnivån

1. `launchctl print gui/$(id -u)/com.tidskoll.skarm` visar `state = running`.
2. Efter en halv minut finns minst en bild i `~/tidskoll/skarm/dagar/<idag>/`, mellan 15 och 500 kB.
3. Senaste raden i `log.jsonl` har ett appnamn som inte är tomt.
4. Öppna en av bilderna själv och kontrollera att texten går att läsa.
5. Kontrollera pauslistan: öppna en sajt från listan, vänta tio sekunder och se att
   loggraden har `"img": false`.

Fungerar något inte: felsök nu. Säg aldrig att installationen är klar när bara en del fungerar.

## Avsluta

Berätta för användaren:
- Var datan ligger (`~/tidskoll/`) och att den aldrig lämnar datorn av sig själv.
- Hur skillen anropas i hens agent, till exempel `/tidskoll` i Claude Code och Cursor eller
  `$tidskoll` i Codex. Det går också att fråga fritt: "vart tog tiden vägen igår?".
- Att kategorierna blir bra först med verklig data. Föreslå att hen ber om
  `tidskoll kategorier` efter en eller två dagar. Då går ni igenom tiden som saknar kategori.
- Att skärmdumparna bara analyseras när hen ber om det, och att ett mönster blir ett förslag
  först när det setts tre gånger.
- Att `minska-skarmtiden.md` beskriver verktyg för telefonen och för sajter som inte går
  att blockera, som One Sec och Skärmtid.
- Att den nedladdade mappen kan slängas. Status, paus och avinstallation sköts sedan med
  `bash ~/tidskoll/bin/installera.sh status|paus|fortsatt|avinstallera`.
