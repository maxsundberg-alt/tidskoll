# Tidskoll — instruktioner till AI-agenten

Du hjälper någon att sätta upp Tidskoll på sin Mac. Användaren har öppnat den här mappen
i en AI-agent som kan köra terminalkommandon (Claude Code, Codex, Cursor, Gemini CLI eller
någon annan) och vill veta hur hen lägger sin tid vid datorn. Hen behöver inte kunna
programmera. Läs `README.md` för vad Tidskoll är. Den här filen beskriver hur du installerar.

## Så pratar du med användaren

Användaren ser allt du skriver och är troligen ingen tekniker.

- Kör alla kommandon själv. Visa inga kommandon, sökvägar eller filnamn om hen inte ber om dem.
- Använd inte ord som bucket, launchd, regex, skill, Homebrew, hosts-fil eller JSON utan att
  säga vad de betyder. Oftast behövs de inte alls.
- Säg innan varje del vad som ska hända och vilka klick hen gör själv. Installationen har
  flera steg, och det är lätt att tappa bort sig.
- Korta meningar. När hen behöver göra något: säg exakt var hen klickar.

Där det står "säg ungefär så här" nedan finns en färdig formulering. Använd den, och anpassa
den bara om situationen kräver det.

## Innan du börjar

Kontrollera att det är en Mac (`uname` ger `Darwin`). Tidskoll fungerar inte på Windows
eller Linux. Säg det i så fall och avbryt.

Kontrollera också själv om ActivityWatch redan finns (`/Applications/ActivityWatch.app`) och
i så fall om den har egna kategorier (`python3 bas/kategorier.py exportera` när den är igång).
Fråga inte användaren om det.

Fråga sedan vilka delar hen vill ha. Säg ungefär så här:

> Tidskoll har fyra delar. Den första behövs, de andra väljer du själv.
>
> 1. **Tidmätning.** Datorn noterar vilken app och webbsida du har framme, och varje söndag
>    får du en rapport över veckan.
> 2. **Blockering.** Sajter du väljer går inte att öppna på datorn. Du behöver datorns lösenord
>    för att slå på den.
> 3. **Dölj LinkedIn-flödet** i Safari på Mac och iPhone. Där installerar du en gratis app själv.
> 4. **Skärmdumpar.** En bild av skärmen var femte sekund, så att jag kan föreslå hur du jobbar
>    snabbare. Allt som syns fotas, även privata meddelanden. Bilderna stannar på datorn tills
>    du ber mig analysera en dag, och då skickas 10 till 30 av dem till [leverantören av din
>    AI-modell]. Banker, BankID och lösenordsappar fotas aldrig.
>
> Vilka vill du ha? Är du osäker, börja med 1. Resten kan läggas till senare.

Fyll i leverantören (Anthropic för Claude, OpenAI för Codex, Google för Gemini och så vidare).

Har ActivityWatch redan egna kategorier, fråga också: "Du har redan tidmätaren ActivityWatch
med egna kategorier. Vill du behålla dem, eller byta till Tidskolls svenska indelning? De
gamla sparas i båda fallen."

Säg också: "Spara den nedladdade mappen tills du vet vilka delar du vill ha. Den behövs om
du vill lägga till något senare."

## Tidmätning

Kör `bash installera.sh bas` i den här mappen. Skriptet:
- installerar ActivityWatch med Homebrew om den saknas,
- startar ActivityWatch och lägger den bland inloggningsobjekten,
- kopierar skripten och en kopia av `installera.sh` till `~/tidskoll/bin/`, och startindelningen
  till `~/tidskoll/kategorier.json`,
- startar webbläsarbevakaren och schemalägger veckorapporten (söndag 20:00),
- installerar skillen `tidskoll` i `~/.agents/skills/` (standardmappen, som bland andra
  Codex, Cursor och Gemini CLI läser) och `~/.claude/skills/` (Claude Code), och lägger
  samma instruktioner som vanlig fil i `~/tidskoll/SKILL.md`.

Saknas både ActivityWatch och Homebrew: be inte användaren installera Homebrew, det kräver
Terminalen. Guida i stället steg för steg: öppna https://activitywatch.net/downloads/, ladda
ner versionen för macOS, öppna filen, dra ActivityWatch till mappen Program och öppna den.
Kör sedan `bash installera.sh bas` igen.

Om macOS stoppar ActivityWatch första gången ("kan inte öppnas"): be användaren öppna
Systeminställningar → Integritet och säkerhet, scrolla ner och klicka på "Öppna ändå".

