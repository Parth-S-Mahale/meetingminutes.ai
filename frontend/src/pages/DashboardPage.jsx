import Hero from "../components/layout/Hero";
import MeetingHistory from "../components/meetings/MeetingHistory";
import MeetingResults from "../components/meetings/MeetingResults";
import UploadForm from "../components/meetings/UploadForm";
import { useMeetings } from "../context/MeetingContext";

export default function DashboardPage() {
  const { selectedMeeting, error } = useMeetings();
  return (
    <main>
      <Hero />
      <section className="workspace">
        <UploadForm />
        <MeetingHistory />
      </section>
      {error && (
        <div className="alert" role="alert">
          {error}
        </div>
      )}
      {selectedMeeting && <MeetingResults meeting={selectedMeeting} />}
    </main>
  );
}
