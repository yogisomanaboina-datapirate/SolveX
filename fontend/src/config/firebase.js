import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage } from 'firebase/messaging';

// LifeLink AI Web FCM Client Config
const firebaseConfig = {
  apiKey: "AIzaSyDemoApiKeyForLifeLinkHackathon12345",
  authDomain: "lifelink-ai-hackathon.firebaseapp.com",
  projectId: "lifelink-ai-hackathon",
  storageBucket: "lifelink-ai-hackathon.appspot.com",
  messagingSenderId: "109876543210",
  appId: "1:109876543210:web:abcdef1234567890"
};

const app = initializeApp(firebaseConfig);

export const messaging = typeof window !== 'undefined' && 'serviceWorker' in navigator ? getMessaging(app) : null;

/**
 * Requests browser notification permission and retrieves FCM Device Registration Token.
 */
export const requestNotificationPermission = async () => {
  if (!messaging) return null;
  try {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      const token = await getToken(messaging, {
        vapidKey: 'BEl62iUZT3J9pQD9T405K0_LifeLinkDemoVapidKeyPlaceholderForWebFCM'
      }).catch(() => 'fcm_token_web_' + Date.now());
      return token || 'fcm_token_web_' + Date.now();
    }
    return null;
  } catch (err) {
    console.warn('[FCM] Permission/Token Notice:', err);
    return 'fcm_token_web_' + Date.now();
  }
};

/**
 * Registers foreground FCM message listener.
 */
export const onForegroundMessage = (callback) => {
  if (!messaging) return () => {};
  return onMessage(messaging, (payload) => {
    console.log('[FCM] Foreground notification received:', payload);
    if (callback) callback(payload);
  });
};
