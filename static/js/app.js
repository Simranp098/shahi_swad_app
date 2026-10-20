const API_BASE_URL = '/api';
let cart = [];
let allCategories = [];

const urlParams = new URLSearchParams(window.location.search);
const tableNumber = urlParams.get('table') || '1';

document.addEventListener('DOMContentLoaded', () => {
    fetchMenu();
    initSearchOverlay();
});

async function fetchMenu() {
    try {
        const response = await fetch(`${API_BASE_URL}/menu/`);
        allCategories = await response.json();
        renderCategoryFilters(allCategories);
        renderMenuGrid(allCategories);
    } catch (error) {
        console.error('Error loading menu:', error);
    }
}

/* ============================================================
   SEARCH OVERLAY LOGIC
   ============================================================ */
function initSearchOverlay() {
    const navSearchBtn = document.getElementById('navSearchBtn');
    const searchOv = document.getElementById('searchOv');
    const searchClose = document.getElementById('searchClose');
    const searchInput = document.getElementById('searchInput');

    if (navSearchBtn && searchOv) {
        navSearchBtn.addEventListener('click', (e) => {
            e.preventDefault();
            searchOv.style.display = 'flex';
            if (searchInput) {
                searchInput.focus();
                searchInput.value = '';
            }
            renderSearchResults('');
        });
    }

    if (searchClose && searchOv) {
        searchClose.addEventListener('click', () => {
            searchOv.style.display = 'none';
        });
    }

    // Close modal on background click
    if (searchOv) {
        searchOv.addEventListener('click', (e) => {
            if (e.target === searchOv) {
                searchOv.style.display = 'none';
            }
        });
    }

    // Live search input handler
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim().toLowerCase();
            renderSearchResults(query);
        });
    }
}

function renderSearchResults(query) {
    const resultsContainer = document.getElementById('searchResults');
    if (!resultsContainer) return;

    if (!query) {
        resultsContainer.innerHTML = '<div class="col-12 text-center text-white-50 py-3">Type above to search dishes...</div>';
        return;
    }

    let matches = [];
    allCategories.forEach(category => {
        category.items.forEach(item => {
            if (item.name.toLowerCase().includes(query) || (item.description && item.description.toLowerCase().includes(query))) {
                matches.push({ ...item, categoryName: category.name });
            }
        });
    });

    if (matches.length === 0) {
        resultsContainer.innerHTML = `<div class="col-12 text-center text-white-50 py-3">No dishes found matching "${query}".</div>`;
        return;
    }

    let html = '';
    matches.forEach(item => {
        const imageUrl = item.image ? item.image : '/static/img/menu/1.jpg';
        html += `
        <div class="col-12 col-md-6">
            <div class="p-2 bg-dark rounded border border-secondary d-flex align-items-center justify-content-between gap-2">
                <img src="${imageUrl}" class="rounded" style="width: 60px; height: 60px; object-fit: cover;" alt="${item.name}"/>
                <div class="flex-grow-1 text-white">
                    <div class="fw-bold text-light small">${item.name}</div>
                    <div class="text-danger small font-weight-bold">₹${parseFloat(item.price).toFixed(2)}</div>
                </div>
                <button class="btn btn-danger btn-sm rounded-circle px-2 py-1" onclick="addToCart(${item.id}, '${item.name}')" title="Add Item">
                    <i class="fas fa-plus"></i>
                </button>
            </div>
        </div>`;
    });

    resultsContainer.innerHTML = html;
}

/* ============================================================
   CATEGORY FILTERS & MENU GRID LOGIC
   ============================================================ */
