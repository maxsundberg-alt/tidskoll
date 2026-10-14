# Tidskoll

Se exakt vart tiden vid datorn tar vägen. Tidskoll mäter vilken app, vilket fönster och
vilken webbsida du har framför dig, sorterar tiden i kategorier och ger dig en
veckorapport varje söndag. Den kan också blockera sajter du vill hålla dig borta från och
visa om blockeringen faktiskt höll. Vill du gå längre kan den ta skärmdumpar, så att din
AI-agent kan se hur du arbetar och föreslå vad som går att göra snabbare.

Allt körs på din egen Mac. Det finns ingen server och inget konto, och datan lämnar inte
datorn av sig själv.

Kräver en Mac och en AI-agent som kan köra kommandon i terminalen, till exempel Claude Code,
Codex, Cursor eller Gemini CLI. Agenten sköter installationen, och efteråt frågar du den om din tid.

## Installera

1. Ladda ner mappen: grön knapp **Code → Download ZIP** och packa upp den. Mappen heter då
   `tidskoll-main`. Med `git clone` heter den `tidskoll`.
2. Öppna mappen i din agent. I terminalen till exempel `cd tidskoll-main` och sedan `claude`,
   `codex` eller `gemini`.
3. Skriv:

> Läs AGENTS.md i den här mappen och sätt upp Tidskoll på min dator.

Agenten frågar vilka delar du vill ha, installerar och kontrollerar att allt fungerar innan
den säger att den är klar. Några behörigheter i Systeminställningar måste du ge själv.
Agenten säger exakt var.

## Tre delar

**Grundnivån** bygger på [ActivityWatch](https://activitywatch.net), en gratis tidmätare med
öppen källkod. Tidskoll lägger till det som gör datan användbar:

- Tidskoll loggar adressen i webbläsaren (Safari, Chrome, Arc, Brave, Edge och Vivaldi). Då
  syns skillnaden mellan tjugo minuter i ett kalkylark och tjugo minuter på YouTube, trots att
  båda bara hette "Safari" i loggen.
- En svensk startindelning i kategorier: arbete, kommunikation, AI-verktyg, planering,
  privat och konsumtion. Efter ett par dagar går agenten tillsammans med dig igenom tiden
  som saknar kategori och skriver regler för just dina projekt och kunder.
- En veckorapport som öppnas i webbläsaren varje söndagskväll: aktiv tid, tid per dag och
  per kategori, de mest använda apparna och sajterna, jämfört med veckan innan.
- Skillen `tidskoll`, en instruktionsfil som agenten läser för att svara på frågor som
  "vart tog tiden vägen i tisdags?" eller "hur mycket tid la jag på mejl den här veckan?".
  Den följer den öppna standarden för agent-skills och installeras där de flesta agenter letar.

Bara tid då du sitter vid datorn räknas. Står datorn orörd räknas du som borta, och den
tiden kommer inte med.

**Blockeringen** är valfri. Sajterna i en lista som du själv bestämmer över går inte längre
att öppna i någon webbläsare på datorn. Att öppna en av dem igen kräver datorns lösenord,
och veckorapporten visar hur mycket tid som ändå gick till blockerade sajter.
Guiden [minska-skarmtiden.md](minska-skarmtiden.md) tar upp fler verktyg: SocialFocus som
döljer flöden, One Sec som lägger in en paus, Skärmtid på telefonen och de vanligaste skälen
till att en blockering inte håller.

**Skärmdumpsnivån** är också valfri. Tidskoll tar då en bild av skärmen var femte sekund i
låg upplösning, glesare när inget ändras och inte alls när du är borta. När du ber om en
analys tittar agenten på de 10 till 30 bilder som säger mest om dagen och letar efter mönster:
menyer där det finns ett kortkommando, att du kopierar och klistrar in samma sak om och om
igen, eller ett verktyg som har ett bättre alternativ. Ett mönster blir ett förslag först när
det setts tre gånger, så be om analyser av några olika dagar. Sedan ger `tidskoll effektivisera`
de förslag som sparar mest tid.

## Integritet

Grundnivån sparar appnamn, fönstertitlar och adresser i ActivityWatch på din dator.

Skärmdumpsnivån fotar allt som syns på skärmen, även privata meddelanden. Bilderna och
loggen sparas i `~/tidskoll/skarm/` och raderas efter 30 dagar. Agentens anteckningar sparas.
Det som lämnar datorn är det agenten läser när du ber om en analys: loggrader och de utvalda
bilderna. De skickas till leverantören av AI-modellen du använder, precis som allt annat du
visar agenten.

Pauslistan `~/tidskoll/pauslista.txt` är ifylld från början och stoppar skärmdumpar av
lösenordshanterare, BankID, banker, betalsidor, myndigheter och vården. Lägg till egna
rader, en per app eller adress.

Vill du stoppa alla skärmdumpar en stund: be agenten pausa dem, eller kör
`bash ~/tidskoll/bin/installera.sh paus` och sedan `fortsatt`.

## Var allt ligger

```
~/tidskoll/
├── bin/                     skripten, och en kopia av installera.sh
├── SKILL.md                 instruktionerna till agenten, som vanlig fil
├── kategorier.json          dina kategoriregler
├── kategorier-backup/       kopior av tidigare kategorier
├── rapporter/               veckorapporterna
├── logg/                    loggar från webbläsarbevakaren och veckorapporten
├── blocklista.txt           sajterna som blockeras (blockeringen)
├── blockera-undantag.txt    sajter som är tillfälligt öppnade (blockeringen)
├── pauslista.txt            där inga skärmdumpar tas (skärmdumpsnivån)
├── skarm/dagar/             skärmdumpar och logg per dag (skärmdumpsnivån)
├── skarm/daemon.log         fel från skärmdumparna
├── anteckningar/            agentens dagsanteckningar
└── observationer.md         återkommande mönster
```

## Ta bort

`bash ~/tidskoll/bin/installera.sh avinstallera` stänger av allt och tar bort blockeringen,
skripten, appen och skillen. Din data i `~/tidskoll/` och ActivityWatch själv ligger kvar
tills du tar bort dem.

## Tack

Skärmdumpsdelen bygger på [screenwatch-kit](https://github.com/tabani-png/screenwatch-kit)
av Muhammad Ali (MIT-licens): idén med en kompilerad app som macOS kan ge behörigheten till,
skriptet som tar skärmdumparna och metoden att läsa metadata först och bilder sedan.
Tidmätningen sköts av [ActivityWatch](https://github.com/ActivityWatch/activitywatch)
(MPL-2.0), som installeras separat och inte ingår här.
