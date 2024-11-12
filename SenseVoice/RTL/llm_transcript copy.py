
# transcript = {  "1.0": "May 22-26, the World Economic Forum’s Annual Meeting will take place in Davos-Klosters, Switzerland, under the theme of Working Together, Restoring Trust. ",
#                 "11.0": "Business leaders, international political leaders, economists, celebrities and journalists come together to discuss global issues such as climate change and broader social challenges with regards to a sustainable future.",
#                 "23.0": "SAP announced that the jobs at SAP Landing Page for refugees from Ukraine is live. ",
#                 "30.0": "To support refugees from Ukraine, SAP is rolling out a dedicated onboarding process for refugees who have arrived in Bulgaria, Czech Republic, Germany, Hungary, Poland, Romania and Slovakia. ",
#                 "42.0": "This includes buddy support with an existing Ukrainian employee, mental health support and dedicated learning and language courses, childcare options (in selected countries) and advanced payment options for new hires. ",
#                 "54.0": "SAP is also working to extend this to other countries."
#             }

def prepare_prompt(user_question, current_position):

    return f"""
                Here is the transcript of the audio with timecodes: {transcript}.
                                        The audio is currently paused at {current_position} seconds.
                                        The user asked: {user_question}. 
                                        Please provide a response to the user, and also provide a transition sentence in your response 
                                        and suggest the next play position in seconds.
                                        the response should be in the following format
                                        {{
                                                "Response": {{
                                                    "action": "",
                                                    "new_position": "",
                                                    "Answer": "",
                                                    "Transition": ""
                                                }}
                                            }}                                                       
            """

transcript = {  "250": "May",
                "420": "22-26",
                "1980": ",",
                "2440": "the",
                "2580": "World",
                "2820": "Economic",
                "3260": "Forum",
                "3540": "’",
                "3540": "s",
                "3660": "Annual",
                "4060": "Meeting",
                "4340": "will",
                "4420": "take",
                "4620": "place",
                "4900": "in",
                "5020": "Davos-Klosters",
                "6020": ",",
                "6640": "Switzerland",
                "7380": ",",
                "7900": "under",
                "8170": "the",
                "8290": "theme",
                "8610": "of",
                "8730": "Working",
                "9090": "Together",
                "9450": ",",
                "10000": "Restoring",
                "10580": "Trust",
                "10900": ".",
                "11460": "Business",
                "11850": "leaders",
                "12170": ",",
                "12760": "international",
                "13390": "political",
                "13830": "leaders",
                "14110": ",",
                "14740": "economists",
                "15490": ",",
                "16080": "celebrities",
                "16740": "and",
                "16900": "journalists",
                "17340": "come",
                "17500": "together",
                "17820": "to",
                "17980": "discuss",
                "18300": "global",
                "18620": "issues",
                "19060": "such",
                "19380": "as",
                "19460": "climate",
                "19820": "change",
                "20140": "and",
                "20260": "broader",
                "20900": "social",
                "21320": "challenges",
                "21840": "with",
                "22000": "regards",
                "22360": "to",
                "22520": "a",
                "22600": "sustainable",
                "23160": "future",
                "23520": ".",
                "23520": "。",
                "24090": "SAP",
                "24440": "announced",
                "24800": "that",
                "24920": "the",
                "25040": "jobs",
                "25360": "at",
                "25480": "SAP",
                "25760": "Landing",
                "26080": "Page",
                "26400": "for",
                "26560": "refugees",
                "27120": "from",
                "27280": "Ukraine",
                "27640": "is",
                "27760": "live",
                "28040": "。",
                "28040": "。",
                "28040": "",
                "28290": "To",
                "440": "support",
                "800": "refugees",
                "1360": "from",
                "1520": "Ukraine",
                "1960": ",",
                "2510": "S",
                "2780": "A",
                "2980": "P",
                "3180": "is",
                "3300": "rolling",
                "3660": "out",
                "3780": "a",
                "3860": "dedicated",
                "4380": "onboarding",
                "4820": "process",
                "5220": "for",
                "5380": "refugees",
                "5940": "who",
                "6140": "have",
                "6300": "arrived",
                "6620": "in",
                "7100": "Bulgaria",
                "7690": ",",
                "8200": "Czech",
                "8540": "Republic",
                "8980": ",",
                "9530": "Germany",
                "9990": ",",
                "10530": "Hungary",
                "10990": ",",
                "11520": "Poland",
                "11950": ",",
                "12480": "Romania",
                "13020": "and",
                "13300": "Slovakia",
                "13940": ".",
                "14450": "This",
                "14670": "includes",
                "15030": "buddy",
                "15310": "support",
                "15670": "with",
                "15830": "an",
                "15910": "existing",
                "16390": "Ukrainian",
                "16870": "employee",
                "17350": ",",
                "17850": "mental",
                "18190": "health",
                "18430": "support",
                "18830": "and",
                "19030": "dedicated",
                "19550": "learning",
                "19910": "and",
                "20110": "language",
                "20510": "courses",
                "20910": ",",
                "21530": "childcare",
                "22040": "options",
                "22040": "(",
                "22480": "in",
                "22600": "selected",
                "23000": "countries",
                "23440": ")",
                "23440": "and",
                "23560": "advanced",
                "23960": "payment",
                "24280": "options",
                "24720": "for",
                "24840": "new",
                "25000": "hires",
                "25320": ".",
                "25910": "S",
                "26180": "A",
                "26380": "P",
                "26540": "is",
                "26660": "also",
                "26940": "working",
                "27260": "to",
                "27420": "extend",
                "27820": "this",
                "27980": "to",
                "28100": "other",
                "28260": "countries",
                "28660": "."
            }