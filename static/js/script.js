document.addEventListener('DOMContentLoaded', function() {
    const allQuestionBlocks = document.querySelectorAll('.question-block');
    let responses = []; // Déclarer un tableau pour stocker les réponses

    let my_symptoms = {
        "Breathing Problem": [],
        "Fever": [],
        "Dry Cough": [],
        "Sore throat": [],
        "Running Nose": [],
        "Asthma": [],
        "Chronic Lung Disease": [],
        "Headache": [],
        "Heart Disease": [],
        "Diabetes": [],
        "Hyper Tension": [],
        "Fatigue ": [],
        "Gastrointestinal ": [],
        "Contact with COVID Patient": [],
        "Attended Large Gathering": [],
        "Visited Public Exposed Places": [],
        "Family working in Public Exposed Places": []
    };

    // Cacher toutes les questions sauf la première
    allQuestionBlocks.forEach(function(block, index) {
        if (index > 0) block.style.display = 'none';
    });

    // Fonction pour passer à la question suivante
    function goToNextQuestionBlock(currentIndex) {
        if (currentIndex + 1 < allQuestionBlocks.length) {
            allQuestionBlocks[currentIndex].style.display = 'none'; // Cacher le bloc actuel
            allQuestionBlocks[currentIndex + 1].style.display = 'block'; // Afficher le prochain bloc
        } else {
            // Si c'est le dernier bloc, le cacher aussi
            allQuestionBlocks[currentIndex].style.display = 'none';
        }
    }

    allQuestionBlocks.forEach(function(block, blockIndex) {
        // Sélection des boutons dans le bloc actuel avec un sélecteur plus général
        const buttons = block.querySelectorAll('button[id^="firstChoice"], button[id^="secondChoice"]');
        buttons.forEach(function(button) {
            button.addEventListener('click', function() {   
                this.disabled = true; // Désactiver le bouton sélectionné
                // Désactiver l'autre bouton dans le même bloc
                buttons.forEach(btn => {
                    if (btn !== this) btn.disabled = true;
                });
                responses.push(this.value); // Ajouter la valeur du bouton au tableau des réponses
                goToNextQuestionBlock(blockIndex); // Passer au bloc de questions suivant
                
                if (blockIndex === allQuestionBlocks.length - 1) {
                    // Mettre à jour my_symptoms avec les réponses
                    let i = 0;
                    for (let symptom in my_symptoms) {
                        my_symptoms[symptom].push(responses[i]);
                        i++;
                    }
                    console.log(my_symptoms);

                    // Envoi des données au serveur
                    let url = 'http://localhost:5000/chatbot';
                    fetch(url, {
                        method: 'POST',
                        headers: {
                            Accept: 'application/json',
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(my_symptoms)
                    })
                    .then(responses => responses.json())
                    .then(data => {
                        let message = '';
                        if (data.resultat === "Positif au COVID-19") {
                            message = 'Positif au COVID-19';
                        } else {
                            message = 'Négatif au COVID-19';
                        }

                        // Créer un nouvel élément div pour afficher le message
                        const messageDiv = document.createElement('div');
                        messageDiv.textContent = message; // Utiliser textContent pour des raisons de sécurité

                        // Ajouter des styles à messageDiv si nécessaire, exemple :
                        messageDiv.style.padding = '10px';
                        messageDiv.style.marginTop = '10px';
                        messageDiv.style.borderRadius = '5px';
                        messageDiv.style.backgroundColor = '#f0f0f0';
                        messageDiv.style.textAlign = 'center';
                        messageDiv.style.color = data.resultat === "Positif au COVID-19" ? 'red' : 'green'; // Couleur conditionnelle

                        // Sélectionner l'élément du formulaire ou un conteneur spécifique pour y ajouter messageDiv
                        const form = document.querySelector('form'); // Remplacer 'form' par le sélecteur correct si nécessaire
                        form.appendChild(messageDiv); // Ajouter messageDiv au formulaire
                    })
                    .catch(error => console.error(error));
                console.log(responses);
                }
            });
        });
    });
});