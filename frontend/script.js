// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Global State
let currentSection = 'dashboard';
let users = [];
let categories = [];
let ingredients = [];
let recipes = [];

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    setupEventListeners();
    await loadInitialData();
    showDashboard();
}

// Event Listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const section = this.dataset.section;
            navigateToSection(section);
        });
    });

    // Forms
    document.getElementById('user-form').addEventListener('submit', handleUserSubmit);
    document.getElementById('category-form').addEventListener('submit', handleCategorySubmit);
    document.getElementById('ingredient-form').addEventListener('submit', handleIngredientSubmit);
    document.getElementById('recipe-form').addEventListener('submit', handleRecipeSubmit);

    // Search and Filters
    document.getElementById('user-search').addEventListener('input', debounce(filterUsers, 300));
    document.getElementById('user-status-filter').addEventListener('change', filterUsers);
    document.getElementById('category-search').addEventListener('input', debounce(filterCategories, 300));
    document.getElementById('ingredient-search').addEventListener('input', debounce(filterIngredients, 300));
    document.getElementById('recipe-search').addEventListener('input', debounce(filterRecipes, 300));
    document.getElementById('recipe-category-filter').addEventListener('change', filterRecipes);
    document.getElementById('recipe-difficulty-filter').addEventListener('change', filterRecipes);

    // Modal close on outside click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this.id);
            }
        });
    });
}

// API Functions
async function apiRequest(endpoint, options = {}) {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }

        return await response.json();
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

// Data Loading Functions
async function loadInitialData() {
    try {
        await Promise.all([
            loadUsers(),
            loadCategories(), 
            loadIngredients(),
            loadRecipes()
        ]);
    } catch (error) {
        showToast('Error loading initial data', 'error');
    }
}

