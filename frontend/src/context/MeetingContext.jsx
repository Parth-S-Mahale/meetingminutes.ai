import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import {
  getMeeting,
  getMeetings,
  regenerateMeetingAnalysis,
  uploadMeeting,
} from "../api/meetings";

const MeetingContext = createContext(null);
const errorMessage = (error) =>
  error.response?.data?.detail ||
  error.message ||
  "Something went wrong while processing the meeting.";

export function MeetingProvider({ children }) {
  const [meetings, setMeetings] = useState([]);
  const [selectedMeeting, setSelectedMeeting] = useState(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState("");

  const loadHistory = useCallback(async () => {
    setIsLoadingHistory(true);
    try {
      setMeetings(await getMeetings());
    } catch (requestError) {
      setError(`Could not load meeting history: ${errorMessage(requestError)}`);
    } finally {
      setIsLoadingHistory(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const processMeeting = async (file, title) => {
    setError("");
    setSelectedMeeting(null);
    setIsProcessing(true);
    setUploadProgress(0);
    try {
      const meeting = await uploadMeeting(file, title, (event) => {
        if (event.total)
          setUploadProgress(Math.round((event.loaded * 100) / event.total));
      });
      setSelectedMeeting(meeting);
      await loadHistory();
      return meeting;
    } catch (requestError) {
      setError(errorMessage(requestError));
      throw requestError;
    } finally {
      setIsProcessing(false);
    }
  };

  const selectMeeting = async (id) => {
    setError("");
    try {
      setSelectedMeeting(await getMeeting(id));
    } catch (requestError) {
      setError(`Could not open this meeting: ${errorMessage(requestError)}`);
    }
  };

  const regenerateAnalysis = async (id) => {
    setError("");
    setIsProcessing(true);
    try {
      const meeting = await regenerateMeetingAnalysis(id);
      setSelectedMeeting(meeting);
      await loadHistory();
    } catch (requestError) {
      setError(errorMessage(requestError));
      throw requestError;
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <MeetingContext.Provider
      value={{
        meetings,
        selectedMeeting,
        isLoadingHistory,
        isProcessing,
        uploadProgress,
        error,
        processMeeting,
        selectMeeting,
        regenerateAnalysis,
      }}
    >
      {children}
    </MeetingContext.Provider>
  );
}

export function useMeetings() {
  const context = useContext(MeetingContext);
  if (!context)
    throw new Error("useMeetings must be used inside MeetingProvider.");
  return context;
}
