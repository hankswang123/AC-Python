
answer = [
            {
                    "Response": {
                        "Question": "Could you summarize the main idea of this audio?",
                        "Current_position": "",
                        "Action": "",
                        "New_position": "",
                        "Answer": "The audio summarizes the significance of rebuilding trust within the business sector.",
                        "Transition": "If you have any further questions, feel free to ask."
                    }
                },
            {
                    "Response": {
                        "Question": "What is the main idea of this audio?",
                        "Current_position": "",
                        "Action": "",
                        "New_position": "",
                        "Answer": "The main idea of this audio is to discuss the importance of restoring trust in the business community.",
                        "Transition": "If you have any further questions, feel free to ask."
                    }
                },
            {
                    "Response": {
                        "Question": "Why is it important to restoring trust in business community based on the audio?",
                        "Current_position": "",
                        "Action": "",
                        "New_position": "",
                        "Answer": "Restoring trust in the business community is crucial for fostering a healthy economic environment and ensuring sustainable growth.",
                        "Transition": "If you have any further questions, feel free to ask."
                    }
                },
            {
                    "Response": {
                        "Question": "What is Newton's laws?",
                        "Current_position": "",
                        "Action": "",
                        "New_position": "",
                        "Answer": "Newton's laws are three fundamental principles that describe the relationship between the motion of an object and the forces acting on it.",
                        "Transition": "If you have any further questions, feel free to ask."
                    }
                },
            {
                    "Response": {
                        "Question": "I did not hear clearly, please repeat the last sentence",
                        "Current_position": "",
                        "Action": "",
                        "New_position": "",
                        "Answer": "Sure, the last sentence was about the importance of trust in business relationships.",
                        "Transition": "If you have any further questions, feel free to ask."
                    }
                },
            {
                    "Response": {
                        "Question": "Yes, please",
                        "Current_position": "",
                        "Action": "",
                        "New_position": "",
                        "Answer": "Certainly! How can I assist you further?",
                        "Transition": "If you have any further questions, feel free to ask."
                    }
                }

]

# for debug purpose
if __name__ == "__main__":
    for i in range(len(answer)):
        print(i)
        print(answer[i]['Response']['Question'])
        print(answer[i]['Response']['Answer'])
        print(answer[i]['Response']['Transition'])
        print()