Läser du inte skills från någon av de mapparna: kontrollera i din dokumentation var du läser
dem och kopiera `skill/tidskoll/SKILL.md` dit. Saknar du stöd för skills helt, säg till
användaren att hen kan be dig "läsa ~/tidskoll/SKILL.md" när hen vill fråga om sin tid.

Kategorierna:
- Har ActivityWatch inga egna kategorier, eller vill användaren byta: kör
  `python3 ~/tidskoll/bin/kategorier.py tillampa ~/tidskoll/kategorier.json`.
- Vill hen behålla sina egna: kör
  `python3 ~/tidskoll/bin/kategorier.py exportera > ~/tidskoll/kategorier.json`, så att
  filen speglar det hen redan har.

Den gamla uppsättningen sparas alltid i `~/tidskoll/kategorier-backup/` innan något skrivs över.

Webbläsaren: innan du kontrollerar den, säg ungefär så här:

> Klicka i Safari eller Chrome. Strax frågar macOS om "python3" får styra webbläsaren.
> python3 är det lilla program som läser av vilken sida du har öppen åt Tidskoll. Klicka OK.
> Frågan kommer en gång per webbläsare.

Klickar hen "Tillåt inte" av misstag: Systeminställningar → Integritet och säkerhet →
Automatisering, och slå på webbläsaren under python3.

### Kontrollera tidmätningen

Du är inte klar förrän det här stämmer:

1. `curl -s localhost:5600/api/0/info` svarar.
2. ActivityWatch har en bucket av typen `currentwindow` med händelser från de senaste
   minuterna, och fönstertitlarna är inte tomma:
   `curl -s "localhost:5600/api/0/buckets/" | python3 -m json.tool`, sedan
   `curl -s "localhost:5600/api/0/buckets/<bucket-id>/events?limit=5"`.
   Tomma titlar betyder att ActivityWatch saknar behörighet. Be användaren öppna
   Systeminställningar → Integritet och säkerhet → Hjälpmedel och slå på ActivityWatch, och
   sedan avsluta ActivityWatch via ikonen i menyraden och öppna den igen.
3. `python3 ~/tidskoll/bin/webblasare.py --en-gang` medan webbläsaren är aktiv skriver ut en
   adress. I Firefox loggas bara fönstertiteln. Vill användaren ha adresser därifrån finns
   ActivityWatchs eget tillägg aw-watcher-web.
4. `launchctl print gui/$(id -u)/com.tidskoll.webblasare` visar `state = running`.
5. `python3 ~/tidskoll/bin/veckorapport.py` skriver en fil utan fel (den är tom första dagen).

## Blockering (bara om användaren sagt ja)

Kör `bash installera.sh blockera`. Det kopierar `blockera.sh` till `~/tidskoll/bin/` och
listan till `~/tidskoll/blocklista.txt`, men slår inte på något.

Gå igenom listan med användaren först. Den innehåller video, sociala medier, forum och
svenska nyhetssajter. Läs upp grupperna med vanliga namn och fråga vad hen behöver i jobbet.
En sajt som används i arbetet ska inte blockeras. Där är det bättre att dölja flödet (delen
Dölj LinkedIn-flödet, eller tillägget SocialFocus för andra sajter). Sätt `#` framför det som
inte ska med.

Slå sedan på med `bash ~/tidskoll/bin/blockera.sh pa`. Säg först ungefär så här:

> Nu visar macOS en ruta som ber om datorns lösenord. Skriv det i rutan, aldrig här i chatten.
> Det behövs eftersom blockeringen ändrar datorns egen adressbok för webbsidor.

Be aldrig om lösenordet i chatten och skriv det aldrig någonstans.

Kontrollera:
1. `bash ~/tidskoll/bin/blockera.sh status` säger att blockeringen är på.
2. `curl -sI --max-time 5 https://<en blockerad sajt>` misslyckas.
3. Be användaren öppna en blockerad sajt som inte redan var öppen i någon flik. Går den ändå
   att öppna i Safari är det nästan alltid Privat reläservice. Säg ungefär så här:

> Privat reläservice skyddar din integritet i Safari, men gör att blockeringen inte fungerar
> där. Vill du ha blockeringen i Safari kan du stänga av den under Systeminställningar → ditt
> namn högst upp → iCloud → Privat reläservice. Låter du den vara på gäller blockeringen bara
> i andra webbläsare.

Säg sist: "Vill du öppna en sajt igen kan du be mig om det. Det kräver datorns lösenord varje
gång, och sajten förblir öppen tills du ber mig blockera den igen."

## Dölj LinkedIn-flödet (bara om användaren sagt ja)

