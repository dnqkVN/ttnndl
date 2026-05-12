import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore, collection, addDoc, onSnapshot, deleteDoc, doc, query, orderBy } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// --- Cấu hình Firebase mới của bạn ---
const firebaseConfig = {
  apiKey: "AIzaSyBPS1LHGU4BctFPO8vzje9LY3dln2i3FQw",
  authDomain: "tunut-22b3c.firebaseapp.com",
  projectId: "tunut-22b3c",
  storageBucket: "tunut-22b3c.firebasestorage.app",
  messagingSenderId: "311389599595",
  appId: "1:311389599595:web:fc7e5ad5e5c7f6fc6ffe2e"
};

// Khởi tạo Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const provider = new GoogleAuthProvider();

// --- DANH SÁCH ADMIN (Thay email của bạn vào đây) ---
const ADMIN_EMAILS = [
    "khangdoannq@gmail.com", // Hãy thay email Google của bạn vào đây để có quyền truy cập
    "admin@nexus.com"
];

// --- Quản lý các thành phần giao diện (DOM) ---
const DOM = {
    loginSection: document.getElementById('login-section'),
    dashboardSection: document.getElementById('dashboard-section'),
    loadingOverlay: document.getElementById('loading-overlay'),
    btnLogin: document.getElementById('btn-google-login'),
    btnLogout: document.getElementById('btn-logout'),
    loginError: document.getElementById('login-error'),
    userName: document.getElementById('user-name'),
    userEmail: document.getElementById('user-email'),
    userAvatar: document.getElementById('user-avatar'),
    modal: document.getElementById('create-modal'),
    btnNavCreate: document.getElementById('btn-nav-create'),
    btnHeaderCreate: document.getElementById('btn-create-header'),
    btnCloseModal: document.getElementById('btn-close-modal'),
    btnGenerateRandom: document.getElementById('btn-generate-random'),
    btnSaveKey: document.getElementById('btn-save-key'),
    keyPreview: document.getElementById('key-preview'),
    keyDuration: document.getElementById('key-duration'),
    keysTbody: document.getElementById('keys-tbody'),
    searchInput: document.getElementById('search-input'),
    statTotal: document.getElementById('stat-total'),
    statActive: document.getElementById('stat-active'),
    statExpired: document.getElementById('stat-expired'),
    toastContainer: document.getElementById('toast-container')
};

let keysData = [];

// --- Hiệu ứng Particle Background ---
function initParticles() {
    const canvas = document.getElementById('particles-bg');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    let particlesArray = [];
    const numberOfParticles = 80;

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 0.5;
            this.speedX = Math.random() * 1 - 0.5;
            this.speedY = Math.random() * 1 - 0.5;
            this.color = `rgba(0, 242, 254, ${Math.random() * 0.3})`;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            if (this.size > 0.2) this.size -= 0.005;
            if (this.x < 0 || this.x > canvas.width) this.speedX = -this.speedX;
            if (this.y < 0 || this.y > canvas.height) this.speedY = -this.speedY;
        }
        draw() {
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    for (let i = 0; i < numberOfParticles; i++) particlesArray.push(new Particle());

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (let i = 0; i < particlesArray.length; i++) {
            particlesArray[i].update();
            particlesArray[i].draw();
        }
        requestAnimationFrame(animate);
    }
    animate();
}

// --- Thông báo Toast ---
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    let icon = type === 'success' ? 'fa-circle-check' : (type === 'error' ? 'fa-circle-xmark' : 'fa-circle-info');
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    DOM.toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 3400);
}

function showLoading(show) {
    DOM.loadingOverlay.classList.toggle('hidden', !show);
}

// --- Logic Hệ thống Key ---
function generateRandomKey() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    const r = () => Array.from({length: 4}, () => chars[Math.floor(Math.random() * chars.length)]).join('');
    return `VIP-${r()}-${r()}`;
}