function renderCategoryFilters(categories) {
    const filterContainer = document.getElementById('categoryFilters');
    if (!filterContainer) return;

    if (!categories || categories.length === 0) {
        filterContainer.innerHTML = '';
        return;
    }

    let html = `<button class="filtbtn active btn btn-outline-danger btn-sm rounded-pill px-3 py-2 fw-semibold" onclick="filterCategory('all', this)">All</button>`;
    
    categories.forEach(cat => {
        const catSlug = cat.name.toLowerCase().replace(/\s+/g, '-');
        html += `<button class="filtbtn btn btn-outline-danger btn-sm rounded-pill px-3 py-2 fw-semibold" onclick="filterCategory('${catSlug}', this)">${cat.name}</button>`;
    });

    filterContainer.innerHTML = html;
}

function filterCategory(catSlug, btnElement) {
    document.querySelectorAll('.filtbtn').forEach(btn => {
        btn.classList.remove('active', 'btn-danger', 'text-white');
        btn.classList.add('btn-outline-danger');
    });

    if (btnElement) {
        btnElement.classList.add('active', 'btn-danger', 'text-white');
        btnElement.classList.remove('btn-outline-danger');
    }

    const items = document.querySelectorAll('.mwrap');
    items.forEach(item => {
        const itemCat = item.getAttribute('data-c');
        if (catSlug === 'all' || itemCat === catSlug) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

function renderMenuGrid(categories) {
    const grid = document.getElementById('mgrid');
    if (!grid) return;

    if (!categories || categories.length === 0) {
        grid.innerHTML = '<div class="col-12 text-center text-muted py-5">No menu items available.</div>';
        return;
    }

    let html = '';
    categories.forEach(category => {
        const catSlug = category.name.toLowerCase().replace(/\s+/g, '-');
        category.items.forEach(item => {
            const imageUrl = item.image ? item.image : '/static/img/menu/1.jpg';
            html += `
            <div class="col-sm-6 col-lg-4 mwrap" data-c="${catSlug}">
                <div class="mcard p-3 shadow-sm rounded border bg-white h-100">
                    <div class="mimg mb-2 position-relative overflow-hidden rounded">
                        <img src="${imageUrl}" class="img-fluid rounded w-100" alt="${item.name}" style="height:200px; object-fit:cover;"/>
                    </div>
                    <div class="mbody d-flex flex-column justify-content-between">
                        <div>
                            <div class="mcat text-uppercase text-danger fw-bold small">${category.name}</div>
                            <div class="mtit h5 font-weight-bold text-dark mt-1">${item.name}</div>
                            <div class="mdesc text-muted small mb-3">${item.description || 'Deliciously prepared dish.'}</div>
                        </div>
                        <div class="mfoot d-flex justify-content-between align-items-center mt-3 pt-2 border-top">
                            <div class="mprice h5 font-weight-bold mb-0 text-dark">₹${parseFloat(item.price).toFixed(2)}</div>
                            <button class="btn btn-danger btn-sm rounded-circle px-3 py-2" onclick="addToCart(${item.id}, '${item.name}')" title="Add Item">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>`;
        });
    });

    grid.innerHTML = html;
}

/* ============================================================
   ORDER SUBMISSION
   ============================================================ */
function addToCart(itemId, name) {
    const existing = cart.find(i => i.menu_item === itemId);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ menu_item: itemId, name: name, quantity: 1 });
    }
    
    if (confirm(`Added "${name}" to Table ${tableNumber} order.\n\nWould you like to submit this order now?`)) {
        submitOrder();
    }
}

async function submitOrder() {
    if (cart.length === 0) return;

    const orderPayload = {
        table_number: tableNumber.toString(),
        items: cart.map(item => ({
            menu_item: item.menu_item,
            quantity: item.quantity
        }))
    };

    try {
        const response = await fetch(`${API_BASE_URL}/orders/`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(orderPayload)
        });

        if (response.ok) {
            const data = await response.json();
            cart = [];
            // Automatically redirect customer to Live Tracking Page
            window.location.href = `/api/orders/${data.id}/track/`;
        } else {
            const errorData = await response.json();
            alert(`Order submission error:\n${JSON.stringify(errorData, null, 2)}`);
        }
    } catch (error) {
        console.error('Error submitting order:', error);
        alert('Network or server error submitting order.');
    }
}