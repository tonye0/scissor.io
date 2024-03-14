document.querySelector('.toggle-menu').addEventListener('click', function() {
        document.querySelector('.nav-links').classList.toggle('show');
    });


// Function to add a new row to the table
function addRow(index, longURL, shortURL, clicks) {
    var table = document.getElementById('history-table').getElementsByTagName('tbody')[0];
    var newRow = table.insertRow();

    var cellIndex = newRow.insertCell(0);
    var cellLongURL = newRow.insertCell(1);
    var cellShortURL = newRow.insertCell(2);
    var cellClicks = newRow.insertCell(3);

    cellIndex.innerHTML = index;
    cellLongURL.innerHTML = longURL;
    cellShortURL.innerHTML = shortURL;
    cellClicks.innerHTML = clicks;
}

// Example usage: addRow(1, 'https://example.com/longurl', 'http://short.url/abc123', 10);