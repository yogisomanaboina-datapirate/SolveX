function LocationCapture({
  location,
  onCapture,
  disabled = false,
}) {
  const captureLocation = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by this browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        onCapture({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
      },
      () => {
        alert(
          "Unable to access your location. Please allow location access.",
        );
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      },
    );
  };

  return (
    <div className="location-box">
      <div className="location-content">
        <span className="label">Your Location</span>

        {location ? (
          <>
            <strong>
              {location.lat.toFixed(5)},{" "}
              {location.lng.toFixed(5)}
            </strong>

            <span className="location-status">
              ✓ Location captured
            </span>
          </>
        ) : (
          <p>Location is required for emergency dispatch.</p>
        )}
      </div>

      <button
        type="button"
        onClick={captureLocation}
        disabled={disabled}
      >
        {location ? "Update Location" : "Use My Location"}
      </button>
    </div>
  );
}

export default LocationCapture;