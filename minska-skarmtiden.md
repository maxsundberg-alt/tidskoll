# Minska skärmtiden

Tidskoll visar vart tiden går. Den här guiden handlar om nästa steg, att ändra det.

Det som hjälper mest är att göra det svårt att hamna där. En sajt som inte går att öppna
behöver du inte stå emot, och ett flöde som inte syns lockar inte. Mät sedan om det höll.
En blockering som inte fungerar märks först i siffrorna.

Verktygen nedan är ordnade från hårdast till mjukast. De flesta behöver en blandning.

## 1. Blockera sajten helt

För sajter du inte behöver alls: video, sociala medier, nyheter och forum.

Tidskoll kan blockera sajter i alla webbläsare på datorn samtidigt, även i inkognitoläge och
i webbläsare du installerar senare. Det sker i datorns egen adressbok för webbsidor, där
sajterna pekas mot en adress som inte finns. Be din agent installera blockeringen.

Att öppna en blockerad sajt igen kräver datorns lösenord varje gång. Det är meningen: att
öppna en sajt ska kräva att du bestämmer dig.

Blockeringen gäller bara datorn. För telefonen, se avsnitt 4.

## 2. Dölj flödet och behåll sajten

För sajter du behöver i jobbet men där flödet äter tid. LinkedIn är det vanligaste exemplet:
du behöver meddelanden och profiler, men inte flödet.

**Tidskolls eget skript** döljer flödet på LinkedIns startsida och lämnar resten av sajten
orörd. Det körs i Safari på Mac och iPhone via den kostnadsfria appen Userscripts. Se
[dolj-floden/README.md](dolj-floden/README.md). Fler sajter går att lägga till som egna skript
i samma mapp, och din agent kan skriva dem åt dig.

**SocialFocus** är ett färdigt webbläsartillägg som döljer utvalda delar av många sajter,
till exempel flöden, rekommendationer, siffror och annonser. Det fungerar bland annat på LinkedIn,
YouTube, X, Instagram, Reddit, Facebook och Gmail, och finns för Safari (via App Store) och för
Chrome och Firefox. Safari-versionen kostar en engångssumma, och det finns en dyrare
Pro-version. Det fungerar bara i webbläsaren. I apparna gör det ingenting. Ett sätt att
använda det är att ha det påslaget hela tiden och bara stänga av det när du ska göra något
som kräver flödet.

## 3. Lägg in en paus

För appar och sajter du inte vill blockera helt men öppnar av ren vana.

**One Sec** visar en kort paus och frågar om du verkligen vill fortsätta innan en app eller
sajt öppnas. Pausen räcker ofta för att impulsen ska hinna gå över. Den finns för iPhone,
Android och Mac (macOS 14 eller senare), och som webbläsartillägg. Grundversionen är gratis,
och det finns en betalversion.

## 4. Telefonen

Blockeringen i avsnitt 1 gäller bara datorn. På telefonen:

- **Skärmtid**, som finns inbyggt i iPhone och Mac: tidsgränser per app eller kategori, och
  under Innehåll och integritet en spärr för vuxensajter som gäller i alla webbläsare.
- **One Sec** för apparna du öppnar av vana.
- Flytta apparna från hemskärmen. Det som inte syns öppnas mer sällan.

## Vanliga fel

- **Privat reläservice (iCloud Private Relay) kringgår blockeringen i Safari.** Trafiken går
  via Apples egna servrar, och då används aldrig datorns adressbok. Går en blockerad sajt ändå att
  öppna i Safari är det nästan alltid det här. Inställningen finns under Systeminställningar →
  ditt namn högst upp → iCloud → Privat reläservice.
- **Flikar som redan var öppna fortsätter fungera en stund** efter att blockeringen slagits
  på. Avsluta webbläsaren helt (Cmd+Q) och prova med en sajt som inte var öppen.
- **Underdomäner räknas för sig.** Tidskoll lägger till `www.` och `m.` automatiskt, men till
  exempel `music.youtube.com` och `se.pinterest.com` måste stå på egna rader i listan.
- **En blockerad flik kan räknas som tid på sajten.** Veckorapporten försöker skilja en felsida
  från en sajt som faktiskt laddades, men det fungerar säkert bara i Safari på engelska. Ser
  siffran konstig ut, fråga din agent.
- **Undantag blir lätt permanenta.** En sajt som öppnas för en kväll förblir öppen tills någon
  blockerar den igen. Be din agent visa vilka sajter som är öppnade då och då.

## Mät att det håller

Veckorapporten har ett avsnitt om blockerade sajter: hur mycket tid som gick till dem trots
blockeringen, och vilka sajter det gällde. Står det att ingen blockerad sajt laddades
fungerar blockeringen. Står det något annat är blockeringen avstängd, sajten tillfälligt
öppnad, eller så kringgår något blockeringen. Börja i så fall med Privat reläservice.
