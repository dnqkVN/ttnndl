import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore, collection, addDoc, onSnapshot, deleteDoc, doc, query, orderBy } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// --- GIỮ NGUYÊN CONFIG CỦA CẬU ---
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

const DOM = {
    loginSection: document.getElementById('login-section'),
    dashboardSection: document.getElementById('dashboard-section'),
    btnLogin: document.getElementById('btn-google-login'),
    keysTbody: document.getElementById('keys-tbody'), // Vẫn là keys-tbody huyền thoại
    searchInput: document.getElementById('search-input'),
    modal: document.getElementById('create-modal'),
    btnCreate: document.getElementById('btn-create-header'),
    btnCloseModal: document.getElementById('btn-close-modal'),
    btnSaveKey: document.getElementById('btn-save-key'),
    keyPreview: document.getElementById('key-preview'),
    keyDuration: document.getElementById('key-duration')
};

// --- LOGIC AUTH (KHÔNG ĐỔI) ---
DOM.btnLogin.onclick = () => signInWithPopup(auth, provider);
onAuthStateChanged(auth, (user) => {
    if (user && user.email === "khangdoannq@gmail.com") {
        DOM.loginSection.classList.add('hidden');
        DOM.dashboardSection.classList.remove('hidden');
        loadKeys();
    } else {
        if(user) signOut(auth);
        DOM.loginSection.classList.remove('hidden');
        DOM.dashboardSection.classList.add('hidden');
    }
});

function loadKeys() {
    const q = query(collection(db, "keys"), orderBy("createdAt", "desc"));
    onSnapshot(q, (snapshot) => {
        const data = [];
        snapshot.forEach(doc => data.push({ id: doc.id, ...doc.data() }));
        renderTable(data);
    });
}

// --- HÀM RENDER (CHỈ THAY ĐỔI GIAO DIỆN CARD) ---
function renderTable(data) {
    DOM.keysTbody.innerHTML = '';
    data.forEach(item => {
        const div = document.createElement('div');
        div.className = 'neo-card';
        
        const expiresAt = item.expiresAt === 'never' ? 'Vĩnh viễn' : new Date(item.expiresAt).toLocaleString('vi-VN');
        const activeStatus = item.isActive ? 'on' : '';

        div.innerHTML = `
            <div class="card-header">
                <div class="device-box">
                    <i class="fa-solid fa-mobile-screen"></i>
                    <div class="device-info">
                        <h4>${item.keyString}</h4>
                        <p>ID: ${item.id.substring(0, 10)}...</p>
                    </div>
                </div>
                <div class="toggle-switch ${activeStatus}"></div>
            </div>
            
            <div class="info-box"><i class="fa-solid fa-key"></i> Key: ${item.keyString}</div>
            <div class="info-box"><i class="fa-regular fa-clock"></i> Hết hạn: ${expiresAt}</div>
            
            <div class="card-footer">
                <div class="badges">
                    <span class="badge normal">NORMAL</span>
                    <span class="badge auth">AUTHORIZED</span>
                </div>
                <div class="card-actions">
                    <button class="btn-copy" data-key="${item.keyString}"><i class="fa-solid fa-copy"></i></button>
                    <button class="btn-delete" data-id="${item.id}"><i class="fa-solid fa-trash-can"></i></button>
                </div>
            </div>
        `;
        DOM.keysTbody.appendChild(div);
    });

    // Sự kiện Copy & Xóa (Giữ nguyên)
    DOM.keysTbody.querySelectorAll('.btn-copy').forEach(btn => {
        btn.onclick = () => {
            navigator.clipboard.writeText(btn.dataset.key);
            alert("Đã copy key!");
        };
    });

    DOM.keysTbody.querySelectorAll('.btn-delete').forEach(btn => {
        btn.onclick = async () => {
            if(confirm("Xóa key này?")) await deleteDoc(doc(db, "keys", btn.dataset.id));
        };
    });
}

// --- LOGIC MODAL (GIỮ NGUYÊN) ---
DOM.btnCreate.onclick = () => {
    DOM.keyPreview.value = "VIP-" + Math.random().toString(36).substring(2, 7).toUpperCase();
    DOM.modal.classList.remove('hidden');
};
DOM.btnCloseModal.onclick = () => DOM.modal.classList.add('hidden');
DOM.btnSaveKey.onclick = async () => {
    const duration = parseInt(DOM.keyDuration.value);
    const expiresAt = duration === 9999 ? 'never' : Date.now() + (duration * 24 * 60 * 60 * 1000);
    await addDoc(collection(db, "keys"), {
        keyString: DOM.keyPreview.value,
        createdAt: Date.now(),
        expiresAt: expiresAt,
        isActive: true,
        createdBy: auth.currentUser.email
    });
    DOM.modal.classList.add('hidden');
};