// --- Xử lý Đăng nhập/Đăng xuất ---
DOM.btnLogin.addEventListener('click', async () => {
    try {
        showLoading(true);
        await signInWithPopup(auth, provider);
    } catch (error) {
        showLoading(false);
        showToast("Login failed!", 'error');
    }
});

DOM.btnLogout.addEventListener('click', () => signOut(auth));

onAuthStateChanged(auth, (user) => {
    if (user && ADMIN_EMAILS.includes(user.email)) {
        DOM.userName.textContent = user.displayName;
        DOM.userEmail.textContent = user.email;
        DOM.userAvatar.src = user.photoURL;
        DOM.loginSection.classList.add('hidden');
        DOM.dashboardSection.classList.remove('hidden');
        loadKeys();
    } else {
        if (user) {
            signOut(auth);
            DOM.loginError.classList.remove('hidden');
        }
        DOM.loginSection.classList.remove('hidden');
        DOM.dashboardSection.classList.add('hidden');
    }
    showLoading(false);
});

// --- Thao tác với Database ---
async function loadKeys() {
    const q = query(collection(db, "keys"), orderBy("createdAt", "desc"));
    onSnapshot(q, (snapshot) => {
        keysData = [];
        let total = 0, active = 0, expired = 0;
        const now = Date.now();

        snapshot.forEach(docSnap => {
            const data = { ...docSnap.data(), id: docSnap.id };
            const isExpired = data.expiresAt !== 'never' && now > data.expiresAt;
            if (isExpired) data.isActive = false;
            
            keysData.push(data);
            total++;
            data.isActive ? active++ : expired++;
        });

        DOM.statTotal.textContent = total;
        DOM.statActive.textContent = active;
        DOM.statExpired.textContent = expired;
        renderTable(keysData);
    });
}

function renderTable(data) {
    DOM.keysTbody.innerHTML = data.map(item => `
        <tr>
            <td><span class="key-string">${item.keyString}</span></td>
            <td><span class="status-badge ${item.isActive ? 'status-active' : 'status-expired'}">${item.isActive ? 'Active' : 'Expired'}</span></td>
            <td>${item.createdBy}</td>
            <td>${new Date(item.createdAt).toLocaleDateString()}</td>
            <td>${item.expiresAt === 'never' ? 'Lifetime' : new Date(item.expiresAt).toLocaleDateString()}</td>
            <td>
                <button class="action-btn btn-copy" onclick="navigator.clipboard.writeText('${item.keyString}'); alert('Copied!');"><i class="fa-regular fa-copy"></i></button>
                <button class="action-btn btn-delete" data-id="${item.id}"><i class="fa-solid fa-trash-can"></i></button>
            </td>
        </tr>
    `).join('');

    // Gán sự kiện xóa
    DOM.keysTbody.querySelectorAll('.btn-delete').forEach(btn => {
        btn.onclick = () => confirm('Delete this key?') && deleteDoc(doc(db, "keys", btn.dataset.id));
    });
}

// --- Event Listeners Modal ---
DOM.btnHeaderCreate.onclick = () => { DOM.keyPreview.value = generateRandomKey(); DOM.modal.classList.remove('hidden'); };
DOM.btnCloseModal.onclick = () => DOM.modal.classList.add('hidden');
DOM.btnGenerateRandom.onclick = () => DOM.keyPreview.value = generateRandomKey();

DOM.btnSaveKey.onclick = async () => {
    const duration = parseInt(DOM.keyDuration.value);
    const expiresAt = duration === 9999 ? 'never' : Date.now() + (duration * 86400000);
    
    await addDoc(collection(db, "keys"), {
        keyString: DOM.keyPreview.value,
        createdBy: auth.currentUser.email,
        createdAt: Date.now(),
        expiresAt: expiresAt,
        isActive: true
    });
    DOM.modal.classList.add('hidden');
    showToast('Key created!', 'success');
};

initParticles();
