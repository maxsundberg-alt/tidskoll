# Tidskoll

Se exakt vart tiden vid datorn tar vägen. Tidskoll mäter vilken app, vilket fönster och
vilken webbsida du har framför dig, sorterar tiden i kategorier och ger dig en
veckorapport varje söndag. Vill du gå längre kan den också ta skärmdumpar, så att Claude
kan se hur du arbetar och föreslå vad som går att göra snabbare.

Allt körs på din egen Mac. Ingen server, inget konto, och datan lämnar inte datorn av sig själv.

Kräver en Mac och [Claude Code](https://claude.com/claude-code).

## Installera

1. Ladda ner mappen: grön knapp **Code → Download ZIP**, packa upp. Eller `git clone`.
2. Öppna Terminal i mappen och starta Claude Code: `cd tidskoll && claude`
3. Skriv:

> Sätt upp Tidskoll på min dator.

Claude läser `CLAUDE.md`, frågar vilken nivå du vill ha, installerar, och kontrollerar att
allt fungerar innan den säger att den är klar. Några behörigheter i Systeminställningar
måste du ge själv. Claude säger exakt var.

## Två nivåer

**Grundnivån** bygger på [ActivityWatch](https://activitywatch.net), en gratis tidmätare med
öppen källkod. Tidskoll lägger till det som gör datan användbar:

- Adressen i webbläsaren loggas, för Safari, Chrome, Arc, Brave, Edge och Vivaldi. Då syns
  skillnaden mellan tjugo minuter i ett kalkylark och tjugo minuter på YouTube, fast båda var "Safari".
- En svensk startindelning i kategorier: arbete, kommunikation, AI-verktyg, planering,
  privat och konsumtion. Efter ett par dagar går Claude igenom den tid som saknar kategori
  tillsammans med dig och skriver regler för just dina projekt och kunder.
- En veckorapport som öppnas i webbläsaren söndag kväll: aktiv tid, tid per dag, per
  kategori, toppappar och toppsajter, jämfört med veckan innan.
- Kommandot `/tidskoll` i Claude Code. Fråga "vart tog tiden vägen i tisdags?" eller
  "hur mycket tid la jag på mejl den här veckan?".

Bara tid när du faktiskt sitter vid datorn räknas. Står den orörd räknas tiden som borta.

**Skärmdumpsnivån** är valfri. Den tar en bild av skärmen var femte sekund i låg upplösning,
glesare när inget ändras och inte alls när du är borta. När du kör `/tidskoll analysera` tittar Claude på de 10 till 30
bilder som säger mest om dagen och letar efter mönster: menyer där ett kortkommando finns,
samma kopiera och klistra in om och om igen, ett verktyg som har ett bättre alternativ.
Ett mönster blir ett förslag först när det setts tre gånger. `/tidskoll effektivisera`
ger de förslag som sparar mest tid per vecka.

## Integritet

Grundnivån sparar appnamn, fönstertitlar och adresser i ActivityWatch på din dator.

Skärmdumpsnivån fotar allt som syns på skärmen, även privata meddelanden. Bilderna sparas
i `~/tidskoll/skarm/` och raderas efter 30 dagar. Det som lämnar datorn är det Claude läser
när du ber om en analys: loggrader och de utvalda bilderna. De skickas till Anthropic som
allt annat du visar Claude.

Pauslistan `~/tidskoll/pauslista.txt` stoppar skärmdumpar från lösenordshanterare,
BankID, banker, betalsidor och myndigheter från början. Lägg till egna rader, en per app
eller adress. Pausa allt med `/tidskoll paus` och starta igen med `/tidskoll fortsatt`.

## Var allt ligger

```
~/tidskoll/
├── bin/                skripten
├── kategorier.json     dina kategoriregler
├── rapporter/          veckorapporterna
├── pauslista.txt       där inga skärmdumpar tas
├── skarm/days/         skärmdumpar och logg per dag (skärmdumpsnivån)
├── anteckningar/       Claudes dagsanteckningar
└── observationer.md    återkommande mönster
```

## Ta bort

`bash installera.sh avinstallera` stoppar allt och tar bort skripten, appen och skillen.
Din data i `~/tidskoll/` och ActivityWatch själv ligger kvar tills du tar bort dem.

## Tack

Skärmdumpsdelen bygger på [screenwatch-kit](https://github.com/tabani-png/screenwatch-kit)
av Muhammad Ali (MIT-licens): idén med en kompilerad app som bär behörigheten,
upptagningsloopen och metoden att läsa metadata först och bilder sedan.
Tidmätningen är [ActivityWatch](https://github.com/ActivityWatch/activitywatch) (MPL-2.0),
som installeras separat och inte ingår här.
