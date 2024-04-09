let postalCodeButton = document.getElementById('postal_code_button');
postalCodeButton.addEventListener('click', function() {
    let postalCode = document.getElementById('postal_code').value;
    console.log(postalCode);
    fetch('http://localhost:5000/map', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({postalCode: postalCode})
    })
    .then(response => response.json())
    .then(data => { console.log(data);})
    .catch(error => console.error('Erreur :', error));
});

document.addEventListener('DOMContentLoaded', function() {
    const questionParagraph = document.getElementById('question'); // Sélectionner le paragraphe de la question
    const buttons = document.querySelectorAll('.btn_response'); // Sélectionner les boutons de réponse
    let currentQuestion = 'Breathing Problem'; // Initialiser avec la première question

    buttons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Désactiver les boutons après une sélection
            buttons.forEach(btn => btn.disabled = true);

            // Envoyer la réponse au backend et obtenir la prochaine question
            fetch('http://localhost:5000/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({answer: this.value, question: currentQuestion})
            })
            .then(response => response.json())
            .then(data => {
                if (data.hasOwnProperty('question')) {
                    // Si une nouvelle question est reçue, mettre à jour l'affichage
                    questionParagraph.textContent = data.question;
                    // Réinitialiser les boutons pour la prochaine question
                    buttons.forEach(btn => {
                        btn.disabled = false;
                        currentQuestion = data.nextQuestionKey; // Mise à jour de la clé de la prochaine question
                    });
                } else {
                    // Si un résultat final est reçu, afficher le résultat
                    questionParagraph.textContent = data.resultat;
                    // Optionnellement, cacher les boutons ou indiquer la fin du questionnaire
                }
            })
            .catch(error => console.error('Erreur :', error));
        });
    });
});