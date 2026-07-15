import { useState, useEffect } from "react";

function SimpleToast({ message, type = "info", onClose }: { message: string; type?: "info" | "success" | "error"; onClose: () => void }) {
  const toastStyle = {
    position: "fixed",
    bottom: "20px",
    left: "50%",
    right: "50%",
    transform: "translateX(-50%)",
    padding: "12px 20px",
    backgroundColor: type === "success" ? "#a5d6a7" : type === "error" ? "#e57373" : "#42a5f5",
    color: "white",
    borderRadius: "6px",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
    zIndex: 9999,
    minWidth: "300px",
    textAlign: "center",
  };

  if (type === "error") toastStyle.backgroundColor = "#ff5252";

  if (!onClose) {
    // Auto-dismiss after 4 seconds
    setTimeout(onClose, 4000);
  }

  return (
    <div style={toastStyle} onClick={onClose}>
      {message}
    </div>
  );
}

type RegisterToastProps = {
  message: string;
  type?: "info" | "success" | "error";
  autoDismiss?: boolean;
};

export function RegisterToast({ message, type = "info", autoDismiss = true }: RegisterToastProps) {
  const [opened, setOpened] = useState(false);
  const handler = () => {
    if (autoDismiss) setTimeout(() => setOpened(false), 4000);
    else setOpened(false);
  };

  return (
    <SimpleToast
      message={opened ? message : ""}
      type={opened ? type : "info"}
      onClose={() => {
        setOpened(false);
        handler();
      }}
      autoDismiss={autoDismiss}
    />
  );
}

// Usage in components:
// <RegisterToast message="Document processed successfully!" type="success" />,