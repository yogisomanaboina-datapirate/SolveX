import { apiClient } from './client';

export const AuthService = {
  async signup(email, password, name) {
    const res = await apiClient.post('/api/v1/auth/signup', { email, password, name });
    if (res.data?.token) {
      localStorage.setItem('auth_token', res.data.token);
    }
    return res;
  },

  async login(email, password) {
    const res = await apiClient.post('/api/v1/auth/login', { email, password });
    if (res.data?.token) {
      localStorage.setItem('auth_token', res.data.token);
    }
    return res;
  },

  async getMe() {
    return apiClient.get('/api/v1/auth/me');
  }
};

export const HealthService = {
  async getHealth() {
    return apiClient.get('/health');
  }
};

export const EmergencyService = {
  async submitEmergencyTriage(symptoms, location, patientAge, medicalHistory = []) {
    return apiClient.post('/api/v1/triage/emergency', {
      symptoms,
      location: {
        lat: location?.lat || 17.4486,
        lng: location?.lng || 78.3908
      },
      patientAge: patientAge ? parseInt(patientAge, 10) : 45,
      medicalHistory
    });
  },

  async getAmbulanceStatus(ambulanceId) {
    return apiClient.get(`/api/v1/ambulance/${ambulanceId}`);
  }
};

export const InsuranceService = {
  async submitClaim(patientId, insuranceProvider, policyNumber, claimedAmount) {
    return apiClient.post('/api/v1/claims', {
      patientId: patientId || 'user_123',
      insuranceProvider: insuranceProvider || 'Apollo Health',
      policyNumber: policyNumber || 'POL-99281',
      claimedAmount: parseFloat(claimedAmount) || 5000.0
    });
  }
};

export const BedService = {
  async getHospitalBeds(hospitalId = 'HOSP-01') {
    return apiClient.get(`/api/v1/beds/${hospitalId}`);
  },

  async optimizeBeds(hospitalId, requestedBedType, patientUrgency, requiredSpecialty) {
    return apiClient.post('/api/v1/beds/optimize', {
      hospitalId: hospitalId || 'HOSP-01',
      requestedBedType: requestedBedType || 'ICU',
      patientUrgency: patientUrgency || 'HIGH',
      requiredSpecialty: requiredSpecialty || 'CARDIOLOGY'
    });
  }
};

export const MedicationService = {
  async getMedications(patientId = 'user_123') {
    return apiClient.get(`/api/v1/medications/${patientId}`);
  },

  async generateSchedule(medications, wakeTime = '08:00', sleepTime = '22:00') {
    return apiClient.post('/api/v1/medications/schedule', {
      medications,
      wakeTime,
      sleepTime
    });
  }
};

export const ReportService = {
  async analyzeReport(reportText, reportTitle = 'Medical Lab Report', reportDate = null, previousReports = []) {
    return apiClient.post('/api/v1/reports/analyze', {
      reportText,
      reportTitle,
      reportDate,
      previousReports
    });
  }
};

export const ChatService = {
  async sendMessage(message, patientProfile = null, conversationHistory = []) {
    return apiClient.post('/api/v1/chat', {
      message,
      patientProfile,
      conversationHistory
    });
  }
};

export const NotificationService = {
  async registerToken(fcmToken) {
    return apiClient.post('/api/v1/notifications/register', { fcmToken });
  },

  async sendTestNotification(title = 'LifeLink AI Medication Reminder', body = 'Time to take your scheduled medication.') {
    return apiClient.post('/api/v1/notifications/test-send', { title, body });
  },

  async scheduleDemoReminder(medicationName = 'Amoxicillin (Demo)', dosage = '500mg', delaySeconds = 60) {
    return apiClient.post('/api/v1/notifications/test-reminder', { medicationName, dosage, delaySeconds });
  }
};
