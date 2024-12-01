import pickle

topics = {
    "Technology and Programming": [
        "Write a Python program to sort a list of files by their last modified timestamp",
        # "Design a SQL database schema for a library management system including books, members, and transactions",
        # "Implement a binary search tree and write a function to find the second-largest element",
        # "Write a script to monitor a local folder and automatically back up new files to a cloud service",
        # "Create a simple blockchain program in Python that supports adding blocks and validating the chain",
        # "Build a REST API using FastAPI to manage a to-do list with create, read, update, and delete operations",
        # "Develop a Python script to convert CSV data into a JSON API response format",
        # "Write a function to parse and validate JSON Web Tokens (JWTs) in Python",
        # "Simulate a producer-consumer model using Python's threading library",
        # "Create a CLI tool to scrape a website for specific data (e.g., headlines or product prices)"
    ],
    "Logical Reasoning and Puzzles": [
        "Determine how to distribute 100 gold coins among three pirates, ensuring no one is killed during the distribution",
        # "Solve the puzzle: A prisoner is told to choose between two doors—one leads to freedom, the other to death. He can ask one guard one question. What should he ask?",
        # "Find the smallest number of moves needed to transfer all disks in a 6-disk Tower of Hanoi puzzle",
        # "Solve a 3x3 magic square puzzle where the sum of each row, column, and diagonal is 15",
        # "Write a step-by-step solution for a river crossing puzzle involving a farmer, a fox, a chicken, and a bag of grain",
        # "Calculate the minimum number of moves to solve a Rubik's cube given an initial configuration",
        # "Design an optimal strategy for a game where two players alternately take 1 to 3 sticks from a pile of 15 sticks",
        # "Solve a logic grid puzzle where three people (Alice, Bob, Charlie) each have different pets (dog, cat, parrot) and houses (red, blue, green)",
        # "Derive the probability of drawing at least one ace in a random 5-card poker hand",
        # "Explain the mathematical solution to the Monty Hall problem with clear examples"
    ],
    "Content Creation and Blogging": [
        "Write a blog post explaining how to write effective meta descriptions that increase click-through rates",
        # "Create a list of 10 actionable tips for writing compelling LinkedIn posts for tech professionals",
        # "Develop a guide on creating engaging infographics for technical blogs",
        # "Write a post comparing five popular CMS platforms (e.g., WordPress, Ghost, Squarespace, Wix, Drupal) based on SEO capabilities",
        # "Create a tutorial on how to set up and use Google Analytics to track blog performance",
        # "Write an article detailing the process of finding and using royalty-free images for blog posts",
        # "Outline the steps to create a personal blogging brand from scratch, including domain name selection",
        # "Write a script for a YouTube video on 'Top 5 Blogging Mistakes and How to Avoid Them'",
        # "Compile a list of the best WordPress plugins for increasing audience engagement",
        # "Explain how to schedule and manage posts across multiple platforms using tools like Buffer or Hootsuite"
    ],
    # "Artificial Intelligence and Machine Learning": [
    #     "Implement a neural network from scratch in Python using only NumPy",
    #     "Train a convolutional neural network (CNN) to classify handwritten digits using the MNIST dataset",
    #     "Write a program to predict house prices using scikit-learn's linear regression model",
    #     "Implement k-means clustering to segment customers based on purchase history",
    #     "Create a chatbot using OpenAI's GPT-3 API to answer basic programming questions",
    #     "Fine-tune a pre-trained BERT model for sentiment analysis on movie reviews",
    #     "Write a program to generate synthetic data for a given dataset using SMOTE",
    #     "Explain step-by-step how to evaluate a machine learning model using precision, recall, and F1-score",
    #     "Develop a recommendation system using collaborative filtering for movie ratings",
    #     "Implement a reinforcement learning agent to play the game of tic-tac-toe"
    # ],
    # "Philosophy and Ethics": [
    #     "Propose a detailed framework for governing the development of sentient AI systems",
    #     "Analyze the ethical considerations of using gene editing technologies like CRISPR in embryos",
    #     "Evaluate the moral implications of universal basic income in the context of AI-driven automation",
    #     "Compare the philosophical perspectives of utilitarianism and deontology in handling climate change",
    #     "Propose a set of ethical guidelines for creating virtual simulations of deceased people",
    #     "Critique the concept of the 'trolley problem' when applied to self-driving car algorithms",
    #     "Analyze the role of empathy in moral decision-making using real-world scenarios",
    #     "Explain Nietzsche's concept of 'eternal recurrence' with an example",
    #     "Explore the ethical implications of deepfake technology in politics and media",
    #     "Critically examine the idea of digital immortality from a philosophical perspective"
    # ],
    # "Science and Exploration": [
    #     "Explain the steps needed to establish a permanent human settlement on Mars",
    #     "Analyze the recent advancements in quantum computing and their potential applications",
    #     "Describe the process of DNA sequencing and how it is used in personalized medicine",
    #     "Explain how gravitational wave detection works using the LIGO observatory",
    #     "Write a detailed guide on the techniques used for carbon capture and storage",
    #     "Explain how CRISPR gene-editing works and its potential risks and benefits",
    #     "Analyze the feasibility of creating artificial black holes in controlled environments",
    #     "Write a detailed explanation of how solar sails can be used for interstellar travel",
    #     "Explain the difference between Type I, II, and III civilizations according to the Kardashev scale",
    #     "Describe the process and challenges involved in building a space elevator"
    # ],
    # "Creative Writing and Storytelling": [
    #     "Write a short story about a world where humans have evolved to live underwater",
    #     "Create a character sketch for a time-traveling historian who collects lost artifacts",
    #     "Write a dialogue between two characters arguing over the morality of creating clones",
    #     "Describe the setting of a post-apocalyptic city where plants have reclaimed the urban landscape",
    #     "Write a narrative from the perspective of an AI system gaining sentience and trying to communicate with humans",
    #     "Create a story where the protagonist discovers their memories have been implanted by a corporation",
    #     "Write the opening scene of a murder mystery set in a space station",
    #     "Develop a plot where a group of adventurers discovers an ancient civilization inside a hollow Earth",
    #     "Write a poem capturing the feeling of solitude in a distant galaxy",
    #     "Create a script for a dystopian play where language has been outlawed"
    # ],
    # "Health and Wellness": [
    #     "Write a guide to creating a daily meditation practice in under 10 minutes",
    #     "Explain how high-intensity interval training (HIIT) impacts metabolism and fat loss",
    #     "Write a step-by-step guide to tracking macronutrients for optimal health",
    #     "Explain the role of gut microbiota in mental health with supporting studies",
    #     "Write a tutorial on using a fitness tracker to monitor heart rate variability (HRV)",
    #     "Analyze the long-term effects of intermittent fasting on overall health",
    #     "Explain the connection between mindfulness practices and reduced anxiety levels",
    #     "Write a guide to improving sleep quality through cognitive behavioral therapy for insomnia (CBT-I)",
    #     "Create a workout plan for beginners that focuses on flexibility and strength",
    #     "Explain the physiological benefits of cold-water immersion therapy"
    # ]
}

with open("topics.pkl", "wb") as file:
    pickle.dump(topics, file)

print("Updated dictionary successfully pickled!")
