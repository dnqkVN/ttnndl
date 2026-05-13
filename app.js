import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore, collection, addDoc, onSnapshot, deleteDoc, doc, query, orderBy, updateDoc } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// --- Cấu hình Firebase (Giữ nguyên) ---
const firebaseConfig = {
  apiKey: "AIzaSyBPS1LHGU4BctFPO8vzje9LY3dln2i3FQw",
  authDomain: "tunut-22b3c.firebaseapp.com",
  projectId: "tunut-22b3c",
  storageBucket: "tunut-22b3c.firebasestorage.app",
  messagingSenderId: "311389599595",
  appId: "1:311389599595:web:fc7e5ad5e5c7f6fc6ffe2e"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const provider = new GoogleAuthProvider();

const ADMIN_EMAILS = ["khangdoannq@gmail.com", "admin@nexus.com"];

const DOM = {
    loginSection: document.getElementById('login-section'),
    dashboardSection: document.getElementById('dashboard-section'),
    loadingOverlay: document.getElementById('loading-overlay'),
    btnLogin: document.getElementById('btn-google-login'),
    btnLogout: document.getElementById('btn-logout'),
    userName: document.getElementById('user-name'),
    userEmail: document.getElementById('user-email'),
    userAvatar: document.getElementById('user-avatar'),
    modal: document.getElementById('create-modal'),
    btnHeaderCreate: document.getElementById('btn-create-header'),
    btnCloseModal: document.getElementById('btn-close-modal'),
    btnSaveKey: document.getElementById('btn-save-key'),
    keyPreview: document.getElementById('key-preview'),
    keyDuration: document.getElementById('key-duration'),
    keysTbody: document.getElementById('keys-tbody'), // Vẫn giữ ID để không lỗi logic
    searchInput: document.getElementById('search-input'),
    statTotal: document.getElementById('stat-total'),
    statActive: document.getElementById('stat-active'),
    statExpired: document.getElementById('stat-expired'),
    toastContainer: document.getElementById('toast-container'),
    tabItems: document.querySelectorAll('.tab-item')
};

let allKeysData = [];
let currentFilter = 'all';

// --- Hiệu ứng & Toast (Giữ nguyên) ---
function initParticles() { /* ... code particles của cậu ... */ }
function showToast(msg, type) { /* ... code toast của cậu ... */ }

// --- Logic Auth (Giữ nguyên) ---
onAuthStateChanged(auth, (user) => {
    if (user && ADMIN_EMAILS.includes(user.email)) {
        DOM.userName.textContent = user.displayName;
        DOM.userEmail.textContent = user.email;
        DOM.userAvatar.src = user.photoURL;
        DOM.loginSection.classList.add('hidden');
        DOM.dashboardSection.classList.remove('hidden');
        loadKeys();
    } else {
        DOM.loginSection.classList.remove('hidden');
        DOM.dashboardSection.classList.add('hidden');
    }
});

DOM.btnLogin.onclick = () => signInWithPopup(auth, provider);
DOM.btnLogout.onclick = () => signOut(auth);

// --- TAB FILTER LOGIC ---
DOM.tabItems.forEach(tab => {
    tab.onclick = () => {
        DOM.tabItems.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentFilter = tab.dataset.filter;
        renderData();
    };
});

function loadKeys() {
    const q = query(collection(db, "keys"), orderBy("createdAt", "desc"));
    onSnapshot(q, (snapshot) => {
        allKeysData = [];
        snapshot.forEach(docSnap => {
            allKeysData.push({ id: docSnap.id, ...docSnap.data() });
        });
        renderData();
    });
}

function renderData() {
    const now = Date.now();
    let filtered = allKeysData;

    // Lọc theo Search
    const searchVal = DOM.searchInput.value.toLowerCase();
    filtered = filtered.filter(k => k.keyString.toLowerCase().includes(searchVal));

    // Lọc theo Tab
    if (currentFilter === 'active') {
        filtered = filtered.filter(k => k.isActive && (k.expiresAt === 'never' || k.expiresAt > now));
    } else if (currentFilter === 'expired') {
        filtered = filtered.filter(k => k.expiresAt !== 'never' && now > k.expiresAt);
    } else if (currentFilter === 'banned') {
        filtered = filtered.filter(k => !k.isActive);
    }

    // Cập nhật Stats
    DOM.statTotal.textContent = allKeysData.length;
    DOM.statActive.textContent = allKeysData.filter(k => k.isActive).length;
    DOM.statExpired.textContent = allKeysData.filter(k => k.expiresAt !== 'never' && now > k.expiresAt).length;

    renderCards(filtered);
}

// --- HÀM RENDER CARD (THAY CHO TABLE) ---
function renderCards(data) {
    DOM.keysTbody.innerHTML = '';
    data.forEach(item => {
        const isExpired = item.expiresAt !== 'never' && Date.now() > item.expiresAt;
        const statusText = isExpired ? 'EXPIRED' : (item.isActive ? 'ACTIVE' : 'BANNED');
        const statusClass = item.isActive && !isExpired ? 'status-active' : 'status-expired';
        
        const card = document.createElement('div');
        card.className = 'key-card';
        card.innerHTML = `
            <div class="card-head">
                <div class="key-identity">
                    <h4>${item.keyString}</h4>
                    <span>ID: ${item.id.substring(0, 8)}...</span>
                </div>
                <label class="switch">
                    <input type="checkbox" class="toggle-active" data-id="${item.id}" ${item.isActive ? 'checked' : ''}>
                    <span class="slider"></span>
                </label>
            </div>
            <div class="card-body-info">
                <div class="info-row"><i class="fa-solid fa-user"></i> By: ${item.createdBy}</div>
                <div class="info-row"><i class="fa-solid fa-clock"></i> Exp: ${item.expiresAt === 'never' ? 'Lifetime' : new Date(item.expiresAt).toLocaleDateString()}</div>
            </div>
            <div class="card-foot">
                <span class="status-badge ${statusClass}">${statusText}</span>
                <div class="card-actions">
                    <button class="action-btn btn-copy" data-key="${item.keyString}"><i class="fa-regular fa-copy"></i></button>
                    <button class="action-btn btn-delete" data-id="${item.id}"><i class="fa-solid fa-trash-can"></i></button>
                </div>
            </div>
        `;
        DOM.keysTbody.appendChild(card);
    });

    // Gán sự kiện Toggle/Copy/Delete
    attachEvents();
}

function attachEvents() {
    // Copy
    DOM.keysTbody.querySelectorAll('.btn-copy').forEach(btn => {
        btn.onclick = () => {
            navigator.clipboard.writeText(btn.dataset.key);
            showToast("Copied to clipboard!", "success");
        };
    });

    // Delete
    DOM.keysTbody.querySelectorAll('.btn-delete').forEach(btn => {
        btn.onclick = async () => {
            if(confirm("Xóa key này?")) await deleteDoc(doc(db, "keys", btn.dataset.id));
        };
    });

    // Toggle Active Status
    DOM.keysTbody.querySelectorAll('.toggle-active').forEach(sw => {
        sw.onchange = async () => {
            await updateDoc(doc(db, "keys", sw.dataset.id), { isActive: sw.checked });
            showToast("Status updated!", "info");
        };
    });
}

// Search realtime (Giữ nguyên logic của cậu)
DOM.searchInput.oninput = () => renderData();

// Modal logic (Giữ nguyên)
DOM.btnHeaderCreate.onclick = () => {
    DOM.keyPreview.value = "VIP-" + Math.random().toString(36).substring(2, 10).toUpperCase();
    DOM.modal.classList.remove('hidden');
};
DOM.btnCloseModal.onclick = () => DOM.modal.classList.add('hidden');
DOM.btnSaveKey.onclick = async () => {
    const duration = parseInt(DOM.keyDuration.value);
    const expiresAt = duration === 9999 ? 'never' : Date.now() + (duration * 24 * 60 * 60 * 1000);
    await addDoc(collection(db, "keys"), {
        keyString: DOM.keyPreview.value,
        createdBy: auth.currentUser.email,
        createdAt: Date.now(),
        expiresAt: expiresAt,
        isActive: true
    });
    DOM.modal.classList.add('hidden');
};
