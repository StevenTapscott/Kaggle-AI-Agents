// State management
let allNotes = [];
let currentCategory = "all";
let searchQuery = "";
let currentSort = "newest";

// DOM Elements
const notesGrid = document.getElementById("notes-grid");
const loader = document.getElementById("loader");
const errorState = document.getElementById("error-state");
const errorMessage = document.getElementById("error-message");
const emptyState = document.getElementById("empty-state");
const refreshBtn = document.getElementById("refresh-btn");
const refreshIcon = document.getElementById("refresh-icon");
const lastUpdatedSpan = document.getElementById("last-updated");
const resultsCountSpan = document.getElementById("results-count");
const searchInput = document.getElementById("search-input");
const clearSearchBtn = document.getElementById("clear-search");
const sortSelect = document.getElementById("sort-select");
const categoryFiltersContainer = document.getElementById("category-filters");
const retryBtn = document.getElementById("retry-btn");
const clearFiltersBtn = document.getElementById("clear-filters-btn");

// Modal Elements
const tweetModal = document.getElementById("tweet-modal");
const closeModalBtn = document.getElementById("close-modal");
const cancelTweetBtn = document.getElementById("cancel-tweet-btn");
const postTweetBtn = document.getElementById("post-tweet-btn");
const tweetTextarea = document.getElementById("tweet-textarea");
const charCountSpan = document.getElementById("char-count");
const charWarning = document.getElementById("char-warning");
const modalBadge = document.getElementById("modal-badge");
const modalDate = document.getElementById("modal-date");
const modalOriginalText = document.getElementById("modal-original-text");

// Initialize Theme (Run immediately to avoid light-mode flash)
const savedTheme = localStorage.getItem("theme") || "dark";
if (savedTheme === "light") {
    document.body.classList.add("light-theme");
} else {
    document.body.classList.remove("light-theme");
}

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
    // Sync checkbox state and UI label on load
    const themeCheckbox = document.getElementById("theme-checkbox");
    if (themeCheckbox) {
        themeCheckbox.checked = (savedTheme === "dark");
        updateThemeUI(savedTheme);
    }
    
    fetchNotes(false);
    setupEventListeners();
});

// Event Listeners Setup
function setupEventListeners() {
    // Refresh button
    refreshBtn.addEventListener("click", () => fetchNotes(true));
    retryBtn.addEventListener("click", () => fetchNotes(true));
    
    // Search input
    searchInput.addEventListener("input", (e) => {
        searchQuery = e.target.value.trim().toLowerCase();
        clearSearchBtn.style.display = searchQuery ? "block" : "none";
        filterAndRenderNotes();
    });
    
    // Clear search
    clearSearchBtn.addEventListener("click", () => {
        searchInput.value = "";
        searchQuery = "";
        clearSearchBtn.style.display = "none";
        filterAndRenderNotes();
    });
    
    // Sorting select
    sortSelect.addEventListener("change", (e) => {
        currentSort = e.target.value;
        filterAndRenderNotes();
    });

    // Category filter buttons
    categoryFiltersContainer.addEventListener("click", (e) => {
        const btn = e.target.closest(".filter-btn");
        if (!btn) return;
        
        // Remove active class from all, add to clicked
        document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        
        currentCategory = btn.getAttribute("data-category");
        filterAndRenderNotes();
    });

    // Clear filters button (empty state action)
    clearFiltersBtn.addEventListener("click", () => {
        searchInput.value = "";
        searchQuery = "";
        clearSearchBtn.style.display = "none";
        currentCategory = "all";
        
        document.querySelectorAll(".filter-btn").forEach(b => {
            if (b.getAttribute("data-category") === "all") {
                b.classList.add("active");
            } else {
                b.classList.remove("active");
            }
        });
        
        filterAndRenderNotes();
    });

    // Modal Close actions
    closeModalBtn.addEventListener("click", closeTweetModal);
    cancelTweetBtn.addEventListener("click", closeTweetModal);
    tweetModal.addEventListener("click", (e) => {
        if (e.target === tweetModal) closeTweetModal();
    });

    // Textarea character counter
    tweetTextarea.addEventListener("input", () => {
        const length = tweetTextarea.value.length;
        charCountSpan.textContent = `${length} / 280`;
        
        if (length > 280) {
            charCountSpan.className = "char-count danger";
            charWarning.style.display = "flex";
            postTweetBtn.disabled = true;
            postTweetBtn.style.opacity = "0.5";
            postTweetBtn.style.pointerEvents = "none";
        } else {
            charWarning.style.display = "none";
            postTweetBtn.disabled = false;
            postTweetBtn.style.opacity = "1";
            postTweetBtn.style.pointerEvents = "auto";
            
            if (length > 250) {
                charCountSpan.className = "char-count warning";
            } else {
                charCountSpan.className = "char-count";
            }
        }
    });

    // Keyboard ESC to close modal
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && tweetModal.style.display === "flex") {
            closeTweetModal();
        }
    });

    // Export to CSV button
    const exportCsvBtn = document.getElementById("export-csv-btn");
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener("click", exportFilteredToCSV);
    }

    // Theme toggle checkbox listener
    const themeCheckbox = document.getElementById("theme-checkbox");
    if (themeCheckbox) {
        themeCheckbox.addEventListener("change", (e) => {
            if (e.target.checked) {
                document.body.classList.remove("light-theme");
                localStorage.setItem("theme", "dark");
                updateThemeUI("dark");
            } else {
                document.body.classList.add("light-theme");
                localStorage.setItem("theme", "light");
                updateThemeUI("light");
            }
        });
    }
}

