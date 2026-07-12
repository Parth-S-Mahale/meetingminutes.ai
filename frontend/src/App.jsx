import { MeetingProvider } from "./context/MeetingContext";
import DashboardPage from "./pages/DashboardPage";

export default function App() {
  return (
    <MeetingProvider>
      <DashboardPage />
    </MeetingProvider>
  );
}
