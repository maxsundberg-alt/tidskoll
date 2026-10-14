# Tidskoll

Se exakt vart tiden vid datorn tar vägen. Tidskoll mäter vilken app, vilket fönster och
vilken webbsida du har framför dig, sorterar tiden i kategorier och ger dig en
veckorapport varje söndag. Den kan också blockera sajter du vill hålla dig borta från, och
visa om blocket faktiskt höll. Vill du gå längre kan den ta skärmdumpar, så att en AI kan se
hur du arbetar och föreslå vad som går att göra snabbare.

Allt körs på din egen Mac. Ingen server, inget konto, och datan lämnar inte datorn av sig själv.

Kräver en Mac och en AI-agent som kan köra kommandon i terminalen, till exempel Claude Code,
Codex, Cursor eller Gemini CLI. Agenten sköter installationen, och efteråt frågar du den om din tid.

## Installera

1. Ladda ner mappen: grön knapp **Code → Download ZIP**, packa upp. Eller `git clone`.
2. Öppna mappen i din agent (i terminalen till exempel `cd tidskoll && claude`, `codex` eller `gemini`).
3. Skriv:

> Läs AGENTS.md i den här mappen och sätt upp Tidskoll på min dator.

Agenten frågar vilka delar du vill ha, installerar, och kontrollerar att allt fungerar innan
den säger att den är klar. Några behörigheter i Systeminställningar måste du ge själv.
Agenten säger exakt var.

## Tre delar

**Grundnivån** bygger på [ActivityWatch](https://activitywatch.net), en gratis tidmätare med
öppen källkod. Tidskoll lägger till det som gör datan användbar:

- Adressen i webbläsaren loggas, för Safari, Chrome, Arc, Brave, Edge och Vivaldi. Då syns
  skillnaden mellan tjugo minuter i ett kalkylark och tjugo minuter på YouTube, fast båda var "Safari".
- En svensk startindelning i kategorier: arbete, kommunikation, AI-verktyg, planering,
  privat och konsumtion. Efter ett par dagar går agenten igenom den tid som saknar kategori
  tillsammans med dig och skriver regler för just dina projekt och kunder.
- En veckorapport som öppnas i webbläsaren söndag kväll: aktiv tid, tid per dag, per
  kategori, toppappar och toppsajter, jämfört med veckan innan.
- Skillen `tidskoll`, som din agent använder för att svara på frågor som "vart tog tiden
  vägen i tisdags?" eller "hur mycket tid la jag på mejl den här veckan?". Den följer den öppna
  standarden för agent-skills och installeras där de flesta agenter letar.

Bara tid när du faktiskt sitter vid datorn räknas. Står den orörd räknas tiden som borta.

**Blockering** är valfri. Sajterna i en lista du själv bestämmer över slutar ladda i alla
webbläsare på datorn. Att öppna en igen kräver lösenordet, och veckorapporten visar hur mycket
tid som ändå gick till blockerade sajter. [minska-skarmtiden.md](minska-skarmtiden.md) går
igenom resten av verktygslådan: att dölja flöden med SocialFocus, pauser med One Sec, Skärmtid
på telefonen, och fallgroparna som får ett block att läcka.

**Skärmdumpar** är valfria. Den tar en bild av skärmen var femte sekund i låg upplösning,
glesare när inget ändras och inte alls när du är borta. När du ber om en analys tittar agenten på de 10 till 30
bilder som säger mest om dagen och letar efter mönster: menyer där ett kortkommando finns,
samma kopiera och klistra in om och om igen, ett verktyg som har ett bättre alternativ.
Analysen görs bara när du ber om den. Ett mönster blir ett förslag först när det setts tre
gånger, så be om en analys av några olika dagar. Sedan ger `tidskoll effektivisera` de
förslag som sparar mest tid.

## Integritet

Grundnivån sparar appnamn, fönstertitlar och adresser i ActivityWatch på din dator.

Skärmdumpsnivån fotar allt som syns på skärmen, även privata meddelanden. Bilderna sparas
i `~/tidskoll/skarm/` och raderas efter 30 dagar. Det som lämnar datorn är det agenten läser
när du ber om en analys: loggrader och de utvalda bilderna. De skickas till leverantören av
AI-modellen du använder, som allt annat du visar den.

Pauslistan `~/tidskoll/pauslista.txt` stoppar skärmdumpar från lösenordshanterare,
BankID, banker, betalsidor och myndigheter från början. Lägg till egna rader, en per app
eller adress. Be agenten pausa skärmdumparna, eller kör `bash installera.sh paus` och
`bash installera.sh fortsatt`.

## Var allt ligger

```
~/tidskoll/
├── bin/                skripten
├── SKILL.md            instruktionerna till agenten, som vanlig fil
├── kategorier.json     dina kategoriregler
├── blocklista.txt      sajter som blockeras (blockeringen)
├── rapporter/          veckorapporterna
├── pauslista.txt       där inga skärmdumpar tas
├── skarm/days/         skärmdumpar och logg per dag (skärmdumpsnivån)
├── anteckningar/       agentens dagsanteckningar
└── observationer.md    återkommande mönster
```

## Ta bort

`bash installera.sh avinstallera` stoppar allt, tar bort sajtblocket och tar bort skripten,
appen och skillen.
Din data i `~/tidskoll/` och ActivityWatch själv ligger kvar tills du tar bort dem.

## Tack

Skärmdumpsdelen bygger på [screenwatch-kit](https://github.com/tabani-png/screenwatch-kit)
av Muhammad Ali (MIT-licens): idén med en kompilerad app som bär behörigheten,
upptagningsloopen och metoden att läsa metadata först och bilder sedan.
Tidmätningen är [ActivityWatch](https://github.com/ActivityWatch/activitywatch) (MPL-2.0),
som installeras separat och inte ingår här.
