
import re
import json

raw_data = '''
#	Club	
Participations
	
Matches
	
W
	
D
	
L
	Goals	
GD
	
Points
	
Points per tournament
1	GNK Dinamo Zagreb	GNK Dinamo Zagreb	24	108	61	24	23	203 : 107	96	207	8.63
2	Dynamo Kyiv	Dynamo Kyiv	25	79	45	16	18	147 : 77	70	151	6.04
3	Celtic FC	Celtic FC	19	74	42	13	19	132 : 68	64	139	7.32
4	FC Copenhagen	FC Copenhagen	16	70	36	18	16	122 : 69	53	126	7.88
5	BATE Borisov	BATE Borisov	16	74	33	24	17	98 : 77	21	123	7.69
6	Rosenborg BK	Rosenborg BK	18	62	37	10	15	115 : 60	55	121	6.72
7	FC Sheriff Tiraspol	FC Sheriff Tiraspol	21	88	33	18	37	92 : 87	5	117	5.57
8	FCSB	FCSB	17	66	30	21	15	120 : 87	33	111	6.53
9	NK Maribor	NK Maribor	16	64	31	13	20	85 : 70	15	106	6.63
10	Red Bull Salzburg	Red Bull Salzburg	18	62	30	15	17	95 : 67	28	105	5.83
11	Qarabağ FK	Qarabağ FK	11	57	29	16	12	95 : 45	50	103	9.36
12	FK Partizan Belgrade	FK Partizan Belgrade	15	62	28	17	17	103 : 69	34	101	6.73
13	Red Star Belgrade	Red Star Belgrade	13	61	26	21	14	98 : 61	37	99	7.62
14	Ludogorets Razgrad	Ludogorets Razgrad	14	64	27	14	23	100 : 77	23	95	6.79
15	APOEL Nicosia	APOEL Nicosia	13	58	25	16	17	75 : 44	31	91	7.00
16	Malmö FF	Malmö FF	10	54	25	14	15	82 : 68	14	89	8.90
17	HJK Helsinki	HJK Helsinki	16	58	25	13	20	84 : 63	21	88	5.50
18	AC Sparta Prague	AC Sparta Prague	17	52	26	9	17	79 : 59	20	87	5.12
19	Rangers FC	Rangers FC	18	54	24	14	16	87 : 58	29	86	4.78
20	Ferencvárosi TC	Ferencvárosi TC	12	49	22	15	12	78 : 60	18	81	6.75
21	Legia Warszawa	Legia Warszawa	11	44	23	10	11	63 : 40	23	79	7.18
22	Shakhtar Donetsk	Shakhtar Donetsk	13	40	22	10	8	66 : 38	28	76	5.85
23	Maccabi Haifa	Maccabi Haifa	11	42	20	9	13	84 : 55	29	69	6.27
24	Slovan Bratislava	Slovan Bratislava	12	47	18	15	14	62 : 54	8	69	5.75
25	FC Viktoria Plzen	FC Viktoria Plzen	8	33	20	6	7	65 : 43	22	66	8.25
26	Galatasaray	Galatasaray	12	30	20	5	5	69 : 34	35	65	5.42
27	Olympiacos Piraeus	Olympiacos Piraeus	10	30	19	8	3	50 : 22	28	65	6.50
28	SL Benfica	SL Benfica	11	31	19	7	5	56 : 25	31	64	5.82
29	RSC Anderlecht	RSC Anderlecht	12	38	18	9	11	72 : 43	29	63	5.25
30	FC Basel 1893	FC Basel 1893	11	38	18	9	11	60 : 48	12	63	5.73
31	Fenerbahce	Fenerbahce	15	42	15	13	14	62 : 51	11	58	3.87
32	Club Brugge KV	Club Brugge KV	11	34	16	8	10	57 : 47	10	56	5.09
33	Panathinaikos FC	Panathinaikos FC	14	38	15	10	13	55 : 50	5	55	3.93
34	PSV Eindhoven	PSV Eindhoven	9	28	16	6	6	62 : 31	31	54	6.00
35	Maccabi Tel Aviv	Maccabi Tel Aviv	12	37	14	11	12	47 : 35	12	53	4.42
36	Skonto Riga (- 2016)	Skonto Riga (- 2016)	12	38	16	5	17	57 : 51	6	53	4.42
37	SK Slavia Prague	SK Slavia Prague	14	38	15	8	15	31 : 41	-10	53	3.79
38	Ajax Amsterdam	Ajax Amsterdam	11	32	12	14	6	52 : 43	9	50	4.55
39	BSC Young Boys	BSC Young Boys	11	32	13	8	11	45 : 56	-11	47	4.27
40	Liverpool FC	Liverpool FC	7	18	14	2	2	40 : 10	30	44	6.29
41	Dinamo Tbilisi	Dinamo Tbilisi	13	37	13	5	19	47 : 53	-6	44	3.38
42	FC Astana	FC Astana	7	29	12	7	10	35 : 42	-7	43	6.14
43	Wisla Kraków	Wisla Kraków	7	26	13	2	11	48 : 39	9	41	5.86
44	Arsenal FC	Arsenal FC	7	14	13	1	0	30 : 3	27	40	5.71
45	CFR Cluj	CFR Cluj	6	24	11	7	6	34 : 26	8	40	6.67
46	The New Saints	The New Saints	17	46	11	7	28	44 : 80	-36	40	2.35
47	Levski Sofia	Levski Sofia	7	28	10	9	9	37 : 18	19	39	5.57
48	Anorthosis Famagusta	Anorthosis Famagusta	7	28	11	6	11	38 : 30	8	39	5.57
49	FBK Kaunas (- 2012)	FBK Kaunas (- 2012)	8	28	10	7	11	38 : 39	-1	39	4.88
50	Molde FK	Molde FK	6	27	9	11	7	41 : 24	17	38	6.33
51	Debreceni VSC	Debreceni VSC	7	26	11	5	10	32 : 31	1	38	5.43
52	CSKA Moscow	CSKA Moscow	6	18	11	4	3	29 : 16	13	37	6.17
53	FC Midtjylland	FC Midtjylland	6	24	10	7	7	31 : 25	6	37	6.17
54	F91 Dudelange	F91 Dudelange	16	42	10	7	25	49 : 78	-29	37	2.31
55	FC Pyunik Yerevan	FC Pyunik Yerevan	14	42	9	10	23	36 : 69	-33	37	2.64
56	Besiktas JK	Besiktas JK	7	19	10	6	3	28 : 15	13	36	5.14
57	Rapid Vienna	Rapid Vienna	7	20	11	3	6	36 : 26	10	36	5.14
58	FK Žalgiris Vilnius	FK Žalgiris Vilnius	9	28	10	6	12	27 : 35	-8	36	4.00
59	AEK Athens	AEK Athens	9	22	10	4	8	27 : 25	2	34	3.78
60	AS Monaco	AS Monaco	6	18	10	3	5	38 : 20	18	33	5.50
61	Bröndby IF	Bröndby IF	8	24	10	3	11	34 : 32	2	33	4.13
62	MSK Zilina	MSK Zilina	7	22	9	5	8	24 : 26	-2	32	4.57
63	SK Sturm Graz	SK Sturm Graz	9	24	9	5	10	35 : 41	-6	32	3.56
64	FK Bodø/Glimt	FK Bodø/Glimt	4	18	10	1	7	42 : 21	21	31	7.75
65	Hapoel Beer Sheva	Hapoel Beer Sheva	3	16	9	3	4	27 : 24	3	30	10.00
66	PAOK Thessaloniki	PAOK Thessaloniki	8	26	7	9	10	40 : 45	-5	30	3.75
67	Lincoln Red Imps FC	Lincoln Red Imps FC	10	29	9	3	17	29 : 51	-22	30	3.00
68	Linfield FC	Linfield FC	16	39	6	12	21	21 : 54	-33	30	1.88
69	FCI Levadia	FCI Levadia	11	29	7	8	14	29 : 45	-16	29	2.64
70	Zenit St. Petersburg	Zenit St. Petersburg	3	12	9	1	2	23 : 6	17	28	9.33
71	Valletta FC	Valletta FC	12	34	7	7	20	33 : 59	-26	28	2.33
72	Neftchi PFK	Neftchi PFK	7	22	7	5	10	18 : 36	-18	26	3.71
73	Manchester United	Manchester United	5	10	8	1	1	25 : 3	22	25	5.00
74	FC Aktobe	FC Aktobe	5	16	7	4	5	23 : 18	5	25	5.00
75	Spartak Moscow	Spartak Moscow	9	20	6	7	7	31 : 29	2	25	2.78
76	Lovech	Lovech	4	16	8	1	7	29 : 28	1	25	6.25
77	NK Olimpija Ljubljana	NK Olimpija Ljubljana	6	16	7	3	6	20 : 19	1	24	4.00
78	Omonia Nicosia	Omonia Nicosia	6	19	6	6	7	21 : 25	-4	24	4.00
79	Shelbourne FC	Shelbourne FC	6	22	5	9	8	22 : 29	-7	24	4.00
80	SC Braga	SC Braga	3	10	7	2	1	21 : 9	12	23	7.67
81	LOSC Lille	LOSC Lille	5	14	7	2	5	17 : 10	7	23	4.60
82	FC Zimbru Chisinau	FC Zimbru Chisinau	4	16	7	2	7	24 : 17	7	23	5.75
83	Vardar Skopje	Vardar Skopje	7	22	5	8	9	30 : 34	-4	23	3.29
84	Valencia CF	Valencia CF	5	10	7	1	2	20 : 6	14	22	4.40
85	Olympique Lyon	Olympique Lyon	5	12	7	1	4	18 : 13	5	22	4.40
86	Kairat Almaty	Kairat Almaty	3	14	6	4	4	15 : 15	0	22	7.33
87	KÍ Klaksvík	KÍ Klaksvík	6	18	6	4	8	22 : 30	-8	22	3.67
88	FH Hafnarfjördur	FH Hafnarfjördur	8	24	5	7	12	21 : 35	-14	22	2.75
89	HSK Zrinjski Mostar	HSK Zrinjski Mostar	9	22	5	7	10	17 : 32	-15	22	2.44
90	FC Porto	FC Porto	5	12	6	3	3	24 : 12	12	21	4.20
91	FC Barcelona	FC Barcelona	4	8	7	0	1	17 : 6	11	21	5.25
92	Grasshopper Club Zurich	Grasshopper Club Zurich	7	16	6	3	7	26 : 19	7	21	3.00
93	FC Petrzalka	FC Petrzalka	2	12	6	3	3	20 : 15	5	21	10.50
94	Beitar Jerusalem	Beitar Jerusalem	5	14	6	3	5	18 : 22	-4	21	4.20
95	KF Skënderbeu	KF Skënderbeu	5	16	6	3	7	18 : 25	-7	21	4.20
96	AIK	AIK	3	12	6	2	4	13 : 11	2	20	6.67
97	JFK Ventspils	JFK Ventspils	6	20	6	2	12	21 : 31	-10	20	3.33
98	Shkendija Tetovo	Shkendija Tetovo	5	18	6	2	10	14 : 29	-15	20	4.00
99	Bayer 04 Leverkusen	Bayer 04 Leverkusen	5	10	6	1	3	25 : 7	18	19	3.80
100	1.FC Kosice (1951 - 2004)	1.FC Kosice (1951 - 2004)	2	8	6	1	1	20 : 4	16	19	9.50
101	Inter Milan	Inter Milan	5	10	5	4	1	17 : 5	12	19	3.80
102	AC Milan	AC Milan	4	8	6	1	1	15 : 5	10	19	4.75
103	Videoton FC Fehérvár	Videoton FC Fehérvár	3	14	4	7	3	13 : 13	0	19	6.33
104	Lech Poznan	Lech Poznan	4	14	6	1	7	17 : 17	0	19	4.75
105	FC Haka	FC Haka	4	18	5	4	9	23 : 28	-5	19	4.75
106	Shamrock Rovers	Shamrock Rovers	6	18	5	4	9	14 : 22	-8	19	3.17
107	IFK Göteborg	IFK Göteborg	5	12	5	3	4	23 : 11	12	18	3.60
108	Helsingborgs IF	Helsingborgs IF	2	10	5	3	2	13 : 5	8	18	9.00
109	Breidablik Kópavogur	Breidablik Kópavogur	3	12	6	0	6	26 : 24	2	18	6.00
110	FC Zürich	FC Zürich	5	14	5	3	6	19 : 19	0	18	3.60
111	KRC Genk	KRC Genk	6	14	5	3	6	21 : 23	-2	18	3.00
112	FK Ekranas Panevezys (- 2014)	FK Ekranas Panevezys (- 2014)	7	20	5	3	12	19 : 40	-21	18	2.57
113	Raków Częstochowa	Raków Częstochowa	1	8	5	2	1	12 : 6	6	17	17.00
114	Grazer AK 1902	Grazer AK 1902	3	10	5	2	3	19 : 13	6	17	5.67
115	Aalborg BK	Aalborg BK	4	12	5	2	5	18 : 15	3	17	4.25
116	Torpedo Kutaisi	Torpedo Kutaisi	4	12	5	2	5	14 : 19	-5	17	4.25
117	HNK Hajduk Split	HNK Hajduk Split	6	14	4	5	5	12 : 19	-7	17	2.83
118	Bayern Munich	Bayern Munich	3	6	5	1	0	14 : 2	12	16	5.33
119	SS Lazio	SS Lazio	4	8	5	1	2	14 : 9	5	16	4.00
120	AEL Limassol	AEL Limassol	2	8	5	1	2	8 : 6	2	16	8.00
121	Sporting CP	Sporting CP	6	14	3	7	4	17 : 15	2	16	2.67
122	Feyenoord Rotterdam	Feyenoord Rotterdam	6	12	5	1	6	20 : 20	0	16	2.67
123	CSKA Sofia	CSKA Sofia	3	10	5	1	4	12 : 14	-2	16	5.33
124	ND Gorica	ND Gorica	3	12	5	1	6	20 : 25	-5	16	5.33
125	Tampere United	Tampere United	3	12	5	1	6	12 : 21	-9	16	5.33
126	MTK Budapest	MTK Budapest	4	14	5	1	8	15 : 24	-9	16	4.00
127	KF Tirana	KF Tirana	9	24	5	1	18	23 : 41	-18	16	1.78
128	FC Flora Tallinn	FC Flora Tallinn	12	27	4	4	19	21 : 56	-35	16	1.33
129	IF Elfsborg	IF Elfsborg	2	10	4	3	3	14 : 7	7	15	7.50
130	Borussia Dortmund	Borussia Dortmund	3	6	5	0	1	10 : 4	6	15	5.00
131	Rabotnicki Skopje	Rabotnicki Skopje	4	14	3	6	5	15 : 13	2	15	3.75
132	Lokomotiv Moscow	Lokomotiv Moscow	5	12	4	3	5	16 : 16	0	15	3.00
133	FC RFS	FC RFS	3	10	5	0	5	13 : 14	-1	15	5.00
134	FC Drita	FC Drita	3	10	5	0	5	12 : 15	-3	15	5.00
135	Hibernians FC	Hibernians FC	6	16	4	3	9	12 : 35	-23	15	2.50
136	Pafos FC	Pafos FC	1	6	4	2	0	8 : 3	5	14	14.00
137	Alashkert Yerevan FC	Alashkert Yerevan FC	4	14	3	5	6	12 : 20	-8	14	3.50
138	HB Tórshavn	HB Tórshavn	10	21	3	5	13	19 : 52	-33	14	1.40
139	Newcastle United	Newcastle United	3	6	4	1	1	10 : 4	6	13	4.33
140	Hapoel Tel Aviv	Hapoel Tel Aviv	2	8	4	1	3	14 : 10	4	13	6.50
141	Olympique Marseille	Olympique Marseille	3	6	4	1	1	6 : 3	3	13	4.33
142	Shakhter Karaganda	Shakhter Karaganda	2	8	4	1	3	10 : 8	2	13	6.50
143	FK Zeljeznicar Sarajevo	FK Zeljeznicar Sarajevo	5	14	4	1	9	12 : 27	-15	13	2.60
144	KR Reykjavík	KR Reykjavík	7	15	3	4	8	13 : 31	-18	13	1.86
145	Barry Town United	Barry Town United	6	14	4	1	9	11 : 38	-27	13	2.17
146	ACF Fiorentina	ACF Fiorentina	3	6	3	3	0	10 : 4	6	12	4.00
147	SV Werder Bremen	SV Werder Bremen	3	6	4	0	2	14 : 9	5	12	4.00
148	Parma Calcio 1913	Parma Calcio 1913	3	6	4	0	2	9 : 5	4	12	4.00
149	Widzew Lodz	Widzew Lodz	3	10	4	0	6	21 : 21	0	12	4.00
150	FK Sarajevo	FK Sarajevo	4	12	4	0	8	16 : 17	-1	12	3.00
151	NK Domzale	NK Domzale	2	8	4	0	4	10 : 12	-2	12	6.00
152	Trabzonspor	Trabzonspor	4	10	3	3	4	10 : 12	-2	12	3.00
153	Boavista FC	Boavista FC	2	6	3	2	1	13 : 7	6	11	5.50
154	Inter Bratislava	Inter Bratislava	2	8	3	2	3	8 : 11	-3	11	5.50
155	Birkirkara FC	Birkirkara FC	4	10	3	2	5	12 : 19	-7	11	2.75
156	Bohemian Football Club	Bohemian Football Club	4	12	3	2	7	9 : 16	-7	11	2.75
157	Dundalk FC	Dundalk FC	5	15	1	8	6	11 : 19	-8	11	2.20
158	Chelsea FC	Chelsea FC	2	4	3	1	0	8 : 0	8	10	5.00
159	FC Thun	FC Thun	1	4	3	1	0	7 : 2	5	10	10.00
160	Sevilla FC	Sevilla FC	3	6	3	1	2	13 : 9	4	10	3.33
161	NK Celje	NK Celje	2	6	3	1	2	12 : 9	3	10	5.00
162	Vålerenga Fotball Elite	Vålerenga Fotball Elite	2	6	3	1	2	9 : 7	2	10	5.00
163	Halmstads BK	Halmstads BK	2	6	3	1	2	9 : 8	1	10	5.00
164	NK Siroki Brijeg	NK Siroki Brijeg	2	6	3	1	2	4 : 5	-1	10	5.00
165	Dinamo Minsk	Dinamo Minsk	4	10	2	4	4	6 : 9	-3	10	2.50
166	Djurgårdens IF	Djurgårdens IF	4	9	2	4	3	10 : 14	-4	10	2.50
167	Atlético de Madrid	Atlético de Madrid	2	4	3	0	1	9 : 3	6	9	4.50
168	Borussia Mönchengladbach	Borussia Mönchengladbach	2	4	3	0	1	12 : 6	6	9	4.50
169	Paris Saint-Germain	Paris Saint-Germain	2	4	3	0	1	10 : 4	6	9	4.50
170	Villarreal CF	Villarreal CF	3	6	3	0	3	8 : 6	2	9	3.00
171	Slavia Mozyr	Slavia Mozyr	2	8	2	3	3	11 : 12	-1	9	4.50
172	Austria Vienna	Austria Vienna	3	8	2	3	3	6 : 8	-2	9	3.00
173	FC Krasnodar	FC Krasnodar	2	6	3	0	3	8 : 11	-3	9	4.50
174	Inter Club d'Escaldes	Inter Club d'Escaldes	4	7	3	0	4	7 : 10	-3	9	2.25
175	HNK Rijeka	HNK Rijeka	3	10	2	3	5	11 : 14	-3	9	3.00
176	FK Borac Banja Luka	FK Borac Banja Luka	3	8	3	0	5	11 : 17	-6	9	3.00
177	Buducnost Podgorica	Buducnost Podgorica	7	13	2	3	8	10 : 25	-15	9	1.29
178	B36 Tórshavn	B36 Tórshavn	6	14	2	3	9	12 : 30	-18	9	1.50
179	FC Santa Coloma	FC Santa Coloma	8	19	2	3	14	12 : 35	-23	9	1.13
180	Juventus FC	Juventus FC	2	4	2	2	0	11 : 4	7	8	4.00
181	FC Rostov	FC Rostov	1	4	2	2	0	9 : 4	5	8	8.00
182	BK Häcken	BK Häcken	1	4	2	2	0	8 : 4	4	8	8.00
183	Deportivo de La Coruña	Deportivo de La Coruña	2	4	2	2	0	4 : 0	4	8	4.00
184	Víkingur Reykjavík	Víkingur Reykjavík	2	6	2	2	2	13 : 9	4	8	4.00
185	Ironi Kiryat Shmona	Ironi Kiryat Shmona	1	6	2	2	2	9 : 6	3	8	8.00
186	Spartak Trnava	Spartak Trnava	1	6	2	2	2	6 : 5	1	8	8.00
187	Udinese Calcio	Udinese Calcio	3	6	2	2	2	7 : 7	0	8	2.67
188	FK Baku (- 2018)	FK Baku (- 2018)	2	6	2	2	2	7 : 8	-1	8	4.00
189	FC Slovan Liberec	FC Slovan Liberec	3	8	2	2	4	6 : 8	-2	8	2.67
190	Servette FC	Servette FC	4	10	1	5	4	12 : 18	-6	8	2.00
191	Twente Enschede FC	Twente Enschede FC	4	10	1	5	4	10 : 17	-7	8	2.00
192	Standard Liège	Standard Liège	5	12	1	5	6	8 : 17	-9	8	1.60
193	NS Mura	NS Mura	1	4	2	1	1	7 : 3	4	7	7.00
194	LKS Lodz	LKS Lodz	1	4	2	1	1	7 : 4	3	7	7.00
195	Polonia Warsaw	Polonia Warsaw	1	4	2	1	1	10 : 8	2	7	7.00
196	AJ Auxerre	AJ Auxerre	2	4	2	1	1	3 : 1	2	7	3.50
197	Athletic Bilbao	Athletic Bilbao	2	4	2	1	1	6 : 4	2	7	3.50
198	SSC Napoli	SSC Napoli	2	4	2	1	1	6 : 4	2	7	3.50
199	Rubin Kazan	Rubin Kazan	1	4	2	1	1	6 : 5	1	7	7.00
200	Drogheda United FC	Drogheda United FC	1	4	2	1	1	6 : 5	1	7	7.00
201	FC Feronikeli 74	FC Feronikeli 74	1	4	2	1	1	5 : 4	1	7	7.00
202	Myllykosken Pallo -47	Myllykosken Pallo -47	1	4	2	1	1	4 : 4	0	7	7.00
203	Rudar Pljevlja	Rudar Pljevlja	2	6	2	1	3	7 : 7	0	7	3.50
204	FK Obilic (- 2015)	FK Obilic (- 2015)	1	4	2	1	1	5 : 6	-1	7	7.00
205	Odense Boldklub	Odense Boldklub	1	4	2	1	1	6 : 7	-1	7	7.00
206	FC Schalke 04	FC Schalke 04	2	4	2	1	1	5 : 7	-2	7	3.50
207	AS Trencin	AS Trencin	2	6	2	1	3	9 : 11	-2	7	3.50
208	FC Milsami Orhei	FC Milsami Orhei	2	6	2	1	3	3 : 6	-3	7	3.50
209	FC Ballkani	FC Ballkani	3	6	2	1	3	6 : 9	-3	7	2.33
210	Víkingur Gøta	Víkingur Gøta	3	8	2	1	5	11 : 14	-3	7	2.33
211	Kuopion Palloseura	Kuopion Palloseura	2	5	2	1	2	3 : 8	-5	7	3.50
212	Zhenis Astana	Zhenis Astana	2	6	2	1	3	9 : 14	-5	7	3.50
213	Cork City FC	Cork City FC	3	8	2	1	5	6 : 13	-7	7	2.33
214	FC Dinamo City	FC Dinamo City	3	8	2	1	5	6 : 14	-8	7	2.33
215	FC Dinamo 1948	FC Dinamo 1948	4	10	2	1	7	10 : 20	-10	7	1.75
216	Kalju FC	Kalju FC	2	8	2	1	5	6 : 20	-14	7	3.50
217	Manchester City	Manchester City	1	2	2	0	0	6 : 0	6	6	6.00
218	Real Madrid	Real Madrid	1	2	2	0	0	5 : 1	4	6	6.00
219	Real Sociedad	Real Sociedad	1	2	2	0	0	4 : 0	4	6	6.00
220	Aris Limassol	Aris Limassol	1	4	2	0	2	12 : 8	4	6	6.00
221	Dynamo Brest	Dynamo Brest	1	3	2	0	1	8 : 5	3	6	6.00
222	Leeds United	Leeds United	1	2	2	0	0	3 : 1	2	6	6.00
223	Royal Antwerp FC	Royal Antwerp FC	1	2	2	0	0	3 : 1	2	6	6.00
224	Jagiellonia Bialystok	Jagiellonia Bialystok	1	4	2	0	2	8 : 6	2	6	6.00
225	Hamburger SV	Hamburger SV	2	4	1	3	0	3 : 1	2	6	3.00
226	LASK	LASK	1	4	2	0	2	6 : 5	1	6	6.00
227	FC Shirak Gyumri	FC Shirak Gyumri	2	6	1	3	2	6 : 5	1	6	3.00
228	Floriana FC	Floriana FC	2	3	2	0	1	2 : 2	0	6	3.00
229	FC Urartu Yerevan	FC Urartu Yerevan	2	4	2	0	2	6 : 6	0	6	3.00
230	FC Sion	FC Sion	1	4	2	0	2	7 : 8	-1	6	6.00
231	FC Prishtina	FC Prishtina	1	4	2	0	2	5 : 6	-1	6	6.00
232	FC Jazz Pori	FC Jazz Pori	1	4	2	0	2	6 : 8	-2	6	6.00
233	FC Shamakhi	FC Shamakhi	2	6	1	3	2	3 : 5	-2	6	3.00
234	FK Alfa Modriča	FK Alfa Modriča	1	4	2	0	2	5 : 8	-3	6	6.00
235	FK Kukësi	FK Kukësi	2	6	1	3	2	3 : 6	-3	6	3.00
236	Zalaegerszegi TE FC	Zalaegerszegi TE FC	1	4	2	0	2	3 : 7	-4	6	6.00
237	KF Egnatia	KF Egnatia	2	4	2	0	2	3 : 7	-4	6	3.00
238	FCV Farul Constanta	FCV Farul Constanta	2	4	2	0	2	2 : 7	-5	6	3.00
239	ÍBV Vestmannaeyjar	ÍBV Vestmannaeyjar	2	6	2	0	4	5 : 10	-5	6	3.00
240	SK Brann	SK Brann	3	8	1	3	4	6 : 11	-5	6	2.00
241	KF Vllaznia	KF Vllaznia	2	6	2	0	4	6 : 12	-6	6	3.00
242	FK Sloga Jugomagnat (- 2012)	FK Sloga Jugomagnat (- 2012)	3	10	1	3	6	5 : 12	-7	6	2.00
243	Mogren Budva	Mogren Budva	2	6	2	0	4	7 : 17	-10	6	3.00
244	Hamrun Spartans	Hamrun Spartans	3	8	2	0	6	4 : 15	-11	6	2.00
245	Stabæk Fotball	Stabæk Fotball	1	4	1	2	1	6 : 4	2	5	5.00
246	Dunaújváros FC (-2019)	Dunaújváros FC (-2019)	1	4	1	2	1	7 : 6	1	5	5.00
247	RCD Mallorca	RCD Mallorca	2	4	1	2	1	3 : 2	1	5	2.50
248	FC Petrocub Hincesti	FC Petrocub Hincesti	1	4	1	2	1	2 : 2	0	5	5.00
249	FK Mlada Boleslav	FK Mlada Boleslav	1	4	1	2	1	8 : 9	-1	5	5.00
250	Basaksehir FK	Basaksehir FK	2	6	1	2	3	8 : 10	-2	5	2.50
251	FC Zestafoni	FC Zestafoni	2	6	1	2	3	6 : 9	-3	5	2.50
252	FK Sūduva Marijampolė	FK Sūduva Marijampolė	3	8	1	2	5	5 : 13	-8	5	1.67
253	FK Partizani	FK Partizani	4	10	0	5	5	3 : 13	-10	5	1.25
254	Crusaders FC	Crusaders FC	4	10	1	2	7	7 : 33	-26	5	1.25
255	Hertha BSC	Hertha BSC	1	2	1	1	0	2 : 0	2	4	4.00
256	VfB Stuttgart	VfB Stuttgart	1	2	1	1	0	2 : 0	2	4	4.00
257	Málaga CF	Málaga CF	1	2	1	1	0	2 : 0	2	4	4.00
258	Metalist Kharkiv (- 2016)	Metalist Kharkiv (- 2016)	1	2	1	1	0	3 : 1	2	4	4.00
259	Real Betis Balompié	Real Betis Balompié	1	2	1	1	0	3 : 2	1	4	4.00
260	SC Tavriya Simferopol (-2022)	SC Tavriya Simferopol (-2022)	1	2	1	1	0	2 : 1	1	4	4.00
261	FC Shkupi	FC Shkupi	1	4	1	1	2	5 : 5	0	4	4.00
262	Heart of Midlothian FC	Heart of Midlothian FC	1	4	1	1	2	4 : 5	-1	4	4.00
263	FK Leotar Trebinje	FK Leotar Trebinje	1	4	1	1	2	3 : 4	-1	4	4.00
264	FC Noah Yerevan	FC Noah Yerevan	1	4	1	1	2	7 : 8	-1	4	4.00
265	Dinamo Batumi	Dinamo Batumi	2	4	1	1	2	3 : 5	-2	4	2.00
266	FK Panevėžys	FK Panevėžys	1	4	1	1	2	5 : 8	-3	4	4.00
267	Apollon Limassol	Apollon Limassol	2	4	1	1	2	3 : 6	-3	4	2.00
268	Belshina Bobruisk	Belshina Bobruisk	1	4	1	1	2	3 : 7	-4	4	4.00
269	FC Wacker Innsbruck	FC Wacker Innsbruck	2	4	1	1	2	3 : 7	-4	4	2.00
270	ÍA Akranes	ÍA Akranes	3	6	1	1	4	3 : 8	-5	4	1.33
271	Sileks Kratovo	Sileks Kratovo	3	5	1	1	3	2 : 9	-7	4	1.33
272	EB/Streymur	EB/Streymur	2	6	1	1	4	9 : 17	-8	4	2.00
273	WIT Georgia Tbilisi	WIT Georgia Tbilisi	2	6	1	1	4	8 : 17	-9	4	2.00
274	Liepajas Metalurgs	Liepajas Metalurgs	2	6	1	1	4	3 : 14	-11	4	2.00
275	Jeunesse Esch	Jeunesse Esch	5	10	1	1	8	1 : 26	-25	4	0.80
276	Tottenham Hotspur	Tottenham Hotspur	1	2	1	0	1	6 : 3	3	3	3.00
277	FC Aarau	FC Aarau	1	2	1	0	1	3 : 2	1	3	3.00
278	Lierse SK (-2018)	Lierse SK (-2018)	1	2	1	0	1	3 : 2	1	3	3.00
279	Celta de Vigo	Celta de Vigo	1	2	1	0	1	3 : 2	1	3	3.00
280	AZ Alkmaar	AZ Alkmaar	1	2	1	0	1	3 : 3	0	3	3.00
281	Kalmar FF	Kalmar FF	1	2	1	0	1	3 : 3	0	3	3.00
282	NK Zagreb	NK Zagreb	1	2	1	0	1	2 : 2	0	3	3.00
283	Cwmbran Town	Cwmbran Town	1	2	1	0	1	4 : 4	0	3	3.00
284	Dynamo Moscow	Dynamo Moscow	1	2	1	0	1	1 : 2	-1	3	3.00
285	FC Koper	FC Koper	1	2	1	0	1	4 : 5	-1	3	3.00
286	UC Sampdoria	UC Sampdoria	1	2	1	0	1	4 : 5	-1	3	3.00
287	IFK Norrköping	IFK Norrköping	1	2	1	0	1	4 : 5	-1	3	3.00
288	HNK Brotnjo Citluk	HNK Brotnjo Citluk	1	2	1	0	1	3 : 4	-1	3	3.00
289	FK Gomel	FK Gomel	1	2	1	0	1	1 : 2	-1	3	3.00
290	Dacia Chisinau	Dacia Chisinau	1	2	1	0	1	2 : 3	-1	3	3.00
291	KF Elbasani (- 2022)	KF Elbasani (- 2022)	1	2	1	0	1	1 : 3	-2	3	3.00
292	NSÍ Runavík	NSÍ Runavík	1	2	1	0	1	1 : 3	-2	3	3.00
293	FC Ararat-Armenia 	FC Ararat-Armenia 	1	3	1	0	2	3 : 5	-2	3	3.00
294	FK Zeta Golubovac	FK Zeta Golubovac	1	4	1	0	3	5 : 7	-2	3	3.00
295	Politehnica Timisoara (- 2012)	Politehnica Timisoara (- 2012)	1	4	0	3	1	2 : 4	-2	3	3.00
296	Sivasspor	Sivasspor	1	2	1	0	1	3 : 6	-3	3	3.00
297	Llanelli Town AFC	Llanelli Town AFC	1	2	1	0	1	1 : 4	-3	3	3.00
298	Sioni Bolnisi	Sioni Bolnisi	1	4	1	0	3	2 : 5	-3	3	3.00
299	Riga FC	Riga FC	3	5	0	3	2	1 : 4	-3	3	1.00
300	FC Banik Ostrava	FC Banik Ostrava	1	2	1	0	1	2 : 6	-4	3	3.00
301	Újpest FC	Újpest FC	1	4	1	0	3	5 : 9	-4	3	3.00
302	Slask Wroclaw	Slask Wroclaw	1	4	1	0	3	3 : 7	-4	3	3.00
303	MFK Ruzomberok	MFK Ruzomberok	1	4	1	0	3	3 : 7	-4	3	3.00
304	UE Santa Coloma	UE Santa Coloma	1	4	1	0	3	3 : 7	-4	3	3.00
305	FC Lugano	FC Lugano	2	4	1	0	3	6 : 10	-4	3	1.50
306	Union Saint-Gilloise	Union Saint-Gilloise	2	4	1	0	3	3 : 7	-4	3	1.50
307	Kapaz PFK	Kapaz PFK	2	4	1	0	3	4 : 9	-5	3	1.50
308	FK Shamkir	FK Shamkir	2	6	1	0	5	6 : 11	-5	3	1.50
309	Europa FC	Europa FC	2	3	1	0	2	3 : 9	-6	3	1.50
310	KAA Gent	KAA Gent	2	5	1	0	4	4 : 12	-8	3	1.50
311	Iberia 1999 Tbilisi	Iberia 1999 Tbilisi	2	6	1	0	5	6 : 14	-8	3	1.50
312	Valur Reykjavík	Valur Reykjavík	4	8	1	0	7	4 : 16	-12	3	0.75
313	Sliema Wanderers	Sliema Wanderers	3	8	1	0	7	6 : 25	-19	3	1.00
314	FK Sutjeska Niksic	FK Sutjeska Niksic	5	12	0	3	9	3 : 23	-20	3	0.60
315	SP Tre Penne	SP Tre Penne	5	8	1	0	7	3 : 27	-24	3	0.60
316	CA Osasuna	CA Osasuna	1	2	0	2	0	1 : 1	0	2	2.00
317	AEK Larnaca	AEK Larnaca	1	2	0	2	0	2 : 2	0	2	2.00
318	FC Rapid 1923	FC Rapid 1923	2	4	0	2	2	6 : 8	-2	2	1.00
319	Pobeda Prilep	Pobeda Prilep	2	4	0	2	2	2 : 5	-3	2	1.00
320	FK Spartaks Jurmala	FK Spartaks Jurmala	2	4	0	2	2	1 : 4	-3	2	1.00
321	Hapoel Haifa	Hapoel Haifa	1	4	0	2	2	1 : 5	-4	2	2.00
322	FC Vaslui (- 2014)	FC Vaslui (- 2014)	2	4	0	2	2	2 : 7	-5	2	1.00
323	Tobol Kostanay	Tobol Kostanay	2	4	0	2	2	2 : 8	-6	2	1.00
324	OGC Nice	OGC Nice	2	6	0	2	4	3 : 11	-8	2	1.00
325	UE Sant Julia	UE Sant Julia	1	4	0	2	2	2 : 11	-9	2	2.00
326	Tre Fiori FC	Tre Fiori FC	4	7	0	2	5	4 : 16	-12	2	0.50
327	CS Fola Esch	CS Fola Esch	4	7	0	2	5	3 : 19	-16	2	0.50
328	St. Patrick's Athletic	St. Patrick's Athletic	3	6	0	2	4	1 : 18	-17	2	0.67
329	FC St. Gallen 1879	FC St. Gallen 1879	1	2	0	1	1	3 : 4	-1	1	1.00
330	FC Metz	FC Metz	1	2	0	1	1	1 : 2	-1	1	1.00
331	Vitória Guimarães SC	Vitória Guimarães SC	1	2	0	1	1	1 : 2	-1	1	1.00
332	Portadown FC	Portadown FC	1	2	0	1	1	2 : 3	-1	1	1.00
333	Piast Gliwice	Piast Gliwice	1	2	0	1	1	2 : 3	-1	1	1.00
334	TVMK Tallinn (- 2008)	TVMK Tallinn (- 2008)	1	2	0	1	1	3 : 4	-1	1	1.00
335	Unirea Urziceni ( - 2011)	Unirea Urziceni ( - 2011)	1	2	0	1	1	0 : 1	-1	1	1.00
336	Irtysh Pavlodar	Irtysh Pavlodar	1	2	0	1	1	1 : 2	-1	1	1.00
337	FC Tiraspol	FC Tiraspol	1	2	0	1	1	3 : 4	-1	1	1.00
338	Ordabasy Shymkent	Ordabasy Shymkent	1	2	0	1	1	0 : 1	-1	1	1.00
339	Dnipro Dnipropetrovsk (- 2020)	Dnipro Dnipropetrovsk (- 2020)	1	2	0	1	1	0 : 2	-2	1	1.00
340	Chievo Verona	Chievo Verona	1	2	0	1	1	2 : 4	-2	1	1.00
341	Silkeborg IF	Silkeborg IF	1	2	0	1	1	1 : 3	-2	1	1.00
342	CS Grevenmacher	CS Grevenmacher	1	2	0	1	1	0 : 2	-2	1	1.00
343	Metalurgi Rustavi	Metalurgi Rustavi	1	2	0	1	1	1 : 3	-2	1	1.00
344	Khazar Lankaran (- 2016)	Khazar Lankaran (- 2016)	1	2	0	1	1	2 : 4	-2	1	1.00
345	Swift Hesperange	Swift Hesperange	1	2	0	1	1	1 : 3	-2	1	1.00
346	SJK Seinäjoki	SJK Seinäjoki	1	2	0	1	1	2 : 4	-2	1	1.00
347	SC Dnipro-1 ( - 2024)	SC Dnipro-1 ( - 2024)	1	2	0	1	1	3 : 5	-2	1	1.00
348	AS Roma	AS Roma	1	2	0	1	1	1 : 4	-3	1	1.00
349	FC Rustavi	FC Rustavi	1	2	0	1	1	0 : 3	-3	1	1.00
350	FK Decic Tuzi	FK Decic Tuzi	1	2	0	1	1	1 : 4	-3	1	1.00
351	Astra Giurgiu (- 2024)	Astra Giurgiu (- 2024)	1	2	0	1	1	1 : 4	-3	1	1.00
352	Connah's Quay Nomads	Connah's Quay Nomads	2	3	0	1	2	2 : 5	-3	1	0.50
353	Hammarby IF	Hammarby IF	1	2	0	1	1	1 : 5	-4	1	1.00
354	FC Differdange 03	FC Differdange 03	2	4	0	1	3	2 : 6	-4	1	0.50
355	Struga Trim & Lum	Struga Trim & Lum	2	4	0	1	3	4 : 8	-4	1	0.50
356	FC Suduroy	FC Suduroy	1	2	0	1	1	0 : 5	-5	1	1.00
357	Derry City	Derry City	2	4	0	1	3	0 : 5	-5	1	0.50
358	FC Norma Tallinn (- 1997)	FC Norma Tallinn (- 1997)	2	4	0	1	3	1 : 7	-6	1	0.50
359	Shakhter Soligorsk (- 2025)	Shakhter Soligorsk (- 2025)	3	6	0	1	5	0 : 6	-6	1	0.33
360	FK Kareda Kaunas (-2003)	FK Kareda Kaunas (-2003)	2	4	0	1	3	1 : 8	-7	1	0.50
361	Larne FC	Larne FC	2	4	0	1	3	2 : 10	-8	1	0.50
362	La Fiorita 1967	La Fiorita 1967	4	6	0	1	5	1 : 13	-12	1	0.25
363	FC Lusitanos	FC Lusitanos	2	4	0	1	3	3 : 16	-13	1	0.50
364	Cliftonville FC	Cliftonville FC	3	6	0	1	5	1 : 20	-19	1	0.33
365	Glentoran FC	Glentoran FC	4	8	0	1	7	2 : 22	-20	1	0.25
366	NK Lokomotiva Zagreb	NK Lokomotiva Zagreb	1	1	0	0	1	0 : 1	-1	0	
367	Everton FC	Everton FC	1	2	0	0	2	2 : 4	-2	0	
368	TSV 1860 Munich	TSV 1860 Munich	1	2	0	0	2	1 : 3	-2	0	
369	Zaglebie Lubin	Zaglebie Lubin	1	2	0	0	2	1 : 3	-2	0	
370	Lillestrøm SK	Lillestrøm SK	1	2	0	0	2	0 : 2	-2	0	
371	Budapest Honvéd FC	Budapest Honvéd FC	1	2	0	0	2	3 : 5	-2	0	
372	FK Teplice	FK Teplice	1	2	0	0	2	0 : 2	-2	0	
373	Valmiera FC	Valmiera FC	1	2	0	0	2	2 : 4	-2	0	
374	FC Inter Turku	FC Inter Turku	1	2	0	0	2	0 : 2	-2	0	
375	FC Ulisses Yerevan	FC Ulisses Yerevan	1	2	0	0	2	0 : 2	-2	0	
376	Atlètic Club d'Escaldes	Atlètic Club d'Escaldes	1	1	0	0	1	0 : 3	-3	0	
377	TSG 1899 Hoffenheim	TSG 1899 Hoffenheim	1	2	0	0	2	3 : 6	-3	0	
378	Strømsgodset IF	Strømsgodset IF	1	2	0	0	2	0 : 3	-3	0	
379	Dnepr Mogilev	Dnepr Mogilev	1	2	0	0	2	0 : 3	-3	0	
380	ETO FC Győr 	ETO FC Győr 	1	2	0	0	2	1 : 4	-3	0	
381	Sligo Rovers	Sligo Rovers	1	2	0	0	2	0 : 3	-3	0	
382	Lantana Tallinn (- 2000)	Lantana Tallinn (- 2000)	1	2	0	0	2	0 : 3	-3	0	
383	FCI Tallinn	FCI Tallinn	1	2	0	0	2	0 : 3	-3	0	
384	FC Dila Gori	FC Dila Gori	1	2	0	0	2	0 : 3	-3	0	
385	FK Liepaja	FK Liepaja	1	2	0	0	2	0 : 3	-3	0	
386	Vác FC	Vác FC	1	2	0	0	2	1 : 5	-4	0	
387	Makedonija Gjorce Petrov	Makedonija Gjorce Petrov	1	2	0	0	2	0 : 4	-4	0	
388	KF Trepca 89	KF Trepca 89	1	2	0	0	2	2 : 6	-4	0	
389	SS Folgore/Falciano	SS Folgore/Falciano	2	3	0	0	3	2 : 6	-4	0	
390	FC Toulouse	FC Toulouse	1	2	0	0	2	0 : 5	-5	0	
391	Motherwell FC	Motherwell FC	1	2	0	0	2	0 : 5	-5	0	
392	FC Paços de Ferreira	FC Paços de Ferreira	1	2	0	0	2	3 : 8	-5	0	
393	Zulte Waregem	Zulte Waregem	1	2	0	0	2	0 : 5	-5	0	
394	KF Teuta	KF Teuta	1	2	0	0	2	0 : 5	-5	0	
395	FC Rànger's	FC Rànger's	1	2	0	0	2	0 : 5	-5	0	
396	Renova Dzepciste	Renova Dzepciste	1	2	0	0	2	0 : 5	-5	0	
397	OFK Titograd	OFK Titograd	1	2	0	0	2	0 : 5	-5	0	
398	Stjarnan Gardabaer	Stjarnan Gardabaer	1	2	0	0	2	1 : 6	-5	0	
399	FC Yerevan (-2020)	FC Yerevan (-2020)	1	2	0	0	2	0 : 5	-5	0	
400	Herfölge Boldklub	Herfölge Boldklub	1	2	0	0	2	0 : 6	-6	0	
401	Lokomotiv Plovdiv	Lokomotiv Plovdiv	1	2	0	0	2	0 : 6	-6	0	
402	FC Nordsjaelland	FC Nordsjaelland	1	2	0	0	2	0 : 6	-6	0	
403	FC Samtredia	FC Samtredia	1	2	0	0	2	0 : 6	-6	0	
404	FK TSC Backa Topola	FK TSC Backa Topola	1	2	0	0	2	1 : 7	-6	0	
405	Spartak Vladikavkaz (-2020)	Spartak Vladikavkaz (-2020)	1	2	0	0	2	3 : 10	-7	0	
406	Marsaxlokk FC	Marsaxlokk FC	1	2	0	0	2	1 : 9	-8	0	
407	Araks Ararat	Araks Ararat	2	4	0	0	4	0 : 8	-8	0	
408	IFK Mariehamn	IFK Mariehamn	1	2	0	0	2	0 : 9	-9	0	
409	Daugava Daugavpils	Daugava Daugavpils	1	2	0	0	2	1 : 11	-10	0	
410	GI Gota	GI Gota	1	2	0	0	2	0 : 11	-11	0	
411	B68 Toftir	B68 Toftir	1	2	0	0	2	0 : 11	-11	0	
412	FC Avenir Beggen	FC Avenir Beggen	2	4	0	0	4	1 : 12	-11	0	
413	SS Murata	SS Murata	2	4	0	0	4	1 : 13	-12	0	
414	Bangor City (- 2025)	Bangor City (- 2025)	1	2	0	0	2	0 : 13	-13	0	
415	AC Virtus Acquaviva	AC Virtus Acquaviva	2	4	0	0	4	2 : 15	-13	0	
416	Rhyl FC (- 2020)	Rhyl FC (- 2020)	2	4	0	0	4	1 : 19	-18	0
'''

# Pattern for the new format: rank, club, club2, participations, matches, wins, draws, losses, goals, gd, points, points_per_tournament
pattern = re.compile(r"(\d+)\t([\w .\-()/]+)\t[\w .\-()/]+\t(\d+)\t(\d+)\t(\d+)\t(\d+)\t(\d+)\t(\d+) : (\d+)\t(-?\d+)\t(\d+)\t([\d.]+)")

entries = []
for match in pattern.finditer(raw_data):
    (
        rank, club, participations, matches, wins, draws, losses,
        goals_for, goals_against, gd, points, points_per_tournament
    ) = match.groups()
    entries.append({
        "rank": int(rank),
        "club": club.strip(),
        "participations": int(participations),
        "matches": int(matches),
        "wins": int(wins),
        "draws": int(draws),
        "losses": int(losses),
        "goals_for": int(goals_for),
        "goals_against": int(goals_against),
        "goal_difference": int(gd),
        "points": int(points),
        "points_per_tournament": float(points_per_tournament)
    })

with open("data/clq_champions_league_qualifying.json", "w") as f:
    json.dump(entries, f, indent=2)

print(f"Extracted {len(entries)} entries.")
