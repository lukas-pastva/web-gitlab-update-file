document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('fileContent');
    const saveButton = document.getElementById('saveButton');
    const loadingIndicator = document.getElementById('loading');

    // Function to show loading spinner
    function showLoading() {
        loadingIndicator.style.display = 'block';
    }

    // Function to hide loading spinner
    function hideLoading() {
        loadingIndicator.style.display = 'none';
    }

    // Fetch the file content from the backend
    async function fetchFile() {
        showLoading();
        try {
            const response = await fetch('/api/get_file');
            const data = await response.json();

            if (response.ok) {
                textarea.value = data.content;
                textarea.disabled = false;
                saveButton.disabled = false;
            } else {
                textarea.placeholder = data.error || 'Failed to load file.';
                alert(data.error);
            }
        } catch (error) {
            textarea.placeholder = 'Error loading file.';
            alert('Error: ' + error.message);
        } finally {
            hideLoading();
        }
    }

    // Save the file content to the backend
    async function saveFile() {
        const confirmSave = confirm('Are you sure you want to save the changes?');
        if (!confirmSave) return;

        saveButton.disabled = true;
        showLoading();

        try {
            const content = textarea.value;
            const response = await fetch('/api/save_file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: content })
            });

            const data = await response.json();

            if (response.ok) {
                alert(data.message || 'File saved successfully!');
                fetchFile(); // Reload the file content
            } else {
                alert(data.error || 'Failed to save file.');
                saveButton.disabled = false;
            }
        } catch (error) {
            alert('Error: ' + error.message);
            saveButton.disabled = false;
        } finally {
            hideLoading();
        }
    }

    // Event listener for the save button
    saveButton.addEventListener('click', saveFile);

    // Initial fetch of the file content
    fetchFile();
});
