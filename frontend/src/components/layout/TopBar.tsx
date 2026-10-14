import { useEffect, useState } from "react";
import { api } from "../../services/api";

export default function TopBar() {
  const [state, setState] = useState<"checking" | "ready" | "no-model" | "offline">("checking");
  useEffect(() => {
    api.health().then((h) => setState(h.model_ready ? "ready" : "no-model")).catch(() => setState("offline"));
  }, []);
  const label = { checking: "Checking backend…", ready: "Backend online · model ready", "no-model": "Backend online · no model loaded", offline: "Backend offline" }[state];
  return <header className="topbar"><span>Full-stack computer vision · RDD2022</span><span role="status">{label}</span></header>;
}
