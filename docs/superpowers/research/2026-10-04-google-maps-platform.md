# Google Maps Platform för `bok`: villkor, Routes, Street View, Places och pris

Fetched 2026-10-04. Endast primärkällor (cloud.google.com/maps-platform/terms*, cloud.google.com/terms/maps-platform/*, developers.google.com/maps/*, about.google). Citat är ordagranna på engelska. Developer-sidornas inledande "Page Summary"-rutor är autogenererade sammanfattningar. Jag har inte citerat dem som normtext.

Villkorsversioner som gällde vid hämtningen:

| Dokument | URL | Senast ändrad (enligt sidan) |
|---|---|---|
| Google Maps Platform Terms of Service ("ToS") | https://cloud.google.com/maps-platform/terms | August 26, 2026 |
| Service Specific Terms ("SST") | https://cloud.google.com/maps-platform/terms/maps-service-terms | June 10, 2026 |
| **EEA** Terms of Service ("EEA-ToS") | https://cloud.google.com/terms/maps-platform/eea | August 26, 2026 |
| **EEA** Service Specific Terms ("EEA-SST") | https://cloud.google.com/terms/maps-platform/eea/maps-service-terms | June 10, 2026 |
| Places API EEA Permitted Uses | https://cloud.google.com/terms/maps-platform/eea-places-api-permitted-uses | June 4, 2025 |

**Viktigt för svenska användare:** har användarens billing account en adress i EES (Sverige ingår) gäller EEA-ToS och EEA-SST i stället för de globala villkoren (se A.0). Båda varianterna redovisas nedan.

---

## Sammanfattning

Juridisk bedömning gjord av en icke-jurist utifrån villkorstexten. Det här är inte juridisk rådgivning.

| Planerad användning | Bedömning |
|---|---|
| 1a. Räkna ut restid och avstånd (gång, cykel, bil, kollektivt) på begäran och **visa** det för författaren i terminalen | **OK** (med "Google Maps"-attribution och beta-varning för gång och cykel) |
| 1b. Låta verktyget **skriva API-resultatet** (t.ex. "23 min", distanceMeters, polyline) till bokens filer permanent | **Förbjudet** enligt ordalydelsen: "No Caching". För Routes får bara lat/lng cachas i 30 dagar, och place_id får sparas |
| 1c. Spara bara **frågan** (från, till, färdsätt, tid) och räkna om vid behov | **OK** |
| 1d. Författaren skriver själv en egen, avrundad formulering i prosan ("en dryg kvart på cykel") efter att ha sett svaret | **Gråzon, låg risk.** Ingen klausul tar upp det. Strikt läst kan "create content based on Google Maps Content" träffa även detta |
| 2a. Street View-**metadata** (datum, pano_id, copyright) för att visa hur gamla bilderna är | **OK.** Gratis och ingen kvot. pano_id får sparas, men datumet bör bara visas, inte lagras |
| 2b. Låta Claude **titta på Street View-bilder** och skriva miljöbeskrivningar som sparas i boken | **Troligen förbjudet (mörk gråzon).** Ingen klausul nämner exakt detta, men flera talar emot det: "No Creating Content From Google Maps Content", "No Scraping … for use outside the Services" och AI-klausulen. Google har dessutom behövt skriva ett uttryckligt *undantag* för att LLM-output från Maps-innehåll ska vara tillåten (Grounding Lite). Undantaget gäller inte Street View och tillåter inte permanent lagring |
| 2c. Spara Street View-bilder i boken | **Förbjudet** (No Caching/No Scraping. Geo Guidelines säger dessutom att Street View inte får användas i böcker) |
| 3. Places "Search Along Route" för att hitta vad som finns längs vägen | **Globalt: gråzon** så länge resultatet bara visas. Att spara namn och adresser är uttryckligen förbjudet. **I EES: troligen inte tillåtet.** Där får Places-innehåll bara användas för nio uppräknade ändamål, och en romanskrivares research passar inte tydligt in |
| Historik (1975 eller 1990) | Går inte via API:erna. Routes tar emot passerade tider bara för TRANSIT, och då högst 7 dagar bakåt. Street View-API:et har ingen dokumenterad parameter för att välja äldre bilder. Allt är "dagens värld" |
| Egen nyckel per användare och open source-verktyg | Det finns ingen särskild klausul om open source eller personligt bruk. Varje användare är själv "Customer" i sitt eget Cloud-projekt och bunden av villkoren |

---

## A. Villkor

### A.0 Vilka villkor gäller? EES eller globalt

ToS (https://cloud.google.com/maps-platform/terms), inledningen under "Google Maps Platform Terms of Service":

> "If Customer's billing account address is in the European Economic Area, the Google Maps Platform EEA Terms of Service (as described at https://cloud.google.com/terms/maps-platform/eea) ("EEA TOS"), will govern Customer's access to and use of the Services. However, to the extent that a Customer's project integration existing prior to July 8, 2025 remains in an unmodified state, such project integration will continue to be governed by the terms of this Agreement, and not the EEA TOS."

EEA FAQ (https://developers.google.com/maps/comms/eea/faq), "EEA countries, territories, & regions": listan innehåller "Sweden". Under "What updates are we making to our Terms of Service?":

> "This version removes three provisions from the "Restrictions Against Misusing the Services" section of your Agreement: No Re-Creating Google Products or Features; No Use with Non-Google Maps; No Use in Embedded Vehicle Systems"
>
> "(2) Clarified restrictions on using Google Maps Content for AI/ML by adding a new example."

Definitionen av innehållet som allt detta gäller är densamma i båda: "Google Maps Content" means any content provided through the Services (whether created by Google or its third-party licensors), including map and terrain data, imagery, traffic data, and places data (including business listings). (ToS, Definitions. EEA-ToS, Definitions.)

En restid, ett avstånd, en Street View-bild och ett platsnamn från API:erna är alltså alla "Google Maps Content".

### A.1 Missbruksbegränsningarna: global ToS §3.2.3

ToS, §3.2 "License Requirements and Restrictions": *"In this Section 3.2 …, the phrase "Customer will not" means "Customer will not, and will not permit a third party to"."*

ToS **§3.2.3 "Restrictions Against Misusing the Services"**, ordagrant:

> **(a) No Scraping.** Customer will not export, extract, or otherwise scrape Google Maps Content for use outside the Services. For example, Customer will not: (i) pre-fetch, index, store, reshare, or rehost Google Maps Content outside the services; (ii) bulk download Google Maps tiles, Street View images, geocodes, directions, distance matrix results, roads information, places information, elevation values, and time zone details; (iii) copy and save business names, addresses, or user reviews; or (iv) use Google Maps Content with text-to-speech services.
>
> **(b) No Caching.** Customer will not cache Google Maps Content except as expressly permitted under the Maps Service Specific Terms.
>
> **(c) No Creating Content From Google Maps Content.** Customer will not create content based on Google Maps Content. For example, Customer will not: (i) trace or digitize roadways, building outlines, utility posts, or electrical lines from the Maps JavaScript API Satellite base map type; (ii) create 3D building models from 45° Imagery from Maps JavaScript API; (iii) build terrain models based on elevation values from the Elevation API; (iv) use latitude/longitude values from the Places API as an input for point-in-polygon analysis; (v) construct an index of tree locations within a city from Street View imagery; (vi) convert text-based driving times into synthesized speech results; or (vii) use Google Maps Content to improve machine learning and artificial intelligence models, including to train, test, validate or fine-tune the models.
>
> **(d) No Re-Creating Google Products or Features.** Customer will not use the Services to create a product or service with features that are substantially similar to or that re-create the features of another Google product or service. Customer's product or service must contain substantial, independent value and features beyond the Google products or services. For example, Customer will not: (i) re-distribute the Google Maps Core Services or pass them off as if they were Customer's services; (ii) use the Google Maps Core Services to create a substitute of the Google Maps Core Services, Google Maps, or Google Maps mobile apps, or their features; (iii) use the Google Maps Core Services in a listings or directory service or to create or augment an advertising product; (iv) combine data from the Directions API, Geolocation API, and Maps SDK for Android to create real-time navigation functionality substantially similar to the functionality provided by the Google Maps for Android mobile app.
>
> **(e) No Use With Non-Google Maps.** To avoid quality issues and/or brand confusion, Customer will not use the Google Maps Core Services with or near a non-Google Map in a Customer Application. For example, Customer will not (i) display or use Places content on a non-Google Map, (ii) display Street View imagery and non-Google Maps on the same screen, or (iii) link a Google Map to non-Google Maps Content or a non-Google Map.
>
> **(f) No Use in Embedded Vehicle Systems.** …
>
> **(g) No Modifying Search Results Integrity.** Customer will not modify any of the Google Maps Core Services' search results.

Övriga relevanta krav i ToS:

- **§3.2.2(a)(i):** *"The Customer Application's terms of service will (A) notify users that the Customer Application includes Google Maps features and content; and (B) state that use of Google Maps features and content is subject to the then-current versions of the: (1) Google Maps End User Additional Terms of Service at https://maps.google.com/help/terms_maps/; and (2) Google Privacy Policy at https://policies.google.com/privacy."*
- **§3.2.2(b) Attribution:** *"Customer will display all attribution that (i) Google provides through the Services (including branding, logos, and copyright and trademark notices); or (ii) is specified in the Maps Service Specific Terms. Customer will not modify, obscure, or delete such attribution."*
- **§3.2.1(c)(ii)(1):** Kunden får inte använda tjänsterna *"in a manner intended to: (1) avoid incurring Fees"*.
- **Definitions:** *""Customer Application" means any web page or application (including all source code and features) that has material value independent of the Services and is owned or controlled by Customer, or that Customer is authorized to use."*

### A.2 Samma begränsningar i EEA-ToS §3.3.2

EEA-ToS (https://cloud.google.com/terms/maps-platform/eea), **§3.3.2 "Restrictions Against Misusing the Services"**, ordagrant:

> **(a) No Scraping.** Customer will not export, extract, or otherwise scrape Google Maps Content for use outside the Services. For example, Customer will not: (i) pre-fetch, index, store, reshare, or rehost Google Maps Content outside of the Services; (ii) bulk download Google Maps Content; or (iii) copy and save business names, addresses, or user reviews.
>
> **(b) No Caching.** Customer will not cache Google Maps Content except as expressly permitted under the Maps Service Specific Terms.
>
> **(c) No Creating Content From Google Maps Content.** Customer will not create content based on Google Maps Content. For example, Customer will not: (i) trace or digitize roadways, building outlines, utility posts, or electrical lines from the Maps JavaScript API Satellite base map type **or from Street View imagery**; (ii) create 3D building models from 45° Imagery from Maps JavaScript API; (iii) build terrain models based on elevation values from the Elevation API; (iv) use latitude/longitude values from the Places API as an input for point-in-polygon analysis; or (v) use Google Maps Content to improve machine learning and artificial intelligence models, including to train, test, validate or fine-tune the models.
>
> **(d) No Modifying Search Results Integrity.** …

(Fetstilen är min.) I EES finns alltså **inte** "No Re-Creating", "No Use With Non-Google Maps" eller "No Use in Embedded Vehicle Systems". Övriga krav: §3.2.2 (samma krav på användarvillkor som global §3.2.2(a)), §3.2.4 "Attribution and Notices" och §3.2.5 *"Customer will comply with the Documentation in connection with using the Services."*

EEA-SST, A.2 "Attribution", lägger till: *"Customer will not misrepresent Google or create confusion as to the source or placement of the content in a Customer Application. If Customer uses the Services with third-party products or services in its Customer Application, Customer is responsible for making it clear to the End User what is Google Maps Content and what content is not from Google."*

### A.3 Cachning: vad får sparas?

**Generellt: bara Google-ID:n.** SST, A.3 "Google ID Caching" (identisk i EEA-SST A.3):

> "Customer may cache the Google ID values from the Services that return such field and allow caching, in accordance with its Documentation. For example, Customer may cache (a) place_id from Places API, Directions API, Geolocation API and Routes API, (b) pano_ID, from Street View Static API, and (c) video_ID from Aerial View API."

**Routes API.** SST §19 "Routes API":

> "19.1 Use without a Google Map. Customer may use Google Maps Content from the Routes API in Customer Applications without a corresponding Google Map."
> "19.2 No use with a non-Google map. Customer must not use Google Maps Content from the Routes API in conjunction with a non-Google map."
> "19.3 Caching. Customer may temporarily cache latitude (lat) and longitude (lng) values from the Routes API for up to 30 consecutive calendar days, after which Customer must delete the cached latitude and longitude values."

EEA-SST §20 "Routes API":

> "20.1 No Use With any Map. Customer may not use description or steps from the Routes API With any Map."
> "20.2 Caching. Customer may temporarily cache latitude and longitude values from the Routes API for up to 30 consecutive calendar days, after which Customer must delete the cached latitude and longitude values."

(EEA-SST, avsnitt B: *""With any Map" means to (1) display Google Maps Content on, next to, or in a manner that is visually associated with any map, including a Google Map; or (2) link Google Maps Content to any map …"*)

**Legacy Directions och Distance Matrix.** SST §4.3: *"Customer may temporarily cache latitude and longitude values from the Directions API for up to 30 consecutive calendar days…"*. SST §5 (Distance Matrix) har **ingen** cachningsklausul alls, bara §5.1/5.2 om kartor. EEA-SST §4.2 är lika för Directions. EEA-SST §5.1 säger: *"Customer may not use (in whole or in part) any addresses or steps from the Distance Matrix API With any Map."*

**Slutsats om restider:** Varken SST eller EEA-SST tillåter att man cachar **duration** eller **distance** från Routes, Directions eller Distance Matrix. Det enda som får sparas i 30 dagar är lat/lng. Som jämförelse tillåter SST §11.8 (Navigation Connect API) uttryckligen *"latitude (lat), longitude (lng), distance, duration, time, and estimated time of arrival values for up to 30 consecutive calendar days"*. Google skriver alltså ut duration och distance när de menar att de ska få cachas, och det gör de inte för Routes. Att permanent skriva "23 min" från API:et i en fil är därmed cachning eller lagring som inte är tillåten.

**Routes policy-sidan** (https://developers.google.com/maps/documentation/routes/policies, "Exceptions from caching restrictions"): *"Note that the place ID, used to uniquely identify a place, is exempt from the caching restrictions. You can therefore store place ID values indefinitely."*

### A.4 AI, ML och LLM: alla klausuler jag hittade

1. **ToS §3.2.3(c)(vii)** och **EEA-ToS §3.3.2(c)(v)**: *"use Google Maps Content to improve machine learning and artificial intelligence models, including to train, test, validate or fine-tune the models."* Formuleringen gäller träning och förbättring, inte inferens. Kom ihåg att "Customer will not" också betyder "will not permit a third party to" (ToS §3.2 och EEA-ToS §3.3). Om AI-leverantören tränar på det som skickas in träffar klausulen alltså även kunden.

2. **Maps Grounding Lite** (SST §10, EEA-SST §11). Det här är den enda platsen där villkoren uttryckligen behandlar LLM-genererad text från Maps-innehåll. SST §10.1–10.3:

   > ""Grounded Output" means output created when Google Maps Content is combined with the output of any LLM."
   > ""Large Language Model" or "LLM" means a generative artificial intelligence model trained on large datasets to recognize, summarize, translate, predict, and generate text or other content in response to user-provided prompts or queries."
   > "10.2 Permitted Use. For clarity, Google Maps Content contained in Grounded Output remains subject to use restrictions applicable to Google Maps Content in the Agreement, including the prohibition on model training. As a limited exception:"
   > "10.2.1 **to the prohibition on using Google Maps Content to create content**, Customer may use the Maps Grounding Lite API to ground a LLM to generate and display Grounded Output to End Users if (i) Customer complies with the Generative AI Prohibited Use Policy … and (ii) Customer includes associated Google Maps source links with the Grounded Output;"
   > "10.2.2 to the prohibition on caching or storing Google Maps Content, Customer may cache Grounded Output for up to thirty (30) consecutive days solely for the purpose of evaluating and optimizing the performance or display of the Grounded Output for the Customer Application."
   > "10.3.1 attempt to extract or otherwise separate Google Maps Content from the Grounded Output;"
   > "10.3.2 use Grounded Output to train, develop, or improve any machine learning models or artificial intelligence systems;"
   > "10.3.3 modify or intersperse content with the Grounded Output, …"

   (Fetstilen är min.) **Tolkning:** Google behövde ett "limited exception" till förbudet mot att skapa innehåll för att en LLM ska få generera text från Maps-innehåll. Utan undantaget räknar Google alltså LLM-text som bygger på Google Maps Content som "create content based on Google Maps Content". Undantaget gäller bara Grounding Lite. Det kräver källänkar, och även där får output cachas högst 30 dagar och bara för utvärdering. Det ger inget stöd för att permanent spara AI-skriven text i ett manus. Det gäller heller inte Street View.

3. **Grounding Lite-dokumentationen** (https://developers.google.com/maps/ai/grounding-lite, "Requirements for Compatible LLMs"):

   > "You may only use Maps Grounding Lite with an LLM that is compliant with the Google Maps Platform Terms of Service. For example, you are responsible for ensuring that Google Maps Content is not cached by, stored by, or used to improve the LLM that you choose to use. … You must not use Maps Grounding Lite with any models that use the data input into the model for any model training or improvement."

   Texten gäller formellt Grounding Lite. Den visar ändå hur Google läser huvudvillkoren när Maps-innehåll skickas till en LLM: innehållet får inte cachas, lagras eller användas för träning hos LLM-leverantören.

4. **Google Earth / "Ask Google Earth"** (SST §8.4) är inte relevant för bok.

Jag hittade ingen klausul som generellt **tillåter** att man skickar Google Maps Content (t.ex. Street View-bilder) till en tredjeparts-LLM för inferens. Jag hittade heller ingen som uttryckligen **förbjuder** just inferens. Förbudet följer i så fall av §3.2.3(a) ("for use outside the Services") och §3.2.3(c) ("create content based on").

### A.5 Street View Static API: policyer

- **SST:** Det globala SST har inget eget Street View-avsnitt. Det enda som nämns är pano_ID i A.3, och pano_ID får cachas.
- **EEA-SST §22.1:** *"Customer may not use any Google Maps Content from the Street View Static API With any Map."*
- **Policy-sidan** (https://developers.google.com/maps/documentation/streetview/policies), "Exceptions from caching restrictions": *"The panorama ID, used to uniquely identify a Street View panorama, is exempt from the caching restriction. Therefore, you can store panorama ID values indefinitely."*
  - **Motsägelse i dokumentationen:** Request-sidan (https://developers.google.com/maps/documentation/streetview/request-streetview, "Required parameters") säger: *"Panoramas may change ID over time, so don't persist this ID. Instead, save the location address or latitude and longitude coordinates so you can refresh the panorama ID."* Att lagra pano_id är alltså tillåtet, men det rekommenderas inte rent tekniskt.
- **Attribution** (samma policy-sida, "Display Google Maps attribution"): *"You must follow Google Maps attribution requirements when displaying Content from Google Maps Platform APIs in your app or website."* Under "Google Maps logo and text attribution": *"Attribution should take the form of the Google Maps logo whenever possible. In cases where space is limited, the text Google Maps is acceptable. It must always be clear to end users which content is provided by Google Maps."* Under "Text attribution": *"Don't localize Google Maps into another language."*
- **Tillfällig nedladdning för visning:** Varken ToS eller policy-sidan definierar "cache" och ingen av dem tar uttryckligen upp transient nedladdning. En bild måste hämtas för att kunna visas, och det är tjänstens normala funktion. Det som är förbjudet är att *lagra* den: ToS §3.2.3(a)(i) "store … outside the services" och (ii) "bulk download … Street View images". **Ej bekräftat:** någon uttrycklig gräns för hur länge en temporärfil får ligga.
- **Geo Guidelines** (https://about.google/brand-resource-center/products-and-services/geo-guidelines/, "Street View – Print"): *"Street View imagery may not be used for any print purposes. This includes: Books, guidebooks, and textbooks …"*. Riktlinjerna gäller Google Maps-produkterna generellt och inte API-avtalet, men de bekräftar att bilderna aldrig får hamna i boken.

### A.6 Places API (New): policyer

- **SST §14** "Places API (Legacy and New)": *"14.1 Use without a Google Map. … 14.2 No use with a non-Google map. … 14.3 Caching. Customer may temporarily cache latitude and longitude values from the Places API for up to 30 consecutive calendar days, after which Customer must delete the cached latitude and longitude values."*
- **EEA-SST §15:** *"15.1 No Use With any Map. Other than latitude, longitude, and place_id, Customer must not use Google Maps Content from the Places API With any Map."* och **"15.2 Permitted Use. Other than latitude, longitude, and place_id, Customer may only use the Google Maps Content from the Places API as permitted by the Places API EEA Permitted Uses."**
- **Places API EEA Permitted Uses** (https://cloud.google.com/terms/maps-platform/eea-places-api-permitted-uses). Kunder i EES *"may only use the Google Maps Content from the Places API within Customer Applications to (collectively, the "Permitted Uses")"*:
  > (1) facilitate address lookup and autocompletion functionalities; (2) display information about Customer's physical stores, offices, or official service points; (3) enable Customers to visualize and manage Places content related to a sales team's customers or opportunities; (4) enable users to associate tasks, notes, or reminders with specific named places within a productivity, chat, personal organization, or note-taking functionality; (5) show information about nearby points of interest (e.g., schools, parks, grocery stores) to provide context for a real estate listing or rental property being viewed by the user; (6) show information about a Place related to a financial transaction; (7) integrate Places as points of interest or objectives within a game; (8) allow users to tag or share a specific Place in their posts, event creations, or shared experiences within a social platform; and (9) allow users to set and monitor location context for their personal smart home routines or IoT device actions.

  Att leta upp vad som finns längs en romanfigurs rutt passar inte tydligt in på någon punkt. Möjligen kan man argumentera för (4), att anteckningar knyts till namngivna platser i en anteckningsfunktion. Det är en tunn tolkning.
- **Places policy-sidan** (https://developers.google.com/maps/documentation/places/web-service/policies), "Exceptions from caching restrictions": *"Note that the place ID … is exempt from the caching restrictions. You can therefore store place ID values indefinitely."* Under "Attribute all content to the content author": *"You must always credit the author when displaying photos or reviews."* Under "Provide direct access to the source content on Google Maps": *"For each photo and review, end-users must always have access to view the individual source photo or review on Google Maps using the provided googleMapsUri."*
- **ToS §3.2.3(a)(iii)** och **EEA-ToS §3.3.2(a)(iii)**: *"copy and save business names, addresses, or user reviews"* är förbjudet. Att skriva in hittade platsnamn och adresser från Places i bokens filer träffar detta direkt.

### A.7 Måste innehållet visas på eller tillsammans med en Google-karta?

Nej. Globalt får Routes, Places och Directions användas utan karta (SST §19.1, §14.1, §4.1: *"may use Google Maps Content … without a corresponding Google Map"*). I EES är det tvärtom: där får man *inte* visa Routes-beskrivningar och steg, Street View Static-innehåll eller Places-innehåll med *någon* karta (EEA-SST §20.1, §22.1, §15.1). En terminal-CLI utan karta uppfyller båda.

### A.8 Personligt bruk, open source och användarens egen nyckel

- Jag hittade **ingen** klausul om personligt eller icke-kommersiellt bruk och ingen om open source-verktyg som anropar API:erna med användarens egen nyckel. ToS nämner "open source" bara om tredjepartskomponenter i Googles tjänster (§ om tredjepartsrättigheter).
- Konsekvens: varje romanförfattare som skapar ett Cloud-projekt och accepterar villkoren är själv "Customer" och ansvarar för att bok används enligt villkoren (ToS §4.1(a): *"ensure that Customer's and its End Users' use of the Services complies with the Agreement"*). bok-projektet distribuerar programvara men levererar inte tjänsten.
- ToS §3.2.2(a)(i) och EEA-ToS §3.2.2 kräver att "Customer Application's terms of service" informerar om Google Maps-innehållet och länkar till Googles slutanvändarvillkor och integritetspolicy. **Ej bekräftat** hur det tillämpas när kund och slutanvändare är samma person. En notis i bok:s dokumentation är billig försäkring.
- Google Cloud AUP, avsnittet "For Google Maps Platform" (https://cloud.google.com/maps-platform/terms/aup), innehåller inget som är specifikt relevant för användningsfallet, utöver allmänna förbud.

### A.9 Samlad bedömning per användning

| Användning | Bedömning | Klausuler |
|---|---|---|
| Visa restid och avstånd i terminalen på begäran | OK | SST §19.1 / EEA-SST §20 (ingen karta krävs). Attribution enligt Routes-policyn. Beta-varning för WALK/BICYCLE (se B) |
| Spara Routes-resultat (duration, distance, polyline) permanent i bokfiler | Förbjudet | ToS §3.2.3(a)(i), (b). SST §19.3 / EEA-SST §20.2 (bara lat/lng i 30 dagar) |
| Spara fråga och place_id, räkna om på begäran | OK | SST A.3, Routes-policyn "Exceptions from caching restrictions" |
| Författarens egna, avrundade prosaformuleringar ("en kvart på cykel") | Gråzon, låg risk | §3.2.3(c) kan läsas brett, men exemplen gäller systematisk datautvinning (digitalisera, indexera, modellera) |
| Street View-metadata: visa datum, spara pano_id | OK | SST A.3, Street View-policyn. Metadata är gratis |
| Claude tittar på Street View-bilder och skriver prosa som sparas i boken | Troligen förbjudet / mörk gråzon | ToS §3.2.3(a) "for use outside the Services", §3.2.3(c), §3.2.3(c)(vii) om leverantören tränar. SST §10.2.1 visar att LLM-output räknas som "create content". EEA-ToS (c)(i) nämner "Street View imagery" |
| Spara Street View-bilder | Förbjudet | ToS §3.2.3(a)(i)–(ii), (b). Geo Guidelines "Street View – Print" |
| Places Search Along Route: visa resultat | Globalt gråzon. EES troligen ej tillåtet | EEA-SST §15.2 och Places EEA Permitted Uses |
| Places: spara platsnamn och adresser i boken | Förbjudet | ToS §3.2.3(a)(iii) / EEA-ToS §3.3.2(a)(iii) |

---

## B. Routes API: tekniskt

Källor: https://developers.google.com/maps/documentation/routes/compute_route_directions och referensen https://developers.google.com/maps/documentation/routes/reference/rest/v2/TopLevel/computeRoutes.

- **Endpoint:** `POST https://routes.googleapis.com/directions/v2:computeRoutes` (referensen, "HTTP request").
- **Nyckel i header:** exemplen använder `-H 'X-Goog-Api-Key: YOUR_API_KEY'` (compute_route_directions). Nyckeln behöver alltså inte ligga i URL:en.
- **Field mask krävs:** *"This method requires that you specify a response field mask in the input. You can provide the response field mask by using URL parameter $fields or fields, or by using an HTTP/gRPC header X-Goog-FieldMask"*. Exempel för produktion: `routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline`. Google avråder från `*` (referensen, metodbeskrivningen).
- **travelMode** (https://developers.google.com/maps/documentation/routes/reference/rest/v2/RouteTravelMode): `DRIVE` (standard), `BICYCLE`, `WALK`, `TWO_WHEELER` ("Two-wheeled, motorized vehicle"), `TRUCK`, `TRANSIT`. Obligatorisk varning: *"WALK, BICYCLE, and TWO_WHEELER routes are in beta and might sometimes be missing clear sidewalks, pedestrian paths, or bicycling paths. You must display this warning to the user for all walking, bicycling, and two-wheel routes that you display in your app."*
- **routingPreference** (referensen): *"You can specify this option only when the travelMode is DRIVE or TWO_WHEELER, otherwise the request fails."* Värdena är `TRAFFIC_UNAWARE` (standard), `TRAFFIC_AWARE` och `TRAFFIC_AWARE_OPTIMAL` (https://developers.google.com/maps/documentation/routes/config_trade_offs, "How to set the traffic level"). Med TRAFFIC_UNAWARE är `duration` lika med `staticDuration`, *"based on road network and average time-independent traffic conditions"*.
- **departureTime och arrivalTime** (referensen, Request body):
  - departureTime: *"If you don't set this value, then this value defaults to the time that you made the request. NOTE: You can only specify a departureTime in the past when RouteTravelMode is set to TRANSIT. Transit trips are available for up to 7 days in the past or 100 days in the future."*
  - arrivalTime: *"This field is ignored when requests specify a RouteTravelMode other than TRANSIT. You can specify either departureTime or arrivalTime, but not both."*
  - Format: RFC 3339, t.ex. `"2014-10-02T15:01:23Z"`.
  - Transit-guiden (https://developers.google.com/maps/documentation/routes/transit-route, "Set parameters for a transit route"): *"up to and including 7 days prior to now; up to and including 100 days after now"* och *"there is no guarantee to provide consistent results for predictions far in advance."*
  - DRIVE i framtiden: config_trade_offs, "Set departure time (optional)": *"Use this property only for traffic aware requests where the departure time needs to be in the future."* och *"The farther ahead you set the departure time into the future, the more consideration is given to historical traffic conditions"*. **Ej bekräftat:** någon uttrycklig övre gräns för DRIVE i framtiden.
  - **Konsekvens:** historiska restider (1975, 1990) går inte att få fram. DRIVE, WALK och BICYCLE kan inte ta en tid bakåt alls, och TRANSIT högst 7 dagar bakåt.
- **trafficModel:** *"only available for requests that have set RoutingPreference to TRAFFIC_AWARE_OPTIMAL and RouteTravelMode to DRIVE"* (referensen).
- **Transit-detaljer** (transit-route): field mask `routes.legs.steps.transitDetails`. Svaret innehåller `stopDetails` (`arrivalStop`/`departureStop` med `name` och `location`, samt `arrivalTime`/`departureTime`), `localizedValues` (tid som text och `timeZone`), `headsign` och `transitLine` (`agencies[]` med `name`, `phoneNumber` och `uri`, samt `name`, `nameShort`, `color`, `textColor` och `vehicle.name.text`). `transitPreferences.allowedTravelModes` tar `BUS`, `SUBWAY`, `TRAIN`, `LIGHT_RAIL` och `RAIL`, och `transitPreferences.routingPreference` tar `LESS_WALKING` eller `FEWER_TRANSFERS`. Transit stöder inte intermediate waypoints. Taxa finns i `routes.travel_advisory.transitFare` och anges *"only … if the API can determine transit fare information for all steps."*
- **Språk och enheter:** `languageCode` (BCP-47). *"When you don't provide this value, the display language is inferred from the location of the route request."* `units` påverkar bara visningsfälten: *"The units of measure used for the route, leg, step distance, and duration are not affected by this value."* (referensen). Lokaliserad text fås med field mask `routes.localizedValues` (https://developers.google.com/maps/documentation/routes/localized-values). ComputeRoutes härleder språk och enheter från origin, medan ComputeRouteMatrix har *"'en-US' and METRIC"* som standard.
- **Waypoints** (https://developers.google.com/maps/documentation/routes/specify_location): *"Place ID (preferred), Latitude/longitude coordinates, Address string …, Navigation point token, Plus Code"*. Adresser *"must first be geocoded by the Routes API"*. Typerna får blandas. Högst 25 intermediate waypoints (referensen). Över 10 räknas som Pro.
- **Polyline** (referensen, PolylineEncoding och PolylineQuality): standard är `ENCODED_POLYLINE`, alternativet är `GEO_JSON_LINESTRING`. Kvaliteten är `OVERVIEW` som standard eller `HIGH_QUALITY`. Search Along Route kräver encoded polyline (se D).
- **Regional täckning:**
  - Sverige (SE) har ⬤ ("good data quality and availability") för Driving, Biking och Walking Directions (https://developers.google.com/maps/coverage, "Country/region coverage for core mapping features"). Sidan anger att *"Some coverage data, such as public transit routes, is not available and doesn't appear in this list."*
  - TWO_WHEELER stöds bara i: AR BD BJ BO BR CL CO CR DZ EC EG GH GT HK HN ID IN KE KH LA LK MM MX MY NG NI PE PH PK PY RW SG TG TH TN TW UG UY VN ZA (https://developers.google.com/maps/documentation/routes/coverage-two-wheeled). **Inte Sverige, och inget EES-land.**
- **computeRouteMatrix** (https://developers.google.com/maps/documentation/routes/compute_route_matrix): `POST https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix`, faktureras per element (origins × destinations).
  - Gränser: *"The number of elements cannot exceed 625 for routes that are not TRANSIT routes."*
  - TRANSIT och TRAFFIC_AWARE_OPTIMAL har en gräns på 100 element.
  - Högst 50 origins och destinations får anges som adress eller place ID.
  - Rate limits (https://developers.google.com/maps/documentation/routes/usage-and-billing): Compute Routes 3 000 QPM, Matrix 3 000 element per minut.

## C. Street View Static API: tekniskt

Källa: https://developers.google.com/maps/documentation/streetview/request-streetview

- **Endpoint:** `https://maps.googleapis.com/maps/api/streetview?parameters`.
- **Obligatoriskt:** `location` (adress eller `lat,lng`; *"searches a 50 meter radius"*) eller `pano`, samt `size` (`{width}x{height}`) och `key`.
- **Storlek:** *"Street View Static API images can be returned in any size up to 640 x 640 pixels."* (https://developers.google.com/maps/documentation/streetview/usage-and-billing, "Image sizes").
- **Valfritt:**
  - `heading` (0–360)
  - `fov` (*"default is 90 … maximum allowed value of 120"*)
  - `pitch` (standard 0, ±90)
  - `radius` (*"default is 50"*, meter)
  - `return_error_code` (*"If set to true, an error message is returned in place of the generic gray image"*, 404 eller 400)
  - `source` (`default` eller `outdoor`; *"outdoor limits searches to outdoor collections … PhotoSpheres are not returned"*)
  - `signature` (*"recommended"*)
- **Nyckel som header?** Dokumentationen visar bara `key=` som query-parameter. Ett eget test (2026-10-04, ingen dokumentation) mot metadata-endpointen med `X-Goog-Api-Key: <ogiltig>` gav *"You must use an API key to authenticate each request"*, samma svar som helt utan nyckel. Med `key=<ogiltig>` blev svaret *"The provided API key is invalid."* **Headern ignoreras alltså. Nyckeln måste ligga i URL:en.** Konsekvens: URL:er får aldrig loggas, skrivas ut eller hamna i tracebacks som AI:n ser.
- **Signatur** (https://developers.google.com/maps/documentation/streetview/digital-signature):
  - *"Depending on your usage, a digital signature - in addition to an API key - may be required to authenticate requests."*
  - *"We strongly recommend that you use both an API key and digital signature, regardless of your usage."*
  - Request-sidan: *"Requests that don't include a digital signature might fail."*
  - Usage and billing, "Authenticate requests": *"Quotas for requests to the Street View Static API are limited unless they are signed."*
  - Signaturen är HMAC-SHA1 med en separat "URL signing secret". Kvoten för osignerade anrop kan sättas i Cloud Console ("Limit unsigned requests").
  - **Ej bekräftat:** den exakta gränsen för osignerade anrop. Dokumentationen anger ingen siffra.
- **Metadata** (https://developers.google.com/maps/documentation/streetview/metadata):
  - Endpoint: `https://maps.googleapis.com/maps/api/streetview/metadata?location=…|pano=…&key=…`, och *"the https:// protocol is required"*.
  - Svaret är JSON med `status`, `copyright` (t.ex. "© 2017 Google"), `date` (t.ex. "2016-05"), `location.lat/lng` och `pano_id`.
  - Status kan vara `OK`, `ZERO_RESULTS`, `NOT_FOUND`, `OVER_QUERY_LIMIT`, `REQUEST_DENIED`, `INVALID_REQUEST` eller `UNKNOWN_ERROR`.
  - Om datumet: *"The date field can have a different granularity for different panoramas. For example, the date field for some panoramas contains a year and month, while for others it contains just the year. The date field is omitted if no data is available."* Datumet kan alltså vara "YYYY-MM", "YYYY" eller saknas helt.
  - **Kostnad:** *"Street View Static API metadata requests are available at no charge. No quota is consumed when you request metadata."* Prislistan anger free cap "Unlimited" för Street View Metadata (se E).
- **Historiska panoramor (time machine):** Varken bild- eller metadata-dokumentationen har någon parameter för att välja datum eller äldre bilder. Jag sökte efter "historic", "older" och "time machine" i alla hämtade Street View-sidor och fick inga träffar. **Bekräftat som frånvaro i dokumentationen, inte som uttryckligt nej.** Man kan teoretiskt ange ett känt äldre `pano`-ID, men API:et har inget sätt att lista äldre panoramor.
- **Länk i stället för API** (https://developers.google.com/maps/documentation/urls/get-started): *"You don't need a Google API key to use Maps URLs."* För Street View fungerar t.ex. `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=LAT%2CLNG&heading=-45&pitch=38&fov=80`, och för vägbeskrivning `https://www.google.com/maps/dir/?api=1&origin=…&destination=…&travelmode=bicycling`.

## D. Places API (New): tekniskt

- **Text Search** (https://developers.google.com/maps/documentation/places/web-service/text-search): `POST https://places.googleapis.com/v1/places:searchText` med `X-Goog-Api-Key` och `X-Goog-FieldMask` (field mask krävs).
  - Högst 20 per sida (`pageSize`; `maxResultCount` är deprecated) och *"a maximum of 60 results across all pages"*.
  - `includedType` filtrerar på typ, och med `strictTypeFiltering` returneras bara den typen.
- **Search Along Route** (https://developers.google.com/maps/documentation/places/web-service/search-along-route): *"Use the searchAlongRouteParameters.polyline.encodedPolyline parameter to pass the route's encoded polyline to Text Search (New) to bias the search results to the route."* och *"Search along route only supports an encoded polyline … This is the Routes API default output."* Man kan också ange en senare startpunkt längs rutten. Jag hittade ingen separat SKU för Search Along Route, så faktureringen följer Text Search-SKU:n enligt fälten.
- **Nearby Search** (https://developers.google.com/maps/documentation/places/web-service/nearby-search): `POST https://places.googleapis.com/v1/places:searchNearby`.
  - `locationRestriction.circle`: *"The radius must be between 0.0 and 50000.0, inclusive."*
  - `includedTypes`, `excludedTypes`, `includedPrimaryTypes` och `excludedPrimaryTypes`.
  - `maxResultCount` *"between 1 and 20 (default)"*.
  - `rankPreference` är `POPULARITY` (standard) eller `DISTANCE`.
- **Fält per SKU-nivå för Text Search** (https://developers.google.com/maps/documentation/places/web-service/data-fields; Nearby har motsvarande nivåer men saknar "IDs Only"-nivån):
  - **Essentials (IDs Only):** `id`, `name` (resursnamn), `attributions`, `consumerAlert`, `movedPlace`, `movedPlaceId`, `nextPageToken`.
  - **Pro:** `displayName`, `formattedAddress`, `shortFormattedAddress`, `location`, `types`, `primaryType`, `primaryTypeDisplayName`, `googleMapsUri`, `googleMapsLinks`, `photos`, `businessStatus`, `viewport`, `addressComponents`, `plusCode`, `timeZone` m.fl.
  - **Enterprise:** `rating`, `userRatingCount`, `regularOpeningHours`, `currentOpeningHours`, telefonnummer, `websiteUri`, `priceLevel`, `priceRange`.
  - **Enterprise + Atmosphere:** `reviews`, `editorialSummary`, `generativeSummary`, `neighborhoodSummary`, `reviewSummary`, `routingSummaries`, serves*-fälten, `outdoorSeating` m.fl.
  - Obs: redan **`displayName` (platsens namn) gör anropet till Pro.**
- **Platstyper** (https://developers.google.com/maps/documentation/places/web-service/place-types): *Table A* kan användas i request (`includedTypes` m.fl., Text Search `includedType`). Exempel är `park`, `historical_landmark`, `cafe` och `train_station`. *Table B* returneras bara i svar.

## E. Pris och kvoter (modellen från mars 2025)

**Ändringen i mars 2025** (https://developers.google.com/maps/billing-and-pricing/march-2025, "Free usage caps"): *"Google has replaced the USD $200 monthly recurring credit with a free monthly usage threshold for each Core Services SKU. The free usage threshold varies for each category."*

**Prislista** (https://developers.google.com/maps/billing-and-pricing/pricing). Priser i USD per 1 000 händelser, gratis tak per månad och SKU. Volymen räknas per billing account och månad.

| SKU | Gratis/mån | Gratis tak–100 000 | 100 001–500 000 |
|---|---|---|---|
| Routes: Compute Routes Essentials | 10 000 | $5.00 | $4.00 |
| Routes: Compute Routes Pro | 5 000 | $10.00 | $8.00 |
| Routes: Compute Routes Enterprise | 1 000 | $15.00 | $12.00 |
| Routes: Compute Route Matrix Essentials/Pro/Enterprise (per element) | 10 000 / 5 000 / 1 000 | $5 / $10 / $15 | $4 / $8 / $12 |
| Static Street View | 10 000 | $7.00 | $5.60 |
| Street View Metadata | Unlimited | – | – |
| Places API Text Search Essentials (IDs Only) | Unlimited | – | – |
| Places API Text Search Pro | 5 000 | $32.00 | $25.60 |
| Places API Text Search Enterprise | 1 000 | $35.00 | $28.00 |
| Places API Text Search Enterprise + Atmosphere | 1 000 | $40.00 | $32.00 |
| Places API Nearby Search Pro / Enterprise / Ent.+Atmosphere | 5 000 / 1 000 / 1 000 | $32 / $35 / $40 | $25.60 / $28 / $32 |

**Vad som utlöser Pro och Enterprise för Compute Routes** (https://developers.google.com/maps/billing-and-pricing/sku-details):

- *Compute Routes Pro*, Triggers: *"Use between 11 and 25 intermediate waypoints; Set "optimizeWaypointOrder": "true"; Set routingPreference to TRAFFIC_AWARE or TRAFFIC_AWARE_OPTIMAL; Set one of the following location modifiers: Side of the road, Heading, Vehicle stopover"*.
- *Compute Routes Enterprise*, Triggers: *"Two-wheeled vehicle routing; Toll calculation; Traffic information on polylines"*.
- Alla SKU:er: *"If you request any features from a higher-priced SKU, then your request is billed at the higher rate. You are only charged for one SKU per request."*
- **TRANSIT finns inte bland triggers för Pro eller Enterprise.** Min slutsats (inte uttryckligen sagt) är att transit utan andra Pro-funktioner faktureras som Essentials.
- Trafikmedvetet (TRAFFIC_AWARE*) blir Pro.

**Street View:** SKU-sidan, "SKU: Static Street View", Notes: *"Use of the Street View Image Metadata endpoint is not charged."*

**Billing krävs.** Routes usage-and-billing: *"To use the Routes API, you must enable billing on each of your projects and include an API key or OAuth token with all API or SDK requests."* Street View usage-and-billing säger samma sak. Kvoter, t.ex. dagliga tak, kan sättas under "Google Maps Platform > Quotas" i Cloud Console (Street View usage-and-billing, "Adjust quota").

**Begränsning av API-nyckeln** (https://developers.google.com/maps/api-security-best-practices):

- "Restrict your API keys": *"Best practice is to always restrict your API keys with one type of application restrictions and one or more API restrictions."*
- "Protect web service API keys": *"Store API keys outside of your application's source code or source tree. If you put your API keys or any other information in environment variables or include files that are stored separately and then share your code, the API keys are not included in the shared files."* och *"also applying IP address restrictions to your web service key will protect it … even if the key accidentally leaks."*
- "Apps calling web services directly / Server-side apps": *"Server-side applications relying on API keys are best secured through IP address restrictions."*
- För en lokal CLI hos en privatperson är IP-begränsning ofta opraktisk, eftersom hemma-IP:n ändras. Rekommendationen blir därför API-begränsning till exakt Routes API, Street View Static API och (om det används) Places API (New), plus dagliga kvottak. **Ej bekräftat:** en officiell rekommendation specifikt för "lokal CLI på slutanvändarens dator".

---

## Konsekvenser för designen

1. **Spara frågan, inte svaret.** bok bör bara spara indata i bokens filer, t.ex. `från`, `till`, `färdsätt`, `avgång` och gärna `place_id`, som får sparas obegränsat (SST A.3). Restid, avstånd och polyline räknas fram på begäran och **visas** i terminalen men skrivs aldrig till en fil. Vill man ha en lokal cache: håll den bara i minnet, eller i lat/lng-form med radering efter högst 30 dagar.
2. **Författaren skriver, verktyget inte.** Resultatet visas för författaren, och författaren formulerar själv en egen, gärna avrundad och tidstypisk formulering. Verktyget ska inte klistra in "23 min" i manus. Det minskar risken under "No Creating Content" och är dessutom rätt i sak, eftersom dagens restider inte är 1975 års.
3. **Märk tiden i allt som visas:** "Restid enligt Google Maps, beräknad 2026-10-04, dagens vägnät och trafikmönster (ej historiskt)". För WALK och BICYCLE ska Googles obligatoriska beta-varning skrivas ut. Attributionstexten är "Google Maps", oöversatt.
4. **Street View: bygg inte en automatisk kedja där bilder går till AI och prosa till manus.** Rekommenderad ersättning:
   - Kör `metadata` (gratis) för att visa *om* det finns bilder och *när* de togs ("Bilderna här är från 2023-06, inte 1975"). Visa copyright-fältet.
   - Generera en **Maps URL** (kräver ingen nyckel) som öppnar Street View i författarens webbläsare. Författaren tittar själv och skriver sin egen miljöbeskrivning. Det är vanligt konsumentbruk av Google Maps, utanför GMP-avtalets API-flöde.
   - Om man ändå vill låta Claude titta (högre risk, se A.4): hämta bilden bara till minnet eller en temporärfil som raderas direkt, spara aldrig bild, URL eller pano-cache, och kör bara med en AI-leverantör eller ett konto där indata inte används för träning (villkoret i ToS §3.2.3(c)(vii) gäller också "permit a third party"). Var medveten om att även detta sannolikt räknas som att "create content based on Google Maps Content". Grounding Lite-undantaget visar att Google inte annars tillåter det. Om något sådant byggs bör det vara avstängt som standard och tydligt märkt.
   - Kontrollera vad Claude Code själv sparar. Om bildfiler läses in i en session kan de hamna i lokala sessionsloggar, vilket skulle vara "store … outside the Services". Det är inte verifierat här, eftersom det ligger utanför Googles källor.
5. **Places / Search Along Route: lägg det sist eller hoppa över det.** För användare i EES (alla svenska) är Places-innehåll begränsat till nio ändamål (EEA-SST §15.2), och en romanskrivares research passar inte tydligt in. Globalt gäller att man inte får spara namn och adresser (§3.2.3(a)(iii)). Om det byggs: visa bara, spara bara `place_id`, och använd minsta möjliga field mask. Redan `displayName` kostar Pro-pris. Visa "Google Maps"-attribution och `googleMapsUri`.
6. **Nyckelhantering:**
   - Läs nyckeln från en miljövariabel eller en fil utanför repot, t.ex. `~/.config/bok/google-maps.key` med chmod 600. Aldrig från repot.
   - Routes och Places: skicka nyckeln i headern `X-Goog-Api-Key`.
   - Street View: nyckeln måste ligga i query-strängen (`key=`). Bygg URL:en internt och logga eller skriv aldrig ut den. Fånga `urllib.error.HTTPError`/`URLError` och skriv ut ett sanerat felmeddelande utan URL. Använd `return_error_code=true` så att fel blir HTTP-koder i stället för en grå bild.
   - Om en signatur används är signing secret ännu en hemlighet som ska hanteras på samma sätt.
   - Instruera användaren att API-begränsa nyckeln till de API:er som används och att sätta dagliga kvottak i Cloud Console.
7. **Kostnadsvakt:** Essentials-anrop (Routes utan trafik, och TRANSIT) har 10 000 gratis per månad, vilket räcker långt för en författare. Undvik `TRAFFIC_AWARE*` (Pro), `TWO_WHEELER` (Enterprise och dessutom inte tillgängligt i Sverige) och mer än 10 waypoints. Street View-bilder har 10 000 gratis per månad och metadata är gratis utan kvot.
8. **Dokumentation (ToS §3.2.2(a)):** bok:s README eller hjälptext bör tala om att funktionen använder Google Maps-innehåll och länka till https://maps.google.com/help/terms_maps/ och https://policies.google.com/privacy. Den bör också säga att användaren som "Customer" är bunden av GMP-villkoren (EEA-varianten vid EES-faktureringsadress) och att bok aldrig sparar Googles resultat.

---

## Osäkert eller ej bekräftat

- **Inget i villkoren behandlar uttryckligen att en LLM tittar på Street View-bilder (inferens).** Bedömningen "troligen förbjudet" är en tolkning av §3.2.3(a) och (c) tillsammans med Grounding Lite-undantaget (SST §10.2.1), inte en direkt träff. Juridisk rådgivning behövs för ett säkert svar.
- **Var gränsen går för "create content based on Google Maps Content"** när en människa skriver egen prosa efter att ha sett en restid. Villkoren har inga exempel på detta.
- **Tillfällig nedladdning:** ToS definierar inte "cache", och jag hittade ingen uttrycklig tidsgräns för transienta kopior i minnet eller i temporärfiler.
- **pano_id:** policy-sidan tillåter obegränsad lagring medan request- och metadata-sidorna säger "don't persist this ID". Det är en motsägelse i Googles egen dokumentation.
- **Hur många osignerade Street View-anrop som tillåts:** dokumentationen säger bara "limited", ingen siffra.
- **Om Street View Static accepterar `X-Goog-Api-Key`:** inte dokumenterat. Mitt test tyder på att det **inte** gör det. Testet gjordes på metadata-endpointen med ogiltig nyckel, så det är indirekt.
- **Övre framtidsgräns för departureTime med DRIVE:** inte angiven. För TRANSIT gäller 100 dagar.
- **Transit-täckning i Sverige:** kollektivtrafik ingår inte i täckningstabellen och är inte bekräftad per land.
- **Om TRANSIT faktureras som Essentials:** min slutsats bygger på att TRANSIT saknas bland Pro- och Enterprise-triggers. Det står inte uttryckligen.
- **EES-priser:** en separat EES-prislista hittades inte (pricing-eea gav 404). Den globala listan antas gälla.
- **Hur ToS §3.2.2(a) (användarvillkor) tillämpas** när kund och slutanvändare är samma person med egen nyckel i ett open source-verktyg: inte reglerat.
- **Claude Codes och Anthropics hantering av bilder** (lokala transkript, eventuell träning): ligger utanför den här researchen och är inte verifierat. Det har betydelse för ToS §3.2.3(c)(vii) och kraven i Grounding Lite-dokumentationen.
- **Geo Guidelines** (about.google) gäller Google Maps-produkterna och inte uttryckligen GMP-API:erna. De används här bara som stöd för att Street View-bilder inte får förekomma i böcker.
