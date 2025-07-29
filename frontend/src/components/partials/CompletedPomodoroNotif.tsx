import toast from "react-hot-toast";
import { createStudyRecord } from "../../services/api/study_records";

export function CompletedPomodoroNotif(study_time: number, topic: string) {
    toast.custom((t) => (
        <div className="bg-gray-950 shadow-lg rounded-xl p-4 flex flex-col gap-3 border border-gray-900">
            <span className="text-gray-200 font-medium">
                Pomodoro completed! Add {study_time} min in task {topic} to your study records?
            </span>
            <div className="flex gap-3 justify-end">
                <button className="bg-teal-950 text-white px-4 py-1 rounded-lg hover:bg-emerald-700 transition"
                        onClick={async () => {
                            try {
                                const payload = {
                                    topic: topic && topic.trim() !== "" ? topic.trim() : null,
                                    study_time: Number(study_time),
                                    notes: "Added automatically, you can edit your note.",
                                };
                                
                                console.log("Payload enviado desde CompletedPomodoroNotif:", payload);
                                await createStudyRecord(payload);
                                toast.success("Pomodoro added to study records!");
                            } catch (error) {
                                toast.error("Failed to save pomodoro record.");
                                console.error(error);
                            } finally {
                                toast.dismiss(t.id);
                            }
                        }}
                >
                    Yes
                </button>
                <button className="text-gray-500 hover:underline"
                        onClick={() => toast.dismiss(t.id)}
                >
                    No
                </button>    
            </div>
        </div>
    ));
}