# 📚 Flashcard Web App: Learn Smarter, Study Faster!

Welcome to the **Flashcard Web App** GitHub repository! 🎉 This project is a Flask-based web application designed to help users study effectively using customizable flashcards. Whether you're learning a new language, preparing for an exam, or mastering technical concepts, this app empowers you to organize your study materials efficiently.

## 🛠 Project Overview

Developed by a data engineer with a passion for coding and powered by the **Gemini Pro 2.5** keyboard and the **Roo Code** plugin in VSCode, this project showcases the blend of technical excellence and creative energy.

### Repository Structure

The repository consists of two folders:

1. **`flashcard_app/`**: The main folder containing the Flask web app code, including backend logic and frontend UI.
2. **`my_flashcard_data/`**: The persistence data folder for the Flask web app, including database and progress tracking file.
3. **`idea/`**: A folder that houses all draft ideas, brainstorming notes, and detailed plans for each phase of development.

## 🚀 Features

- **Create Flashcards**: Add questions and answers to build your personalized flashcard deck.
- **Organize by Categories**: Group flashcards into categories for streamlined learning.
- **Interactive Learning**: Cycle through flashcards to test your knowledge.
- **Progress Tracking**: (Coming Soon!) Track your performance and improvement over time.
- **Responsive Design**: Optimized for both desktop and mobile devices.


## 📁 Folder Details

### 1. `flashcard_app/`

- Contains the Flask application with the main codebase.
- Includes:
    - **Backend**: Python files for server-side logic, database interactions, and API endpoints.
    - **Frontend**: HTML templates, CSS for styling, and JavaScript for interactivity.
    - Configuration files for hosting, database setup, and environment variables.

### 2. `my_flashcard_data/`

- A persistence storage for the Flask application.
- Includes:
    - **database**: Stores datasets including questions, anwsers and correct answer.
    - **json**: Tracking progress of studying for each dataset.
    - **example_topics/**: Contains a sample csv file to initiate if user do not know the required format of a csv.

### 3. `idea/`

- A hub for brainstorming and planning future features.
- Includes:
    - Draft ideas for features like gamified learning, AI-driven flashcard suggestions, and progress analytics.
    - Detailed phase-by-phase development plans.
    - Notes and sketches for UI/UX design improvements.


## 🛠️ Installation Instructions

Follow these steps to set up the app locally:

### Prerequisites

- Python
- Docker

### Steps

1. **Clone the repository**:

```
git clone https://github.com/thevivotran/studytest.git
cd studytest
```


2. **Build App**:

```
make build
```

3. **Run the Flask server**:

```
make
```

4. **Open in a browser**:
Visit `http://127.0.0.1:5000` to play around with the app.


5. **Add an example dataset**:
- Input the Dataset name, such as "Example".
- Select CSV file, choose the [text](my_flashcard_data/topics/GCP_DE_Pro.csv) file.
- Hit the Upload Dataset

6. **Explore the feature of the app**

## 💡 Development Philosophy

This project was built with the mindset of iterating on ideas gradually while enjoying the coding process. Using the **Gemini Pro 2.5** keyboard and **Roo Code** plugin, every line of code was written with precision and care. The "idea-first" approach ensures each feature is thoughtfully planned and executed.


## 🤝 Contributions

Contributions are welcome! If you'd like to improve existing features, fix bugs, or add new functionalities, feel free to fork the repository and submit a pull request.

## 📄 License

This repository is open-sourced under the [MIT License](LICENSE). Feel free to use and modify it, but don’t forget to give credit to the original developer.

## 🙌 Thanks for Checking It Out!

If you find this project helpful, please ⭐ star the repository. Your support motivates further development!

For any questions or feedback, feel free to reach out via GitHub issues.

---

Enjoy using the Flashcard Web App and happy studying! 🎓
