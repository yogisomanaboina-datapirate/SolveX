import { mockEmergency } from "../data/mockData";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "";

const USE_MOCK =
  import.meta.env.VITE_USE_MOCK !== "false";

export async function submitEmergency(emergencyRequest) {
  if (USE_MOCK) {
    await new Promise((resolve) => {
      setTimeout(resolve, 1000);
    });

    return {
      success: true,
      data: {
        ...mockEmergency,
        request: emergencyRequest,
      },
    };
  }

  const token = localStorage.getItem("token");

  const response = await fetch(
    `${API_BASE_URL}/api/v1/triage/emergency`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token
          ? { Authorization: `Bearer ${token}` }
          : {}),
      },
      body: JSON.stringify({
        symptoms: emergencyRequest.symptoms,
        emergencyType: emergencyRequest.emergencyType,
        location: emergencyRequest.location,
        patientAge: 45,
        medicalHistory: [],
      }),
    },
  );

  const result = await response.json();

  if (!response.ok || result.success === false) {
    throw new Error(
      result?.error?.message ||
        "Emergency request failed.",
    );
  }

  return {
    success: true,
    data: normalizeEmergencyResponse(result.data),
  };
}

function normalizeEmergencyResponse(data) {
  return {
    severity: data.severity ?? null,
    condition: data.condition ?? "Emergency detected",
    action: data.action ?? data.recommendedAction ?? null,

    confidence:
      data.confidence ?? data.confidenceScore ?? null,

    reasoning:
      data.reasoning ??
      data.aiReasoning ??
      null,

    ambulanceId:
      data.ambulanceId ?? null,

    eta:
      data.eta ??
      data.ETA ??
      null,

    hospitalId:
      data.hospitalId ?? null,

    hospitalName:
      data.hospitalName ?? null,

    hospitalLocation:
      data.hospitalLocation ?? null,

    firstAid:
      Array.isArray(data.firstAid)
        ? data.firstAid
        : data.firstAid
          ? [data.firstAid]
          : [],
  };
}