Kör `bash installera.sh floden`. Det lägger skripten från `dolj-floden/` i mappen
`Userscripts` i iCloud Drive (eller i `~/tidskoll/userscripts` om iCloud Drive saknas).
Har användaren redan en Userscripts-mapp: kopiera filen dit i stället.

Resten gör användaren själv. Gå igenom stegen i `dolj-floden/README.md` ett i taget, och vänta
på svar mellan stegen: installera Userscripts från App Store, välj mappen Userscripts i iCloud
Drive, slå på tillägget i Safari och tillåt linkedin.com. På iPhone även "Behåll nedladdad" på
mappen i Filer-appen.

Kontrollera genom att be användaren öppna linkedin.com i Safari och säga vad hen ser. Under
rutan för att skriva inlägg ska det stå "Flödet är dolt." Har hen ett annat tillägg som
döljer flöden, till exempel SocialFocus, ska det stängas av för linkedin.com så att de inte
krockar.

## Skärmdumpar (bara om användaren sagt ja)

Kräver Apples utvecklarverktyg. Kontrollera med `xcode-select -p`. Saknas de, kör
`xcode-select --install` och säg ungefär så här:

> En ruta från Apple frågar om du vill installera utvecklarverktyg. Klicka Installera. De är
> gratis och behövs för att bygga den lilla app som tar skärmdumparna. Säg till när det är klart.

Kör sedan `bash installera.sh skarm`. Skriptet bygger `~/Applications/Tidskoll.app`, en liten
app vars enda uppgift är att starta skärmdumparna. Den behövs för att macOS ska kunna ge
behörighet att spela in skärmen: ett vanligt skript räknas som Apples egen bash och nekas tyst.

Användaren måste själv ge två behörigheter. Dialogrutor dyker sällan upp av sig själva för
bakgrundsprogram, så vänta inte på dem. Säg ungefär så här:

> macOS låter bara program som du själv godkänt se skärmen, så nu lägger du till Tidskoll i
> två listor.
>
> 1. Öppna Systeminställningar → Integritet och säkerhet → Skärm- och systemljudinspelning.
>    Klicka på plustecknet, tryck Cmd+Shift+G, skriv ~/Applications och tryck Retur. Välj
>    Tidskoll och klicka Öppna.
> 2. Gör samma sak under Hjälpmedel. Det behövs för att Tidskoll ska kunna läsa vilken app
>    och vilket fönster som är aktivt.
>
> Säg till när du är klar.

Starta sedan om skärmdumparna: `bash installera.sh fortsatt`.

Bygg aldrig om appen efter att behörigheten getts. Den nya signaturen gör behörigheten
ogiltig. Måste den byggas om (`installera.sh skarm --bygg-om`) tar användaren bort appen ur
listan med minus och lägger till den igen.

### Kontrollera skärmdumparna

1. `launchctl print gui/$(id -u)/com.tidskoll.skarm` visar `state = running`.
2. Efter en halv minut finns minst en bild i `~/tidskoll/skarm/dagar/<idag>/`, mellan 15 och 500 kB.
3. Senaste raden i `log.jsonl` har ett appnamn som inte är tomt.
4. Öppna en av bilderna själv och kontrollera att texten går att läsa.
5. Kontrollera pauslistan: be användaren öppna en sajt från listan, vänta tio sekunder och se
   att loggraden har `"img": false`.

Fungerar något inte: felsök nu. Säg aldrig att installationen är klar när bara en del fungerar.

## Avsluta

Säg ungefär så här, och ta bara med de delar som installerades:

> Klart. Tidskoll mäter nu din tid i bakgrunden. Fråga mig med egna ord, till exempel "vart tog
> tiden vägen igår?". Om ett par dagar kan du be mig gå igenom tiden som saknar kategori, så
> blir rapporterna mer träffsäkra. Varje söndag klockan 20 öppnas veckorapporten av sig själv.
>
> [Blockering:] Vill du öppna en blockerad sajt, be mig. Den förblir öppen tills du ber mig
> blockera den igen.
>
> [Skärmdumpar:] Be mig analysera en dag när du vill. Efter några analyser kan jag föreslå
> vad som sparar mest tid. Vill du stoppa skärmdumparna en stund, säg "pausa skärmdumparna".
>
> All data ligger i mappen tidskoll i din hemmapp och lämnar inte datorn av sig själv. Vill du
> ändra, pausa eller ta bort något räcker det att säga det till mig. I guiden
> minska-skarmtiden.md finns fler tips, till exempel för telefonen.
