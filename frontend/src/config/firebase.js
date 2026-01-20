import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Check if in dev mode (no Firebase config)
const isDevMode =
  !import.meta.env.VITE_FIREBASE_API_KEY ||
  import.meta.env.VITE_FIREBASE_API_KEY === "";

// Mock Firebase auth for development
class MockAuth {
  constructor() {
    this.currentUser = null;
    this._listeners = [];
  }

  onAuthStateChanged(callback) {
    this._listeners.push(callback);
    // Simulate logged in user in dev mode
    setTimeout(() => {
      this.currentUser = {
        uid: "dev-user-123",
        email: "dev@example.com",
        displayName: "Dev User",
        getIdToken: async () => "mock-token-dev-123",
      };
      callback(this.currentUser);
    }, 100);

    return () => {
      this._listeners = this._listeners.filter((l) => l !== callback);
    };
  }

  async signInWithEmailAndPassword(email, password) {
    this.currentUser = {
      uid: "dev-user-123",
      email: email,
      displayName: "Dev User",
      getIdToken: async () => "mock-token-dev-123",
    };
    this._listeners.forEach((callback) => callback(this.currentUser));
    return { user: this.currentUser };
  }

  async createUserWithEmailAndPassword(email, password) {
    return this.signInWithEmailAndPassword(email, password);
  }

  async signOut() {
    this.currentUser = null;
    this._listeners.forEach((callback) => callback(null));
  }
}

let auth;

if (isDevMode) {
  console.log("🔧 Running in DEV MODE - Using mock Firebase Auth");
  auth = new MockAuth();
} else {
  const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
  };

  const app = initializeApp(firebaseConfig);
  auth = getAuth(app);
}

export { auth };
