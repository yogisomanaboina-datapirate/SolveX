import { mockAmbulance } from "../data/mockData";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "";

const USE_MOCK =
  import.meta.env.VITE_USE_MOCK !== "false";

export async function getAmbulance(ambulanceId) {
  if (USE_MOCK) {
    return {
      success: true,
      data: {
        ...mockAmbulance,
        id: ambulanceId,
      },
    };
  }

  const token = localStorage.getItem("token");

  const response = await fetch(
    `${API_BASE_URL}/api/v1/ambulance/${ambulanceId}`,
    {
      headers: {
        ...(token
          ? { Authorization: `Bearer ${token}` }
          : {}),
      },
    },
  );

  const result = await response.json();

  if (!response.ok || result.success === false) {
    throw new Error(
      result?.error?.message ||
        "Unable to load ambulance.",
    );
  }

  return {
    success: true,
    data: normalizeAmbulance(result.data),
  };
}

export function subscribeToAmbulance(
  ambulanceId,
  onUpdate,
) {
  if (USE_MOCK) {
    return createMockSubscription(
      ambulanceId,
      onUpdate,
    );
  }

  let stopped = false;

  const poll = async () => {
    if (stopped) {
      return;
    }

    try {
      const response =
        await getAmbulance(ambulanceId);

      if (!stopped) {
        onUpdate(response.data);
      }
    } catch (error) {
      console.error(
        "Ambulance update failed:",
        error,
      );
    }
  };

  const interval = setInterval(poll, 5000);

  return () => {
    stopped = true;
    clearInterval(interval);
  };
}

function createMockSubscription(
  ambulanceId,
  onUpdate,
) {
  let eta = 8;

  const interval = setInterval(() => {
    eta = Math.max(0, eta - 1);

    const progress =
      (8 - eta) / 8;

    onUpdate({
      ...mockAmbulance,
      id: ambulanceId,
      eta,
      status:
        eta === 0
          ? "arrived"
          : "en_route",
      location: {
        lat:
          mockAmbulance.location.lat +
          progress * 0.003,
        lng:
          mockAmbulance.location.lng +
          progress * 0.004,
      },
    });
  }, 5000);

  return () => clearInterval(interval);
}

function normalizeAmbulance(data) {
  return {
    id: data.id,
    status: data.status ?? "en_route",
    eta: data.eta ?? data.ETA ?? null,
    hospitalName:
      data.hospitalName ?? "Assigned Hospital",
    hospitalLocation:
      data.hospitalLocation ?? null,
    location: data.location ?? null,
  };
}