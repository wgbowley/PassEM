function escapeHtml(value) {
    return value.replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

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
                <td>${escapeHtml(info.name)}</td>
                <td>${escapeHtml(info.url)}</td>
                <td>
                    <input type="password" id="password-${id}" class="password-field" value="${escapeHtml(info.password)}" readonly>
                </td>
                <td class="actions">
                    <button onclick="togglePasswordVisibility('password-${id}', this)">View</button>
                    <button class="edit-btn"
                        data-id="${id}"
                        data-name="${escapeHtml(info.name)}"
                        data-url="${escapeHtml(info.url)}"
                        data-password="${escapeHtml(info.password)}">
                        Edit
                    </button>
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

    const addModal = document.getElementById('addModal');
    const addBtn = document.getElementById('addAccount');
    const addClose = document.getElementById('addClose');
    const addForm = document.getElementById('addForm');

    const editModal = document.getElementById('editModal');
    const editClose = document.getElementById('editClose');
    const editForm = document.getElementById('editForm');

    const deleteModal = document.getElementById('deleteModal');
    const deleteClose = document.getElementById('deleteClose');
    const confirmDelete = document.getElementById('confirmDelete');
    const cancelDelete = document.getElementById('cancelDelete');

    // Add Account
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
            await response.json();
            getAccountData();
            addModal.style.display = 'none';
        } catch (error) {
            console.error('Error:', error);
        }
    };

    // Handle Edit Button Clicks
    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('edit-btn')) {
            const btn = event.target;
            const id = btn.dataset.id;
            const name = btn.dataset.name;
            const url = btn.dataset.url;
            const password = btn.dataset.password;

            document.getElementById('editId').value = id;
            document.getElementById('editName').value = name;
            document.getElementById('editUrl').value = url;
            document.getElementById('editPassword').value = password;
            editModal.style.display = 'block';
        }
    });

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
            await response.json();
            getAccountData();
            editModal.style.display = 'none';
        } catch (error) {
            console.error('Error:', error);
        }
    };

    // Delete Account
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

    // Search
    document.getElementById('searchBar').addEventListener('input', () => {
        const searchTerm = document.getElementById('searchBar').value.toLowerCase();
        const rows = document.querySelectorAll('#accountsTable tr');
        rows.forEach(row => {
            const urlCell = row.querySelector('td:nth-child(3)');
            if (urlCell) {
                const urlText = urlCell.textContent.toLowerCase();
                row.style.display = urlText.includes(searchTerm) ? '' : 'none';
            }
        });
    });

    // Close modals on outside click
    window.onclick = (event) => {
        if (event.target === addModal) addModal.style.display = 'none';
        if (event.target === editModal) editModal.style.display = 'none';
        if (event.target === deleteModal) deleteModal.style.display = 'none';
    };
});