// Fetch Notes from API
async function fetchNotes(forceRefresh = false) {
    showLoader();
    try {
        const url = `/api/notes${forceRefresh ? '?refresh=true' : ''}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.success) {
            allNotes = data.notes;
            
            // Update UI components
            lastUpdatedSpan.textContent = data.last_fetched || "Just now";
            if (data.cached) {
                lastUpdatedSpan.innerHTML += " <span class='cached-lbl' title='Served from cache'>(cached)</span>";
            }
            
            filterAndRenderNotes();
        } else {
            throw new Error(data.error || "Unknown error occurred");
        }
    } catch (err) {
        console.error("Fetch notes failed:", err);
        showError(err.message);
    }
}

// Filter and Render Notes
function filterAndRenderNotes() {
    hideStates();
    const filtered = getFilteredNotes();
    
    // Update count badge
    resultsCountSpan.textContent = `${filtered.length} update${filtered.length === 1 ? '' : 's'}`;
    
    // Render
    if (filtered.length === 0) {
        showEmpty();
    } else {
        renderGrid(filtered);
    }
}

// Get filtered and sorted list of notes
function getFilteredNotes() {
    let filtered = allNotes;
    
    // 1. Filter by category
    if (currentCategory !== "all") {
        filtered = filtered.filter(note => note.type === currentCategory);
    }
    
    // 2. Filter by search query
    if (searchQuery) {
        filtered = filtered.filter(note => {
            const plainText = getPlainTextFromHtml(note.html).toLowerCase();
            return (
                note.type.toLowerCase().includes(searchQuery) ||
                note.date.toLowerCase().includes(searchQuery) ||
                plainText.includes(searchQuery)
            );
        });
    }
    
    // 3. Sort notes
    filtered.sort((a, b) => {
        const timeA = new Date(a.timestamp);
        const timeB = new Date(b.timestamp);
        
        if (currentSort === "newest") {
            return timeB - timeA;
        } else {
            return timeA - timeB;
        }
    });
    
    return filtered;
}

// Render the grid of cards
function renderGrid(notes) {
    notesGrid.innerHTML = "";
    notes.forEach(note => {
        const card = document.createElement("div");
        card.className = `note-card ${note.type.toLowerCase()}`;
        card.setAttribute("data-id", note.id);
        
        card.innerHTML = `
            <div class="card-header">
                <span class="card-date">${note.date}</span>
                <span class="card-badge">${note.type}</span>
            </div>
            <div class="card-body">
                ${note.html}
            </div>
            <div class="card-actions" style="display: flex; gap: 10px; justify-content: flex-end;">
                <button class="copy-action-btn" onclick="copyToClipboard('${note.id}', this)">
                    <i class="fa-regular fa-copy"></i> Copy
                </button>
                <button class="tweet-action-btn" onclick="initiateTweet('${note.id}')">
                    <i class="fa-brands fa-x-twitter"></i> Tweet
                </button>
            </div>
        `;
        notesGrid.appendChild(card);
    });
}

// Open Tweet Modal
function initiateTweet(noteId) {
    const note = allNotes.find(n => n.id === noteId);
    if (!note) return;
    
    const plainText = getPlainTextFromHtml(note.html);
    
    // Prefill modal fields
    modalBadge.textContent = note.type;
    modalBadge.className = `preview-badge ${note.type.toLowerCase()}`;
    modalDate.textContent = note.date;
    modalOriginalText.innerHTML = note.html;
    
    // Generate prefilled tweet under 280 chars
    // Format: "BigQuery Update [June 15, 2026] - Feature: Description... #BigQuery #GoogleCloud"
    const prefix = `BigQuery Update (${note.date}) | ${note.type}:\n`;
    const suffix = `\n\n#BigQuery #GoogleCloud`;
    
    // Calculate space for description
    const maxDescLen = 280 - prefix.length - suffix.length - 3; // -3 for "..."
    let body = plainText;
    
    if (body.length > maxDescLen) {
        body = body.substring(0, maxDescLen).trim() + "...";
    }
    
    const prefilledText = prefix + body + suffix;
    tweetTextarea.value = prefilledText;
    
    // Trigger count update
    tweetTextarea.dispatchEvent(new Event("input"));
    
    // Show Modal
    tweetModal.style.display = "flex";
    setTimeout(() => {
        tweetModal.classList.add("active");
    }, 10);
    
    // Handle Tweet posting action
    postTweetBtn.onclick = () => {
        const tweetText = tweetTextarea.value;
        const twitterIntentUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(tweetText)}`;
        window.open(twitterIntentUrl, "_blank");
        closeTweetModal();
    };
}

// Close Tweet Modal
function closeTweetModal() {
    tweetModal.classList.remove("active");
    setTimeout(() => {
        tweetModal.style.display = "none";
    }, 300);
}

// Helpers
function getPlainTextFromHtml(html) {
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = html;
    
    // Extract text and clean up whitespace
    let text = tempDiv.textContent || tempDiv.innerText || "";
    // Remove multiple spaces/newlines
    text = text.replace(/\s+/g, ' ').trim();
    return text;
}

// UI State Switchers
function showLoader() {
    loader.style.display = "flex";
    notesGrid.style.display = "none";
    errorState.style.display = "none";
    emptyState.style.display = "none";
    
    refreshIcon.classList.add("spinning");
    refreshBtn.disabled = true;
}

function filterRenderingState() {
    loader.style.display = "none";
    notesGrid.style.display = "grid";
    errorState.style.display = "none";
    emptyState.style.display = "none";
}

function hideStates() {
    loader.style.display = "none";
    notesGrid.style.display = "grid";
    errorState.style.display = "none";
    emptyState.style.display = "none";
    
    refreshIcon.classList.remove("spinning");
    refreshBtn.disabled = false;
}

function showError(msg) {
    loader.style.display = "none";
    notesGrid.style.display = "none";
    errorState.style.display = "flex";
    emptyState.style.display = "none";
    errorMessage.textContent = msg || "There was an error loading updates. Please check your network connection.";
    
    refreshIcon.classList.remove("spinning");
    refreshBtn.disabled = false;
}

function showEmpty() {
    loader.style.display = "none";
    notesGrid.style.display = "none";
    errorState.style.display = "none";
    emptyState.style.display = "flex";
    
    refreshIcon.classList.remove("spinning");
    refreshBtn.disabled = false;
}

// Copy Note Plain Text to Clipboard
function copyToClipboard(noteId, buttonElement) {
    const note = allNotes.find(n => n.id === noteId);
    if (!note) return;
    
    const plainText = `BigQuery Update (${note.date}) | ${note.type}:\n${getPlainTextFromHtml(note.html)}`;
    
    navigator.clipboard.writeText(plainText).then(() => {
        const originalHTML = buttonElement.innerHTML;
        buttonElement.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
        buttonElement.classList.add("copied");
        setTimeout(() => {
            buttonElement.innerHTML = originalHTML;
            buttonElement.classList.remove("copied");
        }, 2000);
    }).catch(err => {
        console.error("Failed to copy text: ", err);
    });
}

// Export Filtered Release Notes to CSV
function exportFilteredToCSV() {
    const filtered = getFilteredNotes();
    if (filtered.length === 0) {
        alert("No release notes found to export.");
        return;
    }
    
    const csvRows = [];
    
    // CSV Header row
    csvRows.push(['Date', 'Category', 'Description'].map(h => `"${h.replace(/"/g, '""')}"`).join(','));
    
    // CSV Data rows
    filtered.forEach(note => {
        const plainText = getPlainTextFromHtml(note.html);
        const row = [
            note.date,
            note.type,
            plainText
        ];
        csvRows.push(row.map(val => `"${val.replace(/"/g, '""')}"`).join(','));
    });
    
    const csvString = csvRows.join('\r\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", `bigquery_release_notes_${new Date().toISOString().slice(0, 10)}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Bind to window to allow inline onclick handlers in dynamically generated HTML
window.copyToClipboard = copyToClipboard;
window.exportFilteredToCSV = exportFilteredToCSV;

// Update Theme Toggle UI Text and Icon
function updateThemeUI(theme) {
    const themeIndicatorIcon = document.getElementById("theme-indicator-icon");
    if (!themeIndicatorIcon) return;
    
    const themeLabelText = themeIndicatorIcon.parentElement;
    
    if (theme === "light") {
        if (themeLabelText) {
            themeLabelText.innerHTML = `<i class="fa-solid fa-sun" id="theme-indicator-icon" style="color: var(--accent-cyan)"></i> Light Mode`;
        }
    } else {
        if (themeLabelText) {
            themeLabelText.innerHTML = `<i class="fa-solid fa-moon" id="theme-indicator-icon"></i> Dark Mode`;
        }
    }
}

window.updateThemeUI = updateThemeUI;
