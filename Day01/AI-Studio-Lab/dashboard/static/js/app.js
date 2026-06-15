// Global application state
let allDocuments = [];
let filteredDocuments = [];

// DOM Elements
const tableBody = document.getElementById('table-body');
const searchInput = document.getElementById('search-input');
const tagFilter = document.getElementById('tag-filter');
const resetBtn = document.getElementById('reset-btn');
const sourceBadge = document.getElementById('source-badge');
const emptyState = document.getElementById('empty-state');
const responsiveTable = document.querySelector('.responsive-table-wrapper');

// Stats Counters
const valTotalDocs = document.getElementById('val-total-docs');
const valTotalWords = document.getElementById('val-total-words');
const valUniqueTags = document.getElementById('val-unique-tags');

// Format date to local readable format
function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
    } catch (e) {
        return dateString;
    }
}

// Format number (e.g. 1420 -> 1,420; 5420 -> 5.4K)
function formatNumber(num) {
    if (num >= 1000) {
        return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
    }
    return num.toString();
}

// Fetch documents from Flask API
async function loadDocuments() {
    try {
        const response = await fetch('/api/documents');
        const result = await response.json();
        
        if (result.status === 'success') {
            allDocuments = result.data;
            filteredDocuments = [...allDocuments];
            
            // Set data source badge
            if (result.source === 'bigquery') {
                sourceBadge.textContent = 'BigQuery Connected';
                sourceBadge.className = 'badge badge-cloud';
            } else {
                sourceBadge.textContent = 'Simulation Mode';
                sourceBadge.className = 'badge badge-mock';
            }
            
            initializeTagFilter();
            applyFilters();
        } else {
            renderError('Failed to retrieve documents from API.');
        }
    } catch (error) {
        console.error('Error fetching documents:', error);
        renderError('Failed to communicate with dashboard backend.');
    }
}

// Extract unique tags and populate the select dropdown
function initializeTagFilter() {
    const tagsSet = new Set();
    allDocuments.forEach(doc => {
        if (doc.tags && Array.isArray(doc.tags)) {
            doc.tags.forEach(tag => tagsSet.add(tag));
        }
    });
    
    // Clear previous options except default
    tagFilter.innerHTML = '<option value="">All Tags</option>';
    
    // Sort and append tags
    Array.from(tagsSet).sort().forEach(tag => {
        const option = document.createElement('option');
        option.value = tag;
        option.textContent = tag;
        tagFilter.appendChild(option);
    });
}

// Apply Search & Tag filters
function applyFilters() {
    const searchText = searchInput.value.toLowerCase().trim();
    const selectedTag = tagFilter.value;
    
    filteredDocuments = allDocuments.filter(doc => {
        const matchesSearch = doc.filename.toLowerCase().includes(searchText);
        const matchesTag = !selectedTag || (doc.tags && doc.tags.includes(selectedTag));
        return matchesSearch && matchesTag;
    });
    
    renderTable();
    updateKPIs();
}

// Render the documents into the HTML table
function renderTable() {
    tableBody.innerHTML = '';
    
    if (filteredDocuments.length === 0) {
        responsiveTable.classList.add('hidden');
        emptyState.classList.remove('hidden');
        return;
    }
    
    responsiveTable.classList.remove('hidden');
    emptyState.classList.add('hidden');
    
    filteredDocuments.forEach(doc => {
        const tr = document.createElement('tr');
        
        // Filename
        const tdFile = document.createElement('td');
        tdFile.className = 'filename-cell';
        tdFile.textContent = doc.filename;
        tr.appendChild(tdFile);
        
        // Date
        const tdDate = document.createElement('td');
        tdDate.className = 'date-cell';
        tdDate.textContent = formatDate(doc.date);
        tr.appendChild(tdDate);
        
        // Tags
        const tdTags = document.createElement('td');
        tdTags.className = 'tags-cell';
        if (doc.tags && doc.tags.length > 0) {
            doc.tags.forEach(tag => {
                const span = document.createElement('span');
                span.className = 'tag-pill';
                span.textContent = tag;
                // Click tag to filter table by it
                span.addEventListener('click', () => {
                    tagFilter.value = tag;
                    applyFilters();
                });
                tdTags.appendChild(span);
            });
        } else {
            tdTags.innerHTML = '<span style="color: var(--text-secondary); font-size: 0.85rem;">None</span>';
        }
        tr.appendChild(tdTags);
        
        // Word Count
        const tdWord = document.createElement('td');
        tdWord.className = 'word-count-cell text-right';
        tdWord.textContent = doc.word_count.toLocaleString();
        tr.appendChild(tdWord);
        
        tableBody.appendChild(tr);
    });
}

// Compute statistics cards based on current filtered results
function updateKPIs() {
    valTotalDocs.textContent = filteredDocuments.length;
    
    const totalWords = filteredDocuments.reduce((sum, doc) => sum + doc.word_count, 0);
    valTotalWords.textContent = formatNumber(totalWords);
    
    const uniqueTagsSet = new Set();
    filteredDocuments.forEach(doc => {
        if (doc.tags) doc.tags.forEach(tag => uniqueTagsSet.add(tag));
    });
    valUniqueTags.textContent = uniqueTagsSet.size;
}

// Render error row in the table
function renderError(message) {
    tableBody.innerHTML = `
        <tr>
            <td colspan="4" style="text-align: center; color: var(--color-warning); padding: 3rem 0;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚠️</div>
                <span>${message}</span>
            </td>
        </tr>
    `;
    sourceBadge.textContent = 'Error';
    sourceBadge.className = 'badge badge-mock';
    responsiveTable.classList.remove('hidden');
    emptyState.classList.add('hidden');
}

// Event Listeners
searchInput.addEventListener('input', applyFilters);
tagFilter.addEventListener('change', applyFilters);

resetBtn.addEventListener('click', () => {
    searchInput.value = '';
    tagFilter.value = '';
    applyFilters();
});

// Load resources on load
window.addEventListener('DOMContentLoaded', loadDocuments);
