const { initializeApp, cert } = require("firebase-admin/app");
const { getFirestore } = require("firebase-admin/firestore");

const serviceAccount = require("./firebase-service-account.json");

initializeApp({
  credential: cert(serviceAccount),
});

const db = getFirestore();

console.log("Firebase connected!");

async function getUsers() {
  const snapshot = await db.collection("users").get();

  snapshot.forEach((doc) => {
    console.log(doc.id, doc.data());
  });
}

getUsers();