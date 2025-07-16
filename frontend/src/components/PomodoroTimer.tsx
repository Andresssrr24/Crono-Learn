import { useState, useEffect } from 'react';
import { createPomodoro, updatePomodoro } from '../services/api/pomodoro';
import { useNavigate } from 'react-router-dom';

interface PomodoroTimerProps {
  timer?: number;   // in seconds
  rest_time?: number;  // in seconds
  taskName: string;
}

export function PomodoroTimer({
  timer = 1500,  
  rest_time = 300,
  taskName, 
}: PomodoroTimerProps) {
  const navigate = useNavigate();
  const [isRunning, setIsRunning] = useState(false);
  const [isWorkMode, setIsWorkMode] = useState(true);
  const [secondsLeft, setSecondsLeft] = useState(timer);
  const [pomodoroId, setPomodoroId] = useState<string | null>(null);
  const [error, setError] = useState("");
  // Pomodoro customization interface
  const [showCustomization, setShowCustomization] = useState(false);
  const [customTimer, setCustomTimer] = useState(timer);
  const [customRestTime, setCustomRestTime] = useState(rest_time);


  // change duration when changing mode
  useEffect(() => {
    setSecondsLeft(isWorkMode ? timer : rest_time);
  }, [isWorkMode]);

  // timer
  useEffect(() => {
    if (!isRunning || secondsLeft <= 0) return;

    const intervalId = setInterval(() => {
      setSecondsLeft((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(intervalId);
  }, [isRunning, secondsLeft]);

  // rest or work mode when finished
  useEffect(() => {
    if (secondsLeft === 0 && isRunning) {
      setTimeout(() => {
        setIsWorkMode((prev) => !prev);
      }, 1000); // 1 segundo de pausa antes de cambiar
    }
  }, [secondsLeft, isRunning]);

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = time % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleStartPause = async () => {
    setError("");

    if (!isRunning && !pomodoroId) {
        console.log("Creating pomodoro with", {
          task_name: taskName,
          timer: customTimer,
          rest_time: customRestTime,
        });
        try {
            const pomodoro = await createPomodoro({
                task_name: taskName,
                timer: Math.max(1, Math.round(customTimer * 60)),
                rest_time: Math.max(1, Math.round(customRestTime * 60)),
                status: "running",
            });
            setPomodoroId(pomodoro.id);
            setSecondsLeft(customTimer * 60);
            setIsRunning(true);
        } catch (err: any) {
          if (err.message == "User is not authenticated.") {
            navigate("/sign-in");
          } else {
            setError(err.message || "Error starting Pomodoro.");
          }
        }
    } else {
        // alternate pause/running
        setIsRunning((prev) => !prev);
    }
  };

  const handleReset = () => {
    setIsRunning(false);
    setIsWorkMode(true);
    setSecondsLeft(timer);
    setPomodoroId(null);
  };

  return (
    <div className="flex flex-col items-center gap-4 text-center bg-stone-900 text-white p-6 rounded-2xl w-80 shadow-md">
      <h2 className="text-2xl font-bold">Pomodoro Timer</h2>
      <p className="text-lg text-emerald-400">{isWorkMode ? '🧠 Work Time' : '☕️ Break Time'}</p>
      <p className="text-4xl font-mono">{formatTime(secondsLeft)}</p>
      <p className="text-sm text-emerald-400">Status: {secondsLeft === 0 ? 'Completed' : isRunning ? 'Running' : 'Paused'}</p>

      {error && <p className="text-red-400">{error}</p>}

      {showCustomization && (
        <div className='w-full mt-4 bg-stone-800 p-4 rounded-lg'>
          <label className='block text-sm mb-2'>⏱ Worktime (min):</label>
          <input type="number" 
            min={1} 
            value={customTimer} 
            onChange={(e) => setCustomTimer(Number(e.target.value))}
            className='w-full px-2 py-1 mb-3 rounded bg-stone-700 text-white'
           />

           <label className='block text-sm mb-2'>⏱ Restime (min):</label>
           <input type="number" 
            min={1} 
            value={customRestTime} 
            onChange={(e) => setCustomRestTime(Number(e.target.value))}
            className='w-full px-2 py-1 mb-3 rounded bg-stone-700 text-white'
           />

           <button onClick={async () => {
            const newWorkSeconds = customTimer * 60;
            const newRestSeconds = customRestTime * 60;

            setSecondsLeft(isWorkMode ? newWorkSeconds : newRestSeconds);
            setShowCustomization(false);

            if (pomodoroId) {
              try {
                await updatePomodoro(Number(pomodoroId), {
                  timer: Math.floor(customTimer),
                  rest_time: Math.floor(customRestTime),
                });
              } catch (err: any) {
                setError(err.message || "Error updating pomodoro");
              }
            }
           }}
           className='mt-4 bg-emerald-600 hover:bg-emerald-500 px-4 py-2 rounded-lg w-full'
           >
            Save Changes
           </button>
        </div>
      )}

      <div className="flex gap-4 mt-4">
        <button
          onClick={handleStartPause}
          className="bg-emerald-700 hover:bg-emerald-600 px-4 py-2 rounded-lg"
        >
             {isRunning ? 'Pause' : 'Start'}
        </button>
        <button
          onClick={handleReset}
          className="bg-red-600 hover:bg-red-500 px-4 py-2 rounded-lg"
        >
          Reset
        </button>
      </div>

      <button onClick={() => setShowCustomization((prev) => !prev)}
        className='mt-2 text-sm underline text-emerald-400 hover:text-emerald-300'
      >
        {showCustomization ? 'Cancel' : 'Customize Pomodoro'}
      </button>

      {secondsLeft === 0 && <p className="text-yellow-400 mt-2">⏰ Time's up!</p>}
    </div>
  );
}
