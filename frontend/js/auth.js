// Authentication & Session Management

const AUTH_TOKEN_KEY = "screening_platform_jwt";
const USER_DATA_KEY = "screening_platform_user";

function getToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}

function setToken(token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
}

function getUser() {
    try {
        return JSON.parse(localStorage.getItem(USER_DATA_KEY));
    } catch {
        return null;
    }
}

function setUser(user) {
    localStorage.setItem(USER_DATA_KEY, JSON.stringify(user));
}

function logout() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(USER_DATA_KEY);
    window.location.href = "/login";
}

function isAuthenticated() {
    return !!getToken();
}

/**
 * Fetch wrapper that attaches Bearer JWT authorization header
 */
async function authFetch(url, options = {}) {
    const token = getToken();
    const headers = options.headers || {};

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    // Set JSON content-type if body is JSON object string
    if (options.body && typeof options.body === "string" && !headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }

    options.headers = headers;

    const response = await fetch(url, options);

    if (response.status === 401) {
        // If unauthorized and not on login page, redirect
        if (!window.location.pathname.includes("login")) {
            logout();
        }
    }

    return response;
}

/**
 * Update UI Navbar based on authentication status
 */
function updateNavbarAuth() {
    const navAuthContainer = document.getElementById("navAuth");
    if (!navAuthContainer) return;

    const user = getUser();
    if (user && isAuthenticated()) {
        navAuthContainer.innerHTML = `
            <span style="font-size: 0.9rem; color: var(--text-secondary);">👤 ${escapeHtml(user.name)}</span>
            <button onclick="logout()" class="btn btn-secondary btn-sm">Logout</button>
        `;
    } else {
        navAuthContainer.innerHTML = `
            <a href="/login" class="btn btn-primary btn-sm">Login / Register</a>
        `;
    }
}

/**
 * Utility to escape HTML to prevent XSS in rendering
 */
function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

document.addEventListener("DOMContentLoaded", () => {
    updateNavbarAuth();
});
