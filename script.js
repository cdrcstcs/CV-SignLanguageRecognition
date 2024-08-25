document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const outputText = document.getElementById('output-text');
    const charac = document.getElementById('con');
    let stream = null; // Declare stream variable
    let stringChar = ""; // Initialize stringChar

    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then((s) => {
                stream = s;
                video.srcObject = stream;
            })
            .catch((err) => {
                console.error('Error accessing the camera: ', err);
            });
    }

    const context = canvas.getContext('2d');

    setInterval(() => {
        context.drawImage(video, 0, 0, 640, 480);
        const imageData = canvas.toDataURL('image/jpeg')
        sendImageData(imageData);
    }, 3000);

    function sendImageData(base64Data) {
        // Convert imageData to base64 string
        fetch('http://localhost:5000/process_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image_data: base64Data })
        })
        .then(response => response.json())
        .then(data => {
            stringChar += data.text; // Accumulate characters
            charac.textContent = data.text;
            if (charac.style.color == 'aqua'){
                charac.style.color = 'green' 
            } else {
                charac.style.color = 'aqua'
            }
            // Check if formed word is an English word
            fetch('http://localhost:5000/check_word', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ word: stringChar })
            })
            .then(response => response.json())
            .then(data => {
                if (data.check) {
                    outputText.textContent += stringChar; // Update output text
                    // Convert accumulated text to speech
                    speakText(stringChar);
                    stringChar = ""; // Clear stringChar if it's a valid English word
                }
            })
            .catch(error => {
                console.error('Error checking word: ', error);
            });
        })
        .catch(error => {
            console.error('Error processing image: ', error);
        });
    }

    // Function to speak the provided text
    function speakText(text) {
        const utterance = new SpeechSynthesisUtterance(text);
        speechSynthesis.speak(utterance);
    }
});