async function loadUsers() {
    try {
        users = await apiRequest('/users/');
        renderUsers();
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

async function loadCategories() {
    try {
        categories = await apiRequest('/categories/');
        renderCategories();
        populateCategoryFilters();
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadIngredients() {
    try {
        ingredients = await apiRequest('/ingredients/');
        renderIngredients();
        populateIngredientSelects();
    } catch (error) {
        console.error('Error loading ingredients:', error);
    }
}

async function loadRecipes() {
    try {
        recipes = await apiRequest('/recipes/');
        renderRecipes();
    } catch (error) {
        console.error('Error loading recipes:', error);
    }
}

// Navigation
function navigateToSection(section) {
    // Update navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-section="${section}"]`).classList.add('active');

    // Update sections
    document.querySelectorAll('.section').forEach(sec => {
        sec.classList.remove('active');
    });
    document.getElementById(section).classList.add('active');

    currentSection = section;

    // Load section-specific data if needed
    switch(section) {
        case 'dashboard':
            showDashboard();
            break;
    }
}

// Dashboard
async function showDashboard() {
    try {
        const [usersCount, categoriesCount, ingredientsCount, recipesCount] = await Promise.all([
            apiRequest('/users/count'),
            apiRequest('/categories/count'),
            apiRequest('/ingredients/count'),
            apiRequest('/recipes/count')
        ]);

        document.getElementById('total-users').textContent = usersCount.total;
        document.getElementById('total-categories').textContent = categoriesCount.total;
        document.getElementById('total-ingredients').textContent = ingredientsCount.total;
        document.getElementById('total-recipes').textContent = recipesCount.total;

        // Show recent recipes
        const recentRecipes = recipes.slice(0, 6);
        renderRecentRecipes(recentRecipes);
    } catch (error) {
        showToast('Error loading dashboard data', 'error');
    }
}

function renderRecentRecipes(recentRecipes) {
    const container = document.getElementById('recent-recipes-list');
    
    if (recentRecipes.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">No hay recetas disponibles</p>';
        return;
    }

    container.innerHTML = recentRecipes.map(recipe => `
        <div class="recipe-card">
            <div class="recipe-header">
                <h4 class="recipe-title">${recipe.title}</h4>
                <div class="recipe-meta">
                    ${recipe.prep_time ? `<span><i class="fas fa-clock"></i> ${recipe.prep_time + (recipe.cook_time || 0)} min</span>` : ''}
                    ${recipe.servings ? `<span><i class="fas fa-users"></i> ${recipe.servings} porciones</span>` : ''}
                </div>
                <p class="recipe-description">${recipe.description || 'Sin descripción'}</p>
            </div>
            <div class="recipe-footer">
                <div class="recipe-tags">
                    ${recipe.difficulty ? `<span class="tag difficulty-${recipe.difficulty}">${getDifficultyText(recipe.difficulty)}</span>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

// Users Management
function renderUsers(filteredUsers = users) {
    const tbody = document.getElementById('users-table-body');
    
    if (filteredUsers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No hay usuarios disponibles</td></tr>';
        return;
    }

    tbody.innerHTML = filteredUsers.map(user => `
        <tr>
            <td>${user.id}</td>
            <td>${user.username}</td>
            <td>${user.email}</td>
            <td>${user.full_name}</td>
            <td><span class="status-badge ${user.is_active ? 'status-active' : 'status-inactive'}">${user.is_active ? 'Activo' : 'Inactivo'}</span></td>
            <td>
                <div class="action-buttons">
                    <button class="btn-icon btn-edit" onclick="editUser(${user.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-delete" onclick="deleteUser(${user.id})" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function filterUsers() {
    const search = document.getElementById('user-search').value.toLowerCase();
    const status = document.getElementById('user-status-filter').value;

    let filtered = users.filter(user => {
        const matchesSearch = user.username.toLowerCase().includes(search) ||
                            user.email.toLowerCase().includes(search) ||
                            user.full_name.toLowerCase().includes(search);
        
        const matchesStatus = status === '' || user.is_active.toString() === status;

        return matchesSearch && matchesStatus;
    });

    renderUsers(filtered);
}

async function handleUserSubmit(e) {
    e.preventDefault();
    
    const userId = document.getElementById('user-id').value;
    const userData = {
        username: document.getElementById('user-username').value,
        email: document.getElementById('user-email').value,
        full_name: document.getElementById('user-fullname').value,
        is_active: document.getElementById('user-active').value === 'true'
    };

    try {
        if (userId) {
            // Update user
            await apiRequest(`/users/${userId}`, {
                method: 'PUT',
                body: JSON.stringify(userData)
            });
            showToast('Usuario actualizado correctamente', 'success');
        } else {
            // Create user
            await apiRequest('/users/', {
                method: 'POST',
                body: JSON.stringify(userData)
            });
            showToast('Usuario creado correctamente', 'success');
        }
        
        closeModal('user-modal');
        await loadUsers();
    } catch (error) {
        showToast('Error al guardar usuario', 'error');
    }
}

function editUser(userId) {
    const user = users.find(u => u.id === userId);
    if (!user) return;

    document.getElementById('user-modal-title').textContent = 'Editar Usuario';
    document.getElementById('user-id').value = user.id;
    document.getElementById('user-username').value = user.username;
    document.getElementById('user-email').value = user.email;
    document.getElementById('user-fullname').value = user.full_name;
    document.getElementById('user-active').value = user.is_active.toString();

    openModal('user-modal');
}

async function deleteUser(userId) {
    if (!confirm('¿Estás seguro de que quieres eliminar este usuario?')) return;

    try {
        await apiRequest(`/users/${userId}`, { method: 'DELETE' });
        showToast('Usuario eliminado correctamente', 'success');
        await loadUsers();
    } catch (error) {
        showToast('Error al eliminar usuario', 'error');
    }
}

// Categories Management
function renderCategories(filteredCategories = categories) {
    const container = document.getElementById('categories-grid');
    
    if (filteredCategories.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">No hay categorías disponibles</p>';
        return;
    }

    container.innerHTML = filteredCategories.map(category => `
        <div class="card">
            <div class="card-header">
                <h4 class="card-title">${category.name}</h4>
                <p class="card-description">${category.description || 'Sin descripción'}</p>
            </div>
            <div class="card-footer">
                <span class="text-muted">ID: ${category.id}</span>
                <div class="action-buttons">
                    <button class="btn-icon btn-edit" onclick="editCategory(${category.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-delete" onclick="deleteCategory(${category.id})" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function filterCategories() {
    const search = document.getElementById('category-search').value.toLowerCase();
    
    let filtered = categories.filter(category => {
        return category.name.toLowerCase().includes(search) ||
               (category.description && category.description.toLowerCase().includes(search));
    });

    renderCategories(filtered);
}

async function handleCategorySubmit(e) {
    e.preventDefault();
    
    const categoryId = document.getElementById('category-id').value;
    const categoryData = {
        name: document.getElementById('category-name').value,
        description: document.getElementById('category-description').value
    };

    try {
        if (categoryId) {
            await apiRequest(`/categories/${categoryId}`, {
                method: 'PUT',
                body: JSON.stringify(categoryData)
            });
            showToast('Categoría actualizada correctamente', 'success');
        } else {
            await apiRequest('/categories/', {
                method: 'POST',
                body: JSON.stringify(categoryData)
            });
            showToast('Categoría creada correctamente', 'success');
        }
        
        closeModal('category-modal');
        await loadCategories();
    } catch (error) {
        showToast('Error al guardar categoría', 'error');
    }
}

function editCategory(categoryId) {
    const category = categories.find(c => c.id === categoryId);
    if (!category) return;

    document.getElementById('category-modal-title').textContent = 'Editar Categoría';
    document.getElementById('category-id').value = category.id;
    document.getElementById('category-name').value = category.name;
    document.getElementById('category-description').value = category.description || '';

    openModal('category-modal');
}

async function deleteCategory(categoryId) {
    if (!confirm('¿Estás seguro de que quieres eliminar esta categoría?')) return;

    try {
        await apiRequest(`/categories/${categoryId}`, { method: 'DELETE' });
        showToast('Categoría eliminada correctamente', 'success');
        await loadCategories();
    } catch (error) {
        showToast('Error al eliminar categoría', 'error');
    }
}

// Ingredients Management
function renderIngredients(filteredIngredients = ingredients) {
    const container = document.getElementById('ingredients-grid');
    
    if (filteredIngredients.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">No hay ingredientes disponibles</p>';
        return;
    }

    container.innerHTML = filteredIngredients.map(ingredient => `
        <div class="card">
            <div class="card-header">
                <h4 class="card-title">${ingredient.name}</h4>
                <p class="card-description">${ingredient.description || 'Sin descripción'}</p>
                ${ingredient.unit ? `<p class="text-muted"><strong>Unidad:</strong> ${ingredient.unit}</p>` : ''}
            </div>
            <div class="card-footer">
                <span class="text-muted">ID: ${ingredient.id}</span>
                <div class="action-buttons">
                    <button class="btn-icon btn-edit" onclick="editIngredient(${ingredient.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-delete" onclick="deleteIngredient(${ingredient.id})" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function filterIngredients() {
    const search = document.getElementById('ingredient-search').value.toLowerCase();
    
    let filtered = ingredients.filter(ingredient => {
        return ingredient.name.toLowerCase().includes(search) ||
               (ingredient.description && ingredient.description.toLowerCase().includes(search)) ||
               (ingredient.unit && ingredient.unit.toLowerCase().includes(search));
    });

    renderIngredients(filtered);
}

async function handleIngredientSubmit(e) {
    e.preventDefault();
    
    const ingredientId = document.getElementById('ingredient-id').value;
    const ingredientData = {
        name: document.getElementById('ingredient-name').value,
        description: document.getElementById('ingredient-description').value,
        unit: document.getElementById('ingredient-unit').value
    };

    try {
        if (ingredientId) {
            await apiRequest(`/ingredients/${ingredientId}`, {
                method: 'PUT',
                body: JSON.stringify(ingredientData)
            });
            showToast('Ingrediente actualizado correctamente', 'success');
        } else {
            await apiRequest('/ingredients/', {
                method: 'POST',
                body: JSON.stringify(ingredientData)
            });
            showToast('Ingrediente creado correctamente', 'success');
        }
        
        closeModal('ingredient-modal');
        await loadIngredients();
    } catch (error) {
        showToast('Error al guardar ingrediente', 'error');
    }
}

function editIngredient(ingredientId) {
    const ingredient = ingredients.find(i => i.id === ingredientId);
    if (!ingredient) return;

    document.getElementById('ingredient-modal-title').textContent = 'Editar Ingrediente';
    document.getElementById('ingredient-id').value = ingredient.id;
    document.getElementById('ingredient-name').value = ingredient.name;
    document.getElementById('ingredient-description').value = ingredient.description || '';
    document.getElementById('ingredient-unit').value = ingredient.unit || '';

    openModal('ingredient-modal');
}

async function deleteIngredient(ingredientId) {
    if (!confirm('¿Estás seguro de que quieres eliminar este ingrediente?')) return;

    try {
        await apiRequest(`/ingredients/${ingredientId}`, { method: 'DELETE' });
        showToast('Ingrediente eliminado correctamente', 'success');
        await loadIngredients();
    } catch (error) {
        showToast('Error al eliminar ingrediente', 'error');
    }
}

// Recipes Management
function renderRecipes(filteredRecipes = recipes) {
    const container = document.getElementById('recipes-grid');
    
    if (filteredRecipes.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">No hay recetas disponibles</p>';
        return;
    }

    container.innerHTML = filteredRecipes.map(recipe => `
        <div class="recipe-card">
            <div class="recipe-header">
                <h4 class="recipe-title">${recipe.title}</h4>
                <div class="recipe-meta">
                    ${recipe.prep_time ? `<span><i class="fas fa-clock"></i> ${recipe.prep_time} min prep</span>` : ''}
                    ${recipe.cook_time ? `<span><i class="fas fa-fire"></i> ${recipe.cook_time} min cocción</span>` : ''}
                    ${recipe.servings ? `<span><i class="fas fa-users"></i> ${recipe.servings} porciones</span>` : ''}
                </div>
                <p class="recipe-description">${recipe.description || 'Sin descripción'}</p>
                <div class="recipe-tags">
                    ${recipe.difficulty ? `<span class="tag difficulty-${recipe.difficulty}">${getDifficultyText(recipe.difficulty)}</span>` : ''}
                    <span class="tag">Categoría: ${getCategoryName(recipe.category_id)}</span>
                    <span class="tag">Autor: ${getUserName(recipe.author_id)}</span>
                </div>
            </div>
            <div class="recipe-footer">
                <span class="text-muted">ID: ${recipe.id}</span>
                <div class="action-buttons">
                    <button class="btn-icon btn-edit" onclick="editRecipe(${recipe.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-delete" onclick="deleteRecipe(${recipe.id})" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function filterRecipes() {
    const search = document.getElementById('recipe-search').value.toLowerCase();
    const categoryFilter = document.getElementById('recipe-category-filter').value;
    const difficultyFilter = document.getElementById('recipe-difficulty-filter').value;
    
    let filtered = recipes.filter(recipe => {
        const matchesSearch = recipe.title.toLowerCase().includes(search) ||
                            (recipe.description && recipe.description.toLowerCase().includes(search)) ||
                            (recipe.instructions && recipe.instructions.toLowerCase().includes(search));
        
        const matchesCategory = !categoryFilter || recipe.category_id.toString() === categoryFilter;
        const matchesDifficulty = !difficultyFilter || recipe.difficulty === difficultyFilter;

        return matchesSearch && matchesCategory && matchesDifficulty;
    });

    renderRecipes(filtered);
}

async function handleRecipeSubmit(e) {
    e.preventDefault();
    
    const recipeId = document.getElementById('recipe-id').value;
    const ingredientSelect = document.getElementById('recipe-ingredients');
    const selectedIngredients = Array.from(ingredientSelect.selectedOptions).map(option => parseInt(option.value));
    
    const recipeData = {
        title: document.getElementById('recipe-title').value,
        description: document.getElementById('recipe-description').value,
        instructions: document.getElementById('recipe-instructions').value,
        prep_time: parseInt(document.getElementById('recipe-prep-time').value) || null,
        cook_time: parseInt(document.getElementById('recipe-cook-time').value) || null,
        servings: parseInt(document.getElementById('recipe-servings').value) || null,
        difficulty: document.getElementById('recipe-difficulty').value || null,
        author_id: parseInt(document.getElementById('recipe-author').value),
        category_id: parseInt(document.getElementById('recipe-category').value),
        ingredient_ids: selectedIngredients
    };

    try {
        if (recipeId) {
            await apiRequest(`/recipes/${recipeId}`, {
                method: 'PUT',
                body: JSON.stringify(recipeData)
            });
            showToast('Receta actualizada correctamente', 'success');
        } else {
            await apiRequest('/recipes/', {
                method: 'POST',
                body: JSON.stringify(recipeData)
            });
            showToast('Receta creada correctamente', 'success');
        }
        
        closeModal('recipe-modal');
        await loadRecipes();
    } catch (error) {
        showToast('Error al guardar receta', 'error');
    }
}

function editRecipe(recipeId) {
    const recipe = recipes.find(r => r.id === recipeId);
    if (!recipe) return;

    document.getElementById('recipe-modal-title').textContent = 'Editar Receta';
    document.getElementById('recipe-id').value = recipe.id;
    document.getElementById('recipe-title').value = recipe.title;
    document.getElementById('recipe-description').value = recipe.description || '';
    document.getElementById('recipe-instructions').value = recipe.instructions;
    document.getElementById('recipe-prep-time').value = recipe.prep_time || '';
    document.getElementById('recipe-cook-time').value = recipe.cook_time || '';
    document.getElementById('recipe-servings').value = recipe.servings || '';
    document.getElementById('recipe-difficulty').value = recipe.difficulty || '';
    document.getElementById('recipe-author').value = recipe.author_id;
    document.getElementById('recipe-category').value = recipe.category_id;

    openModal('recipe-modal');
}

async function deleteRecipe(recipeId) {
    if (!confirm('¿Estás seguro de que quieres eliminar esta receta?')) return;

    try {
        await apiRequest(`/recipes/${recipeId}`, { method: 'DELETE' });
        showToast('Receta eliminada correctamente', 'success');
        await loadRecipes();
    } catch (error) {
        showToast('Error al eliminar receta', 'error');
    }
}

// Helper Functions
function getCategoryName(categoryId) {
    const category = categories.find(c => c.id === categoryId);
    return category ? category.name : 'Desconocida';
}

function getUserName(userId) {
    const user = users.find(u => u.id === userId);
    return user ? user.full_name : 'Desconocido';
}

function getDifficultyText(difficulty) {
    const difficulties = {
        'easy': 'Fácil',
        'medium': 'Medio',
        'hard': 'Difícil'
    };
    return difficulties[difficulty] || difficulty;
}

function populateCategoryFilters() {
    const recipeFilter = document.getElementById('recipe-category-filter');
    const recipeSelect = document.getElementById('recipe-category');

    // Clear existing options
    recipeFilter.innerHTML = '<option value="">Todas las categorías</option>';
    recipeSelect.innerHTML = '<option value="">Seleccionar categoría</option>';

    categories.forEach(category => {
        recipeFilter.innerHTML += `<option value="${category.id}">${category.name}</option>`;
        recipeSelect.innerHTML += `<option value="${category.id}">${category.name}</option>`;
    });
}

function populateIngredientSelects() {
    const recipeIngredients = document.getElementById('recipe-ingredients');
    const recipeAuthor = document.getElementById('recipe-author');

    // Populate ingredients
    recipeIngredients.innerHTML = '';
    ingredients.forEach(ingredient => {
        recipeIngredients.innerHTML += `<option value="${ingredient.id}">${ingredient.name}</option>`;
    });

    // Populate authors
    recipeAuthor.innerHTML = '<option value="">Seleccionar autor</option>';
    users.forEach(user => {
        recipeAuthor.innerHTML += `<option value="${user.id}">${user.full_name}</option>`;
    });
}

// Modal Functions
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
    
    // Reset form if it's a create modal
    const form = document.querySelector(`#${modalId} form`);
    if (form) {
        const idField = form.querySelector('input[type="hidden"]');
        if (!idField || !idField.value) {
            form.reset();
            // Reset modal title for create operations
            const modalTitle = document.getElementById(modalId.replace('-modal', '-modal-title'));
            if (modalTitle) {
                const entityName = modalId.replace('-modal', '').charAt(0).toUpperCase() + modalId.replace('-modal', '').slice(1);
                if (entityName === 'Category') {
                    modalTitle.textContent = 'Nueva Categoría';
                } else if (entityName === 'Ingredient') {
                    modalTitle.textContent = 'Nuevo Ingrediente';
                } else if (entityName === 'User') {
                    modalTitle.textContent = 'Nuevo Usuario';
                } else if (entityName === 'Recipe') {
                    modalTitle.textContent = 'Nueva Receta';
                }
            }
        }
    }
    
    // Populate selects for recipe modal
    if (modalId === 'recipe-modal') {
        populateIngredientSelects();
        populateCategoryFilters();
    }
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
    
    // Reset form
    const form = document.querySelector(`#${modalId} form`);
    if (form) {
        form.reset();
    }
}

// Loading Functions
function showLoading() {
    document.getElementById('loading').classList.add('active');
}

function hideLoading() {
    document.getElementById('loading').classList.remove('active');
}

// Toast Notifications
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'fas fa-check-circle' : 
                 type === 'error' ? 'fas fa-exclamation-circle' : 
                 'fas fa-info-circle';
    
    toast.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
    
    // Remove on click
    toast.addEventListener('click', () => {
        toast.remove();
    });
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(minutes) {
    if (!minutes) return 'N/A';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hours > 0) {
        return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Recipe Management System initialized');
    initializeApp();
});

// Error handling for uncaught errors
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    showToast('Ha ocurrido un error inesperado', 'error');
});

// Handle network errors
window.addEventListener('online', function() {
    showToast('Conexión restaurada', 'success');
});

window.addEventListener('offline', function() {
    showToast('Sin conexión a internet', 'warning');
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // ESC to close modals
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal.active');
        if (openModal) {
            closeModal(openModal.id);
        }
    }
    
    // Ctrl/Cmd + N for new items
    if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
        event.preventDefault();
        
        switch(currentSection) {
            case 'users':
                openModal('user-modal');
                break;
            case 'categories':
                openModal('category-modal');
                break;
            case 'ingredients':
                openModal('ingredient-modal');
                break;
            case 'recipes':
                openModal('recipe-modal');
                break;
        }
    }
});

// Auto-refresh data every 5 minutes
setInterval(async function() {
    try {
        await loadInitialData();
        console.log('Data refreshed automatically');
    } catch (error) {
        console.error('Auto-refresh failed:', error);
    }
}, 300000); // 5 minutes

// Export functions for global access (if needed)
window.recipeApp = {
    openModal,
    closeModal,
    editUser,
    deleteUser,
    editCategory,
    deleteCategory,
    editIngredient,
    deleteIngredient,
    editRecipe,
    deleteRecipe,
    showToast,
    navigateToSection
};