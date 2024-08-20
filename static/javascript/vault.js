function getAccountData() {
    fetch('/data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const accountsTable = document.getElementById('accountsTable');
        accountsTable.innerHTML = '';  

        for (const [id, info] of Object.entries(data)) {
            const row = document.createElement('tr');

            row.innerHTML = `
                <td>${id}</td>
                <td>${info.name}</td>
                <td>${info.url}</td> <!-- Use 'url' instead of 'label' -->
                <td>
                    <input type="password" id="password-${id}" class="password-field" value="${info.password}" readonly>
                </td>
                <td class="actions">
                    <button onclick="togglePasswordVisibility('password-${id}', this)">View</button>
                    <button onclick="showEditModal('${id}', '${info.name}', '${info.url}', '${info.password}')">Edit</button> 
                    <button onclick="showDeleteModal('${id}')">Delete</button>
                </td>
            `;

            accountsTable.appendChild(row);
        }
    })
    .catch(error => console.error('Error:', error));
}

function togglePasswordVisibility(inputId, button) {
    const passwordField = document.getElementById(inputId);
    
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        button.textContent = 'Hide';
    } else {
        passwordField.type = 'password';
        button.textContent = 'View';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    getAccountData();

    // Add Modal Elements
    const addModal = document.getElementById('addModal');
    const addBtn = document.getElementById('addAccount');
    const addClose = document.getElementById('addClose');
    const addForm = document.getElementById('addForm');

    // Edit Modal Elements
    const editModal = document.getElementById('editModal');
    const editClose = document.getElementById('editClose');
    const editForm = document.getElementById('editForm');

    // Delete Modal Elements
    const deleteModal = document.getElementById('deleteModal');
    const deleteClose = document.getElementById('deleteClose');
    const confirmDelete = document.getElementById('confirmDelete');
    const cancelDelete = document.getElementById('cancelDelete');

    // Add Account Modal
    addBtn.onclick = () => addModal.style.display = 'block';
    addClose.onclick = () => addModal.style.display = 'none';

    addForm.onsubmit = async (event) => {
        event.preventDefault();
        const formData = { 
            name: document.getElementById('addName').value,
            url: document.getElementById('addUrl').value,
            password: document.getElementById('addPassword').value
        };
        try {
            const response = await fetch('/accounts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            getAccountData();
            addModal.style.display = 'none';
        } catch (error) {
            console.error('Error:', error); 
        }
    };

    // Edit Account Modal
    window.showEditModal = (id, name, url, password) => {
        document.getElementById('editId').value = id;
        document.getElementById('editName').value = name;
        document.getElementById('editUrl').value = url;
        document.getElementById('editPassword').value = password;
        editModal.style.display = 'block';
    };

    editClose.onclick = () => editModal.style.display = 'none';

    editForm.onsubmit = async (event) => {
        event.preventDefault();

        const formData = {
            id: document.getElementById('editId').value,
            name: document.getElementById('editName').value,
            url: document.getElementById('editUrl').value,
            password: document.getElementById('editPassword').value
        };

        try {
            const response = await fetch('/accounts', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            getAccountData();
            editModal.style.display = 'none';
        } catch (error) {
            console.error('Error:', error);
        }
    };

    // Delete Account Modal
    window.showDeleteModal = (id) => {
        deleteModal.style.display = 'block';

        confirmDelete.onclick = async () => {
            try {
                await fetch('/accounts', {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ id })
                });
                getAccountData();
                deleteModal.style.display = 'none';
            } catch (error) {
                console.error('Error:', error);
            }
        };
    };

    deleteClose.onclick = () => deleteModal.style.display = 'none';
    cancelDelete.onclick = () => deleteModal.style.display = 'none';

    // Search Accounts
    function searchAccounts() {
        const searchTerm = document.getElementById('searchBar').value.toLowerCase();
        const rows = document.querySelectorAll('#accountsTable tr');
        
        rows.forEach(row => {
            const urlCell = row.querySelector('td:nth-child(3)'); 
            if (urlCell) {
                const urlText = urlCell.textContent.toLowerCase();
                row.style.display = urlText.includes(searchTerm) ? '' : 'none';
            }
        });
    }

    document.getElementById('searchBar').addEventListener('input', searchAccounts);

    // Close Modals on Click Outside
    window.onclick = (event) => {
        if (event.target === addModal) addModal.style.display = 'none';
        if (event.target === editModal) editModal.style.display = 'none';
        if (event.target === deleteModal) deleteModal.style.display = 'none';
    };
});
