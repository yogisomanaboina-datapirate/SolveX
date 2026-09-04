const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "";

const USE_MOCK =
  import.meta.env.VITE_USE_MOCK !== "false";

export async function loginUser(credentials) {
  if (USE_MOCK) {
    return {
      success: true,
      token: "demo-token",
      user: {
        id: "demo-user",
        name: "Emergency User",
      },
    };
  }

  const response = await fetch(
    `${API_BASE_URL}/api/v1/auth/login`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    },
  );

  const result = await response.json();

  if (!response.ok || result.success === false) {
    throw new Error(
      result?.error?.message || "Login failed.",
    );
  }

  return {
    success: true,
    token:
      result?.data?.token ??
      result?.token,
    user:
      result?.data?.user ??
      result?.user ??
      null,
  };
}