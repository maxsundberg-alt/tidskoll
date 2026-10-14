# Tidskoll

Se exakt vart tiden vid datorn tar vägen, och gör något åt det. Tidskoll är byggt för Mac och
sätts upp av din AI-agent. Det har fyra delar:

- **Tidmätning.** Vilken app, vilket fönster och vilken webbsida du har framför dig, sorterat i
  kategorier, med en veckorapport varje söndag.
- **Blockering.** Sajter du vill hålla dig borta från går inte att öppna i någon webbläsare, och
  veckorapporten visar om blockeringen höll.
- **Dölja flöden.** LinkedIn-flödet försvinner, medan meddelanden, profiler och resten av
  LinkedIn fungerar som vanligt.
- **Skärmdumpar.** Din agent ser hur du arbetar och föreslår vad som går att göra snabbare.

Bara tidmätningen är nödvändig. Resten väljer du till eller låter bli.

Allt körs på din egen Mac. Det finns ingen server och inget konto, och datan lämnar inte
datorn av sig själv.

## Det här behövs

- En Mac.
- En AI-agent som kan köra kommandon i terminalen, till exempel Claude Code, Codex, Cursor
  eller Gemini CLI. Agenten sköter installationen, och efteråt är det den du frågar om din tid.
- Helst [Homebrew](https://brew.sh). Utan det får du ladda ner ActivityWatch själv.

## Installera

1. Ladda ner mappen: grön knapp **Code → Download ZIP**, och packa upp den. Mappen heter då
   `tidskoll-main`. Med `git clone` heter den `tidskoll`.
2. Öppna mappen i din agent, i terminalen till exempel `cd tidskoll-main` och sedan `claude`,
   `codex` eller `gemini`.
3. Skriv:

> Läs AGENTS.md i den här mappen och sätt upp Tidskoll på min dator.

Agenten frågar vilka delar du vill ha, installerar och kontrollerar att allt fungerar innan
den säger att den är klar. Några behörigheter i Systeminställningar måste du ge själv, och
agenten säger exakt var. När installationen är klar kan den nedladdade mappen slängas. Vill du
lägga till en del senare laddar du ner den igen.

## Använda

Fråga din agent med egna ord, till exempel:

- "Vart tog tiden vägen igår?"
- "Hur mycket tid la jag på mejl den här veckan?"
- "Gå igenom tiden som saknar kategori."
- "Öppna YouTube tillfälligt."
- "Analysera gårdagen." (kräver skärmdumpar)

Agenten använder skillen `tidskoll`, en instruktionsfil som installeras där de flesta agenter
letar. Den kan också anropas direkt, med `/tidskoll` i Claude Code och Cursor eller
`$tidskoll` i Codex, följt av `dag`, `vecka`, `kategorier`, `analysera`, `effektivisera`,
`blockera`, `lyft`, `ater`, `status`, `paus` eller `fortsatt`.

Veckorapporten öppnas av sig själv i webbläsaren varje söndag klockan 20. Sover datorn då
öppnas den när den vaknar.

## De fyra delarna

### Tidmätning

Bygger på [ActivityWatch](https://activitywatch.net), en gratis tidmätare med öppen källkod.
Tidskoll lägger till tre saker:

- **Adressen i webbläsaren** loggas för Safari, Chrome, Arc, Brave, Edge och Vivaldi. Då syns
  skillnaden mellan tjugo minuter i ett kalkylark och tjugo minuter på YouTube, trots att båda
  bara hette "Safari" i ActivityWatch. I Firefox loggas bara fönstertiteln.
- **Kategorier på svenska.** Startindelningen har arbete, AI-verktyg, kommunikation, planering,
  privat och konsumtion. Efter ett par dagar går agenten tillsammans med dig igenom tiden som
  saknar kategori och skriver regler för just dina projekt och kunder.
- **Veckorapporten**: aktiv tid, tid per dag och per kategori, de mest använda apparna och
  sajterna, jämfört med veckan innan.

Bara tid då du sitter vid datorn räknas. Står datorn orörd räknas du som borta, och den tiden
kommer inte med.

### Blockering

Sajterna i en lista som du själv bestämmer över går inte att öppna i någon webbläsare på
datorn, inte heller i inkognitoläge. Listan innehåller från början video, sociala medier,
forum och nyhetssajter, och agenten går igenom den med dig innan något slås på. Att öppna en
blockerad sajt igen kräver datorns lösenord. Veckorapporten visar hur mycket tid som ändå gick
till blockerade sajter.

Guiden [minska-skarmtiden.md](minska-skarmtiden.md) går igenom fler verktyg, bland annat One Sec
och Skärmtid på telefonen, och de vanligaste skälen till att en blockering inte håller.

### Dölja flöden

En sajt du behöver i jobbet går inte att blockera. Där döljer Tidskoll i stället flödet. Skriptet
döljer flödet på LinkedIns startsida, medan meddelanden, profiler och rutan för att skriva inlägg
fungerar som vanligt. Det körs i Safari på Mac och iPhone med den kostnadsfria appen Userscripts.
Agenten kan skriva fler skript för andra sajter. Mer i [dolj-floden/README.md](dolj-floden/README.md).

### Skärmdumpar

Tidskoll tar en bild av skärmen var femte sekund i låg upplösning, glesare när inget ändras och
inte alls när du är borta. När du ber om en analys tittar agenten på de 10 till 30 bilder som
säger mest om dagen och letar efter mönster: menyer där det finns ett kortkommando, att du
kopierar och klistrar in samma sak om och om igen, eller ett verktyg som har ett bättre
alternativ. Ett mönster blir ett förslag först när det setts tre gånger, så be om analyser av
några olika dagar. Sedan ger "tidskoll effektivisera" de förslag som sparar mest tid.

Analysen görs bara när du ber om den.

## Integritet

**Tidmätningen** sparar appnamn, fönstertitlar och adresser i ActivityWatch på din dator.

**Blockeringen** skriver i `/etc/hosts`, datorns egen adressbok. En kopia av filen som den såg
ut innan sparas som `/etc/hosts.tidskoll-original`.

**Dölja flöden** körs helt i Safari och skickar ingenting någonstans.

**Skärmdumparna** fotar allt som syns på skärmen, även privata meddelanden. Bilderna och loggen
sparas i `~/tidskoll/skarm/` och raderas efter 30 dagar, medan agentens anteckningar sparas.
Det som lämnar datorn är det agenten läser när du ber om en analys: loggrader och de utvalda
bilderna. De skickas till leverantören av AI-modellen du använder, precis som allt annat du
visar agenten.

Pauslistan `~/tidskoll/pauslista.txt` är ifylld från början och stoppar skärmdumpar av
lösenordshanterare, BankID, banker, betalsidor, myndigheter och vården. Lägg till egna rader,
en per app eller adress.

Vill du stoppa alla skärmdumpar en stund: be agenten pausa dem, eller kör
`bash ~/tidskoll/bin/installera.sh paus` och sedan `bash ~/tidskoll/bin/installera.sh fortsatt`.

## Var allt ligger

```
~/tidskoll/
├── bin/                     skripten, och en kopia av installera.sh
├── SKILL.md                 instruktionerna till agenten, som vanlig fil
├── kategorier.json          dina kategoriregler
├── kategorier-backup/       kopior av tidigare kategorier
├── rapporter/               veckorapporterna
├── logg/                    loggar från webbläsarbevakaren och veckorapporten
├── blocklista.txt           sajterna som blockeras
├── blockera-undantag.txt    sajter som är tillfälligt öppnade
├── pauslista.txt            där inga skärmdumpar tas
├── skarm/dagar/             skärmdumpar och logg, en mapp per dag
├── skarm/daemon.log         fel från skärmdumparna
├── anteckningar/            agentens dagsanteckningar
└── observationer.md         återkommande mönster från analyserna
```

Skripten som döljer flöden ligger i mappen `Userscripts` i iCloud Drive, så att samma fil
används på Mac och iPhone. Saknas iCloud Drive ligger de i `~/tidskoll/userscripts/`.

## Ta bort

`bash ~/tidskoll/bin/installera.sh avinstallera` stänger av allt och tar bort blockeringen,
skripten, appen och skillen. Det här ligger kvar tills du tar bort det själv:

- din data i `~/tidskoll/`
- ActivityWatch
- skripten som döljer flöden, i mappen `Userscripts` (eller stäng av Userscripts i Safari)

## Tack

Skärmdumparna bygger på [screenwatch-kit](https://github.com/tabani-png/screenwatch-kit) av
Muhammad Ali (MIT-licens): idén med en kompilerad app som macOS kan ge behörigheten till,
skriptet som tar skärmdumparna och metoden att läsa metadata först och bilder sedan.
Tidmätningen sköts av [ActivityWatch](https://github.com/ActivityWatch/activitywatch) (MPL-2.0),
som installeras separat och inte ingår här.

Licens: MIT, se [LICENSE](LICENSE).
