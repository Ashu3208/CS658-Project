document.getElementById('urlForm').addEventListener('submit', async function(event) {
    event.preventDefault();  // Prevent default form submission
    
    // Get the URL value from the input field
    const urlValue = document.getElementById('url').value;

    // Send the data as JSON via a POST request
    try {
        const response = await fetch('https://cs658-5den.onrender.com/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: urlValue }),  // Sending the URL in JSON format
        });

        // Check if the request was successful
        if (response.ok) {
            const data = await response.json();  // Assuming the response is JSON
            console.log('Prediction Response:', data);

            // Show the result section
            const resultSection = document.getElementById('result');
            const modelResults = document.getElementById('modelResults');
            
            // Clear previous results
            modelResults.innerHTML = '';
            
            // Populate the results dynamically
            for (const model in data) {
                const resultDiv = document.createElement('div');
                resultDiv.className = 'model-result';
                resultDiv.innerHTML = `<strong>${model}:</strong> 
                                        Encoded Prediction: ${data[model].encoded_prediction}, 
                                        Human-Readable Label: ${data[model].human_readable_label}`;
                modelResults.appendChild(resultDiv);
            }

            // Make the result section visible
            resultSection.style.display = 'block';
        } else {
            console.error('Error:', response.statusText);
            alert('Error occurred during prediction.');
        }
    } catch (error) {
        console.error('Request failed:', error);
        alert('Failed to submit the data.');
    }
});