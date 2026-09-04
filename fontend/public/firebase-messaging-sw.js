// LifeLink AI Firebase Cloud Messaging Service Worker
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyDemoApiKeyForLifeLinkHackathon12345",
  authDomain: "lifelink-ai-hackathon.firebaseapp.com",
  projectId: "lifelink-ai-hackathon",
  storageBucket: "lifelink-ai-hackathon.appspot.com",
  messagingSenderId: "109876543210",
  appId: "1:109876543210:web:abcdef1234567890"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Background FCM message received:', payload);
  const notificationTitle = payload.notification?.title || payload.data?.title || 'LifeLink AI Medication Reminder';
  const notificationOptions = {
    body: payload.notification?.body || payload.data?.body || 'Time to take your scheduled medication.',
    icon: '/favicon.ico',
    badge: '/favicon.ico',
    data: payload.data || { route: '/medications' }
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const route = event.notification.data?.route || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(route);
      }
    })
  );
});
