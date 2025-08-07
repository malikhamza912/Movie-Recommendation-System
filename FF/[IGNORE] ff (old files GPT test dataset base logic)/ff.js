const homePage = document.getElementById('home-page');
    const questionPage = document.getElementById('question-page');
    const questionContainer = document.getElementById('question-container');

    const questions = [
        {
            question: "What is your age?",
            options: ["10+", "13+", "16+", "18+"],
        },
        {
            question: "What is your preferred genre?",
            options: ["Action", "Drama", "Comedy", "Sci-Fi", "Horror", "Romance", "Adventure", "Thriller", "Fantasy", "Mystery", "Animation"],
        },
        {
            question: "What is your preferred year range?",
            options: ["1990-2000", "2000-2006", "2006-2010", "2010-2020", "2020-2024"],
        },
        {
            question: "What is your preferred rating?",
            options: ["1", "2", "3", "4", "5"],
        },
        {
            question: "What is your preferred duration range?",
            options: ["80-100 minutes", "101-120 minutes", "121-140 minutes", "141-160 minutes"],
        },
    ];

    let currentQuestionIndex = 0;
    let selectedOptions = Array(questions.length).fill(null);

    function renderQuestion() {
        const questionData = questions[currentQuestionIndex];
        questionContainer.innerHTML = `
            <h2>${questionData.question}</h2>
            <ul class="options">
                ${questionData.options.map((option, index) => `
                    <li class="option ${selectedOptions[currentQuestionIndex] === index ? 'selected' : ''}" data-index="${index}">${option}</li>
                `).join('')}
            </ul>
            <div class="navigation">
                ${currentQuestionIndex > 0 ? '<button id="previous-button">Previous</button>' : ''}
            </div>
        `;

        document.querySelectorAll('.option').forEach(option => {
            option.addEventListener('click', (e) => {
                const index = parseInt(e.target.getAttribute('data-index'));
                selectedOptions[currentQuestionIndex] = index;
                renderQuestion();
                if (currentQuestionIndex < questions.length - 1) {
                    currentQuestionIndex++;
                    renderQuestion();
                } else {
                    showResults();
                }
            });
        });

        if (currentQuestionIndex > 0) {
            document.getElementById('previous-button').addEventListener('click', () => {
                currentQuestionIndex--;
                renderQuestion();
            });
        }
    }

    function showResults() {
        questionPage.innerHTML = '<h2>Your recommended movies will appear here!</h2>';
    }

    document.getElementById('start-button').addEventListener('click', () => {
        homePage.style.display = 'none';
        questionPage.style.display = 'flex';
        questionPage.style.flexDirection = 'column';
        questionPage.style.justifyContent = 'center';
        questionPage.style.alignItems = 'center';
        renderQuestion();
    });