# Minska skärmtiden

Tidskoll visar vart tiden går. Den här guiden handlar om nästa steg: att ändra det.

Principen är att ta bort ytan i stället för att förlita sig på viljestyrka. En sajt som inte
laddar behöver man inte stå emot. Ett flöde som inte syns lockar inte. Sedan mäter du om det
höll, för en spärr som läcker märks inte förrän man tittar i siffrorna.

Verktygen nedan är ordnade från hårdast till mjukast. De flesta behöver en blandning.

## 1. Blockera sajten helt

För sajter du inte behöver alls: video, sociala medier, nyheter, forum.

Tidskoll kan blockera sajterna i `~/tidskoll/blocklista.txt` i alla webbläsare på datorn
samtidigt, även inkognito och webbläsare du installerar senare. Det sker i `/etc/hosts`,
datorns egen adressbok, där sajterna pekas mot en adress som inte finns. Be din agent
installera blockeringen, eller kör `bash installera.sh blockera`.

Att öppna en sajt kräver lösenordet varje gång (`blockera.sh lyft <sajt>`). Den friktionen
är poängen. Det ska vara ett beslut, inte en reflex.

Blocket når inte telefonen och inte appar som har en egen väg till nätet. Se avsnitt 4.

## 2. Dölj flödet men behåll sajten

För sajter du behöver i jobbet men där flödet äter tid. LinkedIn är det vanligaste
exemplet: du behöver meddelanden och profiler, men inte flödet.

**SocialFocus** är ett webbläsartillägg som döljer utvalda delar av sajter: flöden,
rekommendationer, siffror och annonser. Det täcker bland annat LinkedIn, YouTube, X,
Instagram, Reddit, Facebook och Gmail, och finns för Safari (via App Store) samt Chrome och
Firefox. Safari-versionen kostar en engångssumma, med en betald Pro-nivå ovanpå. Det fungerar
bara i webbläsaren, inte i apparna. Ett sätt att använda det: ha det påslaget som standard,
och stäng av det bara när du ska göra något som kräver flödet.

## 3. Lägg in en paus

För appar och sajter du inte vill stänga helt men öppnar av ren vana.

**One Sec** lägger in en kort paus, och en fråga om du verkligen vill, innan en app eller
sajt öppnas. Pausen räcker ofta för att impulsen ska hinna gå över. Den finns för iPhone,
Android och Mac (macOS 14 eller senare), och som webbläsartillägg. Grunden är gratis, och
det finns en betalversion.

## 4. Telefonen och apparna

Blocket i avsnitt 1 gäller bara datorn. På telefonen:

- **Skärmtid** (inbyggt i iPhone och Mac): tidsgränser per app eller kategori, och under
  Innehåll och integritet en spärr för vuxensajter som gäller i alla webbläsare.
- **One Sec** på telefonen för apparna du öppnar av vana.
- Flytta apparna från hemskärmen. Det som inte syns öppnas mer sällan.

## Fallgropar

- **iCloud Private Relay går runt blocket i Safari.** Trafiken går via Apples relä och läser
  aldrig `/etc/hosts`. Laddar en blockerad sajt ändå i Safari är det nästan alltid det här.
  Inställningen finns under Systeminställningar → Apple-konto → iCloud → Private Relay.
- **Redan öppna flikar laddar en stund till** efter att blocket slagits på. Avsluta
  webbläsaren helt (Cmd+Q) och prova på en sajt som inte var öppen.
- **Underdomäner räknas för sig.** Tidskoll lägger till `www.` och `m.` automatiskt, men till
  exempel `music.youtube.com` och `se.pinterest.com` måste stå i listan på egna rader.
- **En öppen flik är inte samma sak som en sajt som laddade.** En blockerad sajt som ligger
  framme visar en felsida, och den tiden mäts ändå. Veckorapporten skiljer på de två genom
  sidtiteln: Safari skriver "Failed to open page" och Chrome visar bara adressen.
- **Tillfälliga undantag blir lätt permanenta.** En sajt som öppnas "för en kväll" ligger
  kvar tills någon stänger den. Kolla `blockera.sh status` då och då, eller be din agent göra det.

## Mät att det håller

Veckorapporten har en rad om blockerade sajter: hur mycket tid som gick till dem trots
blocket, och vilka sajter det gällde. Står det noll fungerar blocket. Står det något är
blocket av, sajten är öppnad som undantag, eller så går något runt blocket. Börja i så fall
med Private Relay.
