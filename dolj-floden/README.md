# Dölja flöden

Skript som döljer flöden på sajter du behöver men inte vill fastna i. Sajten fungerar som
vanligt i övrigt. De körs i Safari på Mac och iPhone med appen
[Userscripts](https://apps.apple.com/app/userscripts/id1463298887), som är gratis och har
[öppen källkod](https://github.com/quoid/userscripts).

| Skript | Vad det gör |
|---|---|
| `linkedin-dolj-flode.user.js` | Döljer inläggsflödet på LinkedIns startsida. Rutan för att skriva inlägg, meddelanden, profiler och alla andra sidor fungerar som vanligt. Där flödet brukade vara står "Flödet är dolt." |

Skripten påverkar bara webbsidorna i Safari. LinkedIns app på telefonen påverkas inte.

## Så kommer skriptet igång

Be din agent installera det, eller kör `bash installera.sh floden` i den nedladdade
Tidskoll-mappen.
Skriptet läggs i mappen `Userscripts` i iCloud Drive, så att samma fil används på Mac och iPhone.
Saknas iCloud Drive läggs det i `~/tidskoll/userscripts`.

Resten gör du själv, eftersom det är inställningar i Safari:

**Mac**
1. Installera Userscripts från App Store och öppna appen.
2. Välj mappen där skriptet ligger som skriptmapp.
3. Safari → Inställningar → Tillägg: kryssa i Userscripts.
4. Öppna linkedin.com, klicka på Userscripts-ikonen bredvid adressfältet och tillåt sajten.

**iPhone**
1. Installera Userscripts från App Store och välj samma mapp i iCloud Drive.
2. Inställningar → Appar → Safari → Tillägg: slå på Userscripts och tillåt linkedin.com.
3. I Filer-appen: håll fingret på mappen och välj "Behåll nedladdad", annars kan iOS ta bort
   skriptet från telefonen för att spara plats.

## Om något slutar fungera

LinkedIn byter ofta namn på delarna av sidan. Skriptet bygger på den del som brukar ändras
minst, men visas flödet igen är det troligen där det har hänt något. Be din agent öppna
linkedin.com, titta på hur sidan är uppbyggd nu och uppdatera skriptet.

Har du redan ett annat tillägg som döljer flöden, till exempel SocialFocus, kan de krocka.
Stäng av det andra för samma sajt.

## Fler sajter

Varje sajt får en egen fil i samma mapp. Be din agent skriva en ny med det här skriptet som
mall. Det som behöver bytas är `@match` (vilken sajt), hur startsidan känns igen och vilka
delar av sidan som ska döljas.
