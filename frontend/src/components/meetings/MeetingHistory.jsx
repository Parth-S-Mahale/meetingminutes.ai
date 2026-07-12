import StatusBadge from "../../common/StatusBadge";
import { useMeetings } from "../../context/MeetingContext";

const formatDate = (date) => new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(date));
export default function MeetingHistory() {
  const { meetings, isLoadingHistory, selectMeeting } = useMeetings();
  const openMeeting = async (id) => { await selectMeeting(id); window.scrollTo({ top: 0, behavior: "smooth" }); };
  return <aside className="history-card"><div className="section-heading"><span className="step">02</span><div><h2>Recent meetings</h2><p>Your saved meeting records.</p></div></div><div className="meeting-list">{isLoadingHistory ? <p className="muted">Loading meetings…</p> : meetings.length === 0 ? <p className="muted">Your processed meetings will appear here.</p> : meetings.map((item) => <button className="meeting-row" type="button" onClick={() => openMeeting(item.id)} key={item.id}><span className="meeting-title">{item.title || item.original_filename}</span><span>{formatDate(item.created_at)}</span><StatusBadge status={item.status} /></button>)}</div></aside>;
}
