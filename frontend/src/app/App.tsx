import { Route, Routes } from "react-router-dom";
import AppShell from "../components/layout/AppShell";
import HomePage from "../pages/HomePage";
import DetectionPage from "../pages/DetectionPage";
import AnalyticsPage from "../pages/AnalyticsPage";
import ModelInsightsPage from "../pages/ModelInsightsPage";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/detect" element={<DetectionPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/model" element={<ModelInsightsPage />} />
      </Routes>
    </AppShell>
  );
}
