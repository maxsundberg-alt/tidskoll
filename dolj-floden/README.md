# Dölja flöden

Skript som döljer flöden på sajter du behöver men inte vill fastna i. Sajten fungerar som
vanligt i övrigt. De körs i Safari på Mac och iPhone med appen
[Userscripts](https://apps.apple.com/app/userscripts/id1463298887), som är gratis och har
[öppen källkod](https://github.com/quoid/userscripts).

Just nu finns ett skript, för LinkedIn (`linkedin-dolj-flode.user.js`). Det döljer
inläggsflödet på startsidan. Rutan för att skriva inlägg, meddelanden, profiler och alla andra
sidor fungerar som vanligt, och där flödet brukade vara står "Flödet är dolt."

Skripten påverkar bara webbsidorna i Safari. LinkedIns app på telefonen påverkas inte.

## Så kommer skriptet igång

Be din agent installera det. Skriptet läggs i mappen Userscripts i iCloud Drive, så att samma
fil används på Mac och iPhone.

Resten gör du själv, eftersom det är inställningar i Safari:

**Mac**
1. Installera Userscripts från App Store och öppna appen.
2. Välj mappen Userscripts i iCloud Drive som skriptmapp.
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

Be din agent skriva ett skript för en annan sajt. Det hamnar i samma mapp, och sedan tillåter
du den nya sajten i Userscripts.
