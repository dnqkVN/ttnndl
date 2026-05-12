import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore, collection, addDoc, onSnapshot, deleteDoc, doc, query, orderBy } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

const firebaseConfig = {
    apiKey: "AIzaSyCVJ49ItRu-dUCtytI0P5v7mDLE_QcubO8",
    authDomain: "kdtfdevt.firebaseapp.com",
    databaseURL: "https://kdtfdevt-default-rtdb.firebaseio.com",
    projectId: "kdtfdevt",
    storageBucket: "kdtfdevt.firebasestorage.app",
    messagingSenderId: "375523757842",
    appId: "1:375523757842:web:e3edae2409412e399cedcb",
    measurementId: "G-8R696PV3PB"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const provider = new GoogleAuthProvider();

const ADMIN_EMAILS = [
    "admin@gmail.com",
    "ceo@nexus.com" 
];

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

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    let icon = 'fa-circle-info';
    if(type === 'success') icon = 'fa-circle-check';
    if(type === 'error') icon = 'fa-circle-xmark';
    
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    DOM.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        if(toast.parentElement) toast.remove();
    }, 3400);
}

function showLoading(show) {
    if (show) DOM.loadingOverlay.classList.remove('hidden');
    else DOM.loadingOverlay.classList.add('hidden');
}

function generateRandomKey() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let p1 = '', p2 = '';
    for(let i=0; i<4; i++) p1 += chars.charAt(Math.floor(Math.random() * chars.length));
    for(let i=0; i<4; i++) p2 += chars.charAt(Math.floor(Math.random() * chars.length));
    return `VIP-${p1}-${p2}`;
}

DOM.btnLogin.addEventListener('click', async () => {
    try {
        showLoading(true);
        DOM.loginError.classList.add('hidden');
        await signInWithPopup(auth, provider);
    } catch (error) {
        showLoading(false);
        showToast(error.message, 'error');
    }
});

DOM.btnLogout.addEventListener('click', () => {
    signOut(auth);
});

onAuthStateChanged(auth, (user) => {
    if (user) {
        if (ADMIN_EMAILS.includes(user.email)) {
            DOM.userName.textContent = user.displayName;
            DOM.userEmail.textContent = user.email;
            DOM.userAvatar.src = user.photoURL;
            
            DOM.loginSection.classList.remove('active');
            DOM.loginSection.classList.add('hidden');
            DOM.dashboardSection.classList.remove('hidden');
            DOM.dashboardSection.classList.add('active');
            
            loadKeys();
            showLoading(false);
            showToast('Welcome back, Admin!', 'success');
        } else {
            signOut(auth);
            showLoading(false);
            DOM.loginError.classList.remove('hidden');
        }
    } else {
        DOM.loginSection.classList.add('active');
        DOM.loginSection.classList.remove('hidden');
        DOM.dashboardSection.classList.add('hidden');
        DOM.dashboardSection.classList.remove('active');
        showLoading(false);
    }
});

function openModal() {
    DOM.keyPreview.value = generateRandomKey();
    DOM.modal.classList.remove('hidden');
}

function closeModal() {
    DOM.modal.classList.add('hidden');
}

DOM.btnNavCreate.addEventListener('click', openModal);
DOM.btnHeaderCreate.addEventListener('click', openModal);
DOM.btnCloseModal.addEventListener('click', closeModal);
DOM.btnGenerateRandom.addEventListener('click', () => {
    DOM.keyPreview.value = generateRandomKey();
});

DOM.btnSaveKey.addEventListener('click', async () => {
    const keyValue = DOM.keyPreview.value;
    const durationDays = parseInt(DOM.keyDuration.value);
    const user = auth.currentUser;

    if (!user) return;

    try {
        showLoading(true);
        const now = new Date();
        let expiresAt = null;
        
        if (durationDays !== 9999) {
            expiresAt = new Date(now.getTime() + durationDays * 24 * 60 * 60 * 1000);
        }

        await addDoc(collection(db, "keys"), {
            keyString: keyValue,
            createdBy: user.email,
            createdAt: now.getTime(),
            expiresAt: expiresAt ? expiresAt.getTime() : 'never',
            isActive: true
        });

        closeModal();
        showLoading(false);
        showToast('Key generated successfully!', 'success');
    } catch (error) {
        showLoading(false);
        showToast('Error saving key.', 'error');
    }
});

function loadKeys() {
    const q = query(collection(db, "keys"), orderBy("createdAt", "desc"));
    onSnapshot(q, (snapshot) => {
        keysData = [];
        let total = 0;
        let active = 0;
        let expired = 0;
        const now = new Date().getTime();

        snapshot.forEach((docSnap) => {
            const data = docSnap.data();
            data.id = docSnap.id;
            
            if (data.expiresAt !== 'never' && now > data.expiresAt) {
                data.isActive = false;
            }
            
            keysData.push(data);
            total++;
            if (data.isActive) active++;
            else expired++;
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
        
        const createdDate = new Date(item.createdAt).toLocaleDateString() + ' ' + new Date(item.createdAt).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        const expiresDate = item.expiresAt === 'never' ? 'Lifetime' : new Date(item.expiresAt).toLocaleDateString() + ' ' + new Date(item.expiresAt).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        const statusClass = item.isActive ? 'status-active' : 'status-expired';
        const statusText = item.isActive ? 'Active' : 'Expired';

        tr.innerHTML = `
            <td><span class="key-string">${item.keyString}</span></td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td>${item.createdBy}</td>
            <td>${createdDate}</td>
            <td>${expiresDate}</td>
            <td>
                <button class="action-btn btn-copy" data-key="${item.keyString}" title="Copy"><i class="fa-regular fa-copy"></i></button>
                <button class="action-btn btn-delete" data-id="${item.id}" title="Delete"><i class="fa-solid fa-trash-can"></i></button>
            </td>
        `;
        DOM.keysTbody.appendChild(tr);
    });

    document.querySelectorAll('.btn-copy').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const keyStr = e.currentTarget.getAttribute('data-key');
            navigator.clipboard.writeText(keyStr);
            showToast('Key copied to clipboard!', 'success');
        });
    });

    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            if(confirm('Are you sure you want to delete this key?')) {
                const id = e.currentTarget.getAttribute('data-id');
                await deleteDoc(doc(db, "keys", id));
                showToast('Key deleted.', 'info');
            }
        });
    });
}

DOM.searchInput.addEventListener('input', (e) => {
    const val = e.target.value.toLowerCase();
    const filtered = keysData.filter(k => 
        k.keyString.toLowerCase().includes(val) || 
        k.createdBy.toLowerCase().includes(val)
    );
    renderTable(filtered);
});

initParticles();
