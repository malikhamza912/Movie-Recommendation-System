// app.js

let currentQuestionIndex = 0;
let selectedOptions = [];

function renderQuestion(questionData) {
    const isMultiSelect = questionData.isMultiSelect;

    const container = document.createElement('div');
    container.innerHTML = `
        <h2>${questionData.question}</h2>
        <div class="${isMultiSelect ? 'grid-options' : 'options'}">
            ${questionData.options.map((option, index) => `
                <label>
                    <input type="${isMultiSelect ? 'checkbox' : 'radio'}" 
                           name="question-${currentQuestionIndex}" 
                           value="${index}" 
                           ${selectedOptions[currentQuestionIndex]?.includes(index) ? 'checked' : ''}>
                    ${option}
                </label>
            `).join('')}
        </div>
        <div class="navigation">
            ${currentQuestionIndex > 0 ? '<button id="previous-button">Go Back</button>' : ''}
            <button id="next-button">${currentQuestionIndex === questions.length - 1 ? 'Finish' : 'Next'}</button>
        </div>
    `;

    document.body.appendChild(container);

    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('change', (e) => {
            const index = parseInt(e.target.value);
            if (isMultiSelect) {
                if (e.target.checked) {
                    selectedOptions[currentQuestionIndex].push(index);
                } else {
                    selectedOptions[currentQuestionIndex] = selectedOptions[currentQuestionIndex].filter(i => i !== index);
                }
            } else {
                selectedOptions[currentQuestionIndex] = [index];
            }
        });
    });

    if (currentQuestionIndex > 0) {
        document.getElementById('previous-button').addEventListener('click', () => {
            currentQuestionIndex--;
            renderQuestion(questions[currentQuestionIndex]);
        });
    }

    document.getElementById('next-button').addEventListener('click', () => {
        if (currentQuestionIndex < questions.length - 1) {
            currentQuestionIndex++;
            renderQuestion(questions[currentQuestionIndex]);
        } else {
            showResults();
        }
    });
}

function showResults() {
    const userPreferences = questions.map((q, i) => ({
        question: q.question,
        answers: selectedOptions[i].map(index => q.options[index]),
    }));

    fetch('http://127.0.0.1:5000/submit_preferences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: userId, preferences: userPreferences }),
    })
    .then(response => response.json())
    .then(data => {
        const recommendationContainer = document.createElement('div');
        recommendationContainer.innerHTML = `
            <h2>Recommended Movies</h2>
            <ul id="recommendations">
                ${data.recommendations.map(movie => `<li>${movie}</li>`).join('')}
            </ul>
            <button id="restart-button">Restart</button>
        `;
        document.body.appendChild(recommendationContainer);

        document.getElementById('restart-button').addEventListener('click', () => {
            currentQuestionIndex = 0;
            selectedOptions = Array(questions.length).fill(null).map(() => []);
            document.body.innerHTML = '';
            document.getElementById('home-page').style.display = 'block';
        });
    })
    .catch(error => console.error('Error:', error));
}

// Initial setup
const questions = [
    // ... (keep the existing questions array)
];

const userId = Math.floor(Math.random() * 10000);
console.log("Generated Unique User ID:", userId);

fetchExistingUserIds();

document.getElementById('start-button').addEventListener('click', () => {
    document.getElementById('home-page').style.display = 'none';
    renderQuestion();
});
