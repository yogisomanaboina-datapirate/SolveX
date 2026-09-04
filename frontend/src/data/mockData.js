export const mockEmergency = {
  severity: 5,

  condition:
    "Possible Cardiac Emergency",

  action:
    "Immediate emergency response required",

  confidence: 94,

  reasoning:
    "Reported chest pain and difficulty breathing indicate a potentially life-threatening cardiac emergency.",

  ambulanceId:
    "AMB-001",

  eta: 8,

  hospitalId:
    "HOSP-001",

  hospitalName:
    "City General Hospital",

  hospitalLocation: {
    lat: 17.385,
    lng: 78.4867,
  },

  firstAid: [
    "Stay calm and remain seated.",
    "Avoid unnecessary movement.",
    "Do not eat or drink.",
    "Wait for emergency medical assistance.",
  ],
};

export const mockAmbulance = {
  id: "AMB-001",

  status: "en_route",

  eta: 8,

  hospitalName:
    "City General Hospital",

  hospitalLocation: {
    lat: 17.385,
    lng: 78.4867,
  },

  location: {
    lat: 17.392,
    lng: 78.48,
  },
};