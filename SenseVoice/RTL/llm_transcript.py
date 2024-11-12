
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
            
            The audio is currently paused at: {current_position} in ms.

            The user asked: {user_question}. 

            Please provide a response to the user with following information:
                1) Action: this indicate what the next action should be done for the audio player, e.g. continue, pause, stop, etc. 
                2) New_position: this is the new position in ms where the audio should be resumed after the replied answer is played. 
                    Please apply the following rules when recommend new_position
                    1) Generally, new position should be the current_position. 
                    2) If you can not sure where should be the exact new_position, then set the new_position as current_position
                    3) If the question is about "repeat the previous senstence", just find the previous "." position, this will be
                       new_position. If there is no previous ".", then set the new_position as 0 which means start of the audio.
                    4) If the question is about "go to the <position> of the audio", then set the new_position there.
                3) Answer: this is the exact answer replied to the user's question. 
                    Apply following rules when replying the user's question
                    1) User's question maybe only related to the transcript, please provide the answer based on the transcript.
                    2) User's question maybe just as simple as repeating previous sentence, e.g. "I didn't hear that, please repeat the previous sentence",
                       the answer same should be empty because audio will be directly resumed at new_position after transition is played.
                    3) User's question maybe not related to the transcript, please also provide a general answer.
                    4) If you cannot answer with confidance, just set the answer as empty, and provide a polite transition.
                    4) Answer should be always in English.
                4) Transition: this is the transition sentence in your response. Transition will be played after answer finished.
                    Apply following rules when suggesting the transition sentences.
                    1)If there is no more user question raised, the transition sentence will be played before the audio continues.
                    e.g. "If no other questions, I will continue play the news"
                    2)Transition sentence should be a short sentence, not more than 20 words.
                    3)Transition sentence should be not empty everytime no matter what the user is ask about.
                    4)transition should be always in English.

            The response should be in the following format strictly
            {{
                    "Response": {{
                        "Question": "{user_question}",
                        "Current_position": "{current_position}",
                        "Action": "",
                        "New_position": "",
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
                "28730": "support",
                "29090": "refugees",
                "29650": "from",
                "29810": "Ukraine",
                "30250": ",",
                "30800": "S",
                "31070": "A",
                "31270": "P",
                "31470": "is",
                "31630": "rolling",
                "32050": "out",
                "32210": "a",
                "32370": "dedicated",
                "32860": "onboarding",
                "33310": "process",
                "33710": "for",
                "33930": "refugees",
                "34390": "who",
                "34610": "have",
                "34890": "arrived",
                "35210": "in",
                "35490": "Bulgaria",
                "36030": ",",
                "36580": "Czech",
                "36860": "Republic",
                "37320": ",",
                "37870": "Germany",
                "38330": ",",
                "38880": "Hungary",
                "39330": ",",
                "39880": "Poland",
                "40330": ",",
                "40880": "Romania",
                "41330": "and",
                "41590": "Slovakia",
                "41990": ".",
                "42540": "This",
                "42700": "includes",
                "43100": "buddy",
                "43360": "support",
                "43760": "with",
                "43980": "an",
                "44140": "existing",
                "44540": "Ukrainian",
                "45090": "employee",
                "45590": ",",
                "46140": "mental",
                "46430": "health",
                "46720": "support",
                "47120": "and",
                "47340": "dedicated",
                "47740": "learning",
                "48140": "and",
                "48360": "language",
                "48760": "courses",
                "49160": ",",
                "49610": "childcare",
                "50010": "options",
                "50010": "(",
                "50450": "in",
                "50610": "selected",
                "51010": "countries",
                "51450": ")",
                "51450": "and",
                "51670": "advanced",
                "52070": "payment",
                "52350": "options",
                "52750": "for",
                "52970": "new",
                "53130": "hires",
                "53530": ".",
                "54080": "S",
                "54360": "A",
                "54520": "P",
                "54780": "is",
                "54940": "also",
                "55220": "working",
                "55500": "to",
                "55720": "extend",
                "56120": "this",
                "56340": "to",
                "56560": "other",
                "56720": "countries",
                "56950": "."
            }