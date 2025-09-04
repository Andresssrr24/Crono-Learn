import { createContext, useContext, useState, useEffect } from "react";
import { createPomodoro, pausePomodoro, stopPomodoro, resumePomodoro, getPomodoro } from "../services/api/pomodoro";

type PomodoroContextType = {
  pomodoroId: string | null;
  isRunning: boolean;
  isWorkMode: boolean;
  isCompleted: boolean;
  secondsLeft: number;
  customTimer: number;
  customRestTime: number;
  customTaskName: string;
  setCustomTimer: (n: number) => void;
  setCustomRestTime: (n: number) => void;
  setCustomTaskName: (s: string) => void;
  startPomodoro: (taskName: string, timer: number, restTime: number) => Promise<void>;
  pausePomodoroAction: () => Promise<void>;
  resumePomodoroAction: () => Promise<void>;
  resetPomodoro: () => Promise<void>;
};

const PomodoroContext = createContext<PomodoroContextType | undefined>(undefined);

export const PomodoroProvider = ({ children }: { children: React.ReactNode }) => {
    const [pomodoroId, setPomodoroId] = useState<string | null>(null);
    const [isRunning, setIsRunning] = useState(false);
    const [isWorkMode, setIsWorkMode] = useState(true);
    const [isCompleted, setIsCompleted] = useState(false);
    const [secondsLeft, setSecondsLeft] = useState(0);
    const [customTimer, setCustomTimer] = useState(25 * 60);
    const [customRestTime, setCustomRestTime] = useState(5 * 60);
    const [customTaskName, setCustomTaskName] = useState("");

    // Countdown
    useEffect(() => {
        if (!isRunning || secondsLeft <= 0) return;
        const id = setInterval(() => {
            setSecondsLeft((s) => s - 1);
        }, 1000);
        return () => clearInterval(id);
    }, [isRunning, secondsLeft]);

    const startPomodoro = async (taskName: string, timer: number, restTime: number) => {
        const pomodoro = await createPomodoro({
            task_name: taskName,
            timer: timer * 60,
            rest_time: restTime * 60,
            status: "running",
        });
        setPomodoroId(pomodoro.id);
        setSecondsLeft(timer * 60);
        setIsRunning(true);
        setIsWorkMode(true);
        setIsCompleted(false);
        setCustomTimer(timer);
        setCustomRestTime(restTime);
        setCustomTaskName(taskName);
    };

    const pausePomodoroAction = async () => {
        if (!pomodoroId) return;
        await pausePomodoro(pomodoroId);
        const updated = await getPomodoro(pomodoroId);
        setSecondsLeft(updated.time_left);
        setIsRunning(false);
    };

    const resumePomodoroAction = async () => {
        if (!pomodoroId) return;
        await resumePomodoro(pomodoroId);
        const updated = await getPomodoro(pomodoroId);
        setSecondsLeft(updated.time_left);
        setIsRunning(true);
    };
    
    const resetPomodoro = async () => {
        if (!pomodoroId) return;
        await stopPomodoro(pomodoroId);
        setPomodoroId(null);
        setIsRunning(false);
        setIsWorkMode(true);
        setIsCompleted(false);
        setSecondsLeft(0);
    };

    return (
        <PomodoroContext.Provider
            value={{
                pomodoroId,
                isRunning,
                isWorkMode,
                isCompleted,
                secondsLeft,
                customTimer,
                customRestTime,
                customTaskName,
                setCustomTimer,
                setCustomRestTime,
                setCustomTaskName,
                startPomodoro,
                pausePomodoroAction,
                resumePomodoroAction,
                resetPomodoro,
            }}
        >
            {children}
        </PomodoroContext.Provider>
    );
};

export const usePomodoro = () => {
    const context = useContext(PomodoroContext);
    if (!context) throw new Error("usePomodoro must be used within a PomodoroProvider");
    return context;
}