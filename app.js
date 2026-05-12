import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore, collection, addDoc, onSnapshot, deleteDoc, doc, query, orderBy } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

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

function initParticles() {
    const canvas = document.getElementById('particles-bg');
    if(!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    let particlesArray = [];
    for (let i = 0; i < 80; i++) {
        particlesArray.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * 2 + 0.5,
            speedX: Math.random() * 1 - 0.5,
            speedY: Math.random() * 1 - 0.5
        });
    }
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "rgba(0, 242, 254, 0.3)";
        particlesArray.forEach(p => {
            p.x += p.speedX; p.y += p.speedY;
            if (p.x < 0 || p.x > canvas.width) p.speedX *= -1;
            if (p.y < 0 || p.y > canvas.height) p.speedY *= -1;
            ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2); ctx.fill();
        });
        requestAnimationFrame(animate);
    }
    animate();
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${message}</span>`;
    DOM.toastContainer.appendChild(toast);
    setTimeout(() => { if(toast) toast.remove(); }, 3000);
}

function showLoading(show) {
    if(DOM.loadingOverlay) DOM.loadingOverlay.classList.toggle('hidden', !show);
}

DOM.btnLogin.addEventListener('click', async () => {
    try {
        showLoading(true);
        await signInWithPopup(auth, provider);
    } catch (e) {
        showLoading(false);
        showToast("Lỗi đăng nhập!", "error");
    }
});

DOM.btnLogout.addEventListener('click', () => signOut(auth));

onAuthStateChanged(auth, (user) => {
    if (user) {
        if (ADMIN_EMAILS.includes(user.email)) {
            DOM.userName.textContent = user.displayName;
            DOM.userEmail.textContent = user.email;
            DOM.userAvatar.src = user.photoURL;
            DOM.loginSection.classList.add('hidden');
            DOM.dashboardSection.classList.remove('hidden');
            loadKeys();
        } else {
            signOut(auth);
            DOM.loginError.classList.remove('hidden');
            showToast("Bạn không có quyền Admin!", "error");
        }
    } else {
        DOM.loginSection.classList.remove('hidden');
        DOM.dashboardSection.classList.add('hidden');
    }
    showLoading(false);
});

function loadKeys() {
    const q = query(collection(db, "keys"), orderBy("createdAt", "desc"));
    onSnapshot(q, (snapshot) => {
        keysData = [];
        let total = 0, active = 0, expired = 0;
        const now = Date.now();
        snapshot.forEach(docSnap => {
            const data = { ...docSnap.data(), id: docSnap.id };
            const isExp = data.expiresAt !== 'never' && now > data.expiresAt;
            if (isExp) data.isActive = false;
            keysData.push(data);
            total++; data.isActive ? active++ : expired++;
        });
        DOM.statTotal.textContent = total;
        DOM.statActive.textContent = active;
        DOM.statExpired.textContent = expired;
        renderTable(keysData);
    });
}

function renderTable(data) {
    DOM.keysTbody.innerHTML = '';
    data.forEach(item => {
        const tr = document.createElement('tr');
        const exp = item.expiresAt === 'never' ? 'Lifetime' : new Date(item.expiresAt).toLocaleDateString();
        tr.innerHTML = `
            <td><span class="key-string">${item.keyString}</span></td>
            <td><span class="status-badge ${item.isActive ? 'status-active' : 'status-expired'}">${item.isActive ? 'Active' : 'Expired'}</span></td>
            <td>${item.createdBy}</td>
            <td>${new Date(item.createdAt).toLocaleDateString()}</td>
            <td>${exp}</td>
            <td>
                <button class="action-btn btn-copy" data-key="${item.keyString}"><i class="fa-regular fa-copy"></i></button>
                <button class="action-btn btn-delete" data-id="${item.id}"><i class="fa-solid fa-trash-can"></i></button>
            </td>
        `;
        DOM.keysTbody.appendChild(tr);
    });
    DOM.keysTbody.querySelectorAll('.btn-copy').forEach(btn => {
        btn.onclick = () => {
            navigator.clipboard.writeText(btn.dataset.key);
            showToast("Đã copy!", "success");
        };
    });
    DOM.keysTbody.querySelectorAll('.btn-delete').forEach(btn => {
        btn.onclick = () => confirm('Xóa key này?') && deleteDoc(doc(db, "keys", btn.dataset.id));
    });
}

DOM.btnHeaderCreate.onclick = () => {
    const r = () => Math.random().toString(36).substring(2, 6).toUpperCase();
    DOM.keyPreview.value = `VIP-${r()}-${r()}`;
    DOM.modal.classList.remove('hidden');
};

DOM.btnCloseModal.onclick = () => DOM.modal.classList.add('hidden');

DOM.btnSaveKey.onclick = async () => {
    const d = parseInt(DOM.keyDuration.value);
    await addDoc(collection(db, "keys"), {
        keyString: DOM.keyPreview.value,
        createdBy: auth.currentUser.email,
        createdAt: Date.now(),
        expiresAt: d === 9999 ? 'never' : Date.now() + (d * 86400000),
        isActive: true
    });
    DOM.modal.classList.add('hidden');
    showToast('Đã tạo Key!', 'success');
};

initParticles();
      
