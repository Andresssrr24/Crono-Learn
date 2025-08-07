import { useState, useEffect } from 'react';
import { createPomodoro, updatePomodoro } from '../services/api/pomodoro';
import { useNavigate } from 'react-router-dom';
import { CompletedPomodoroNotif } from './partials/CompletedPomodoroNotif';

interface PomodoroTimerProps {
  timer?: number;   // in seconds
  rest_time?: number;  // in seconds
  task_name: string;
}

export function PomodoroTimer({
  timer = 1500,  
  rest_time = 300,
  task_name, 
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
  const [customTaskName, setCustomTaskName] = useState(task_name);

  // change duration when changing mode
  useEffect(() => {
    const newTime = isWorkMode ? customTimer * 60 : customRestTime * 60;
    setSecondsLeft(newTime);
  }, [isWorkMode, customTimer, customRestTime]);

  // timer
  useEffect(() => {
    if (!isRunning || secondsLeft <= 0) return;

    const intervalId = setInterval(() => {
      setSecondsLeft((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(intervalId);
  }, [isRunning, secondsLeft]);

  {/*// rest or work mode when finished
  useEffect(() => {
    if (secondsLeft === 0 && isRunning) {
      setTimeout(() => {
        setIsWorkMode((prev) => !prev);
      }, 6000); // 6 pause seconds before changing state
    }
  }, [secondsLeft, isRunning]); 
  // Interesting to implement later as an option between manual and automatic pomodoro restart 
  */} 

  // Manually start timer and rest pauses
  useEffect(() => {
  if (secondsLeft === 0 && isRunning) {
    setIsRunning(false);

    if (isWorkMode) {
      const totalSeconds = customTimer * 60;
      const workedSeconds = totalSeconds - secondsLeft;
      let workedMinutes = Math.floor(workedSeconds / 60);

      if (workedMinutes < 1) {
        workedMinutes = 1;
      }

      CompletedPomodoroNotif(workedMinutes, customTaskName || task_name);
    }
  }
}, [secondsLeft, isRunning, isWorkMode, customTimer, customTaskName, task_name]);

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = time % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleStartPause = async () => {
    setError("");

    if (!isRunning && !pomodoroId) {
        console.log("Creating pomodoro with", {
          task_name: task_name,
          timer: customTimer,
          rest_time: customRestTime,
        });
        try {
            const pomodoro = await createPomodoro({
                task_name: customTaskName || task_name,
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
            max={240}
            value={customTimer} 
            onChange={(e) => setCustomTimer(Number(e.target.value))}
            className='w-full px-2 py-1 mb-3 rounded bg-stone-700 text-white'
           />

           <label className='block text-sm mb-2'>⏱ Restime (min):</label>
           <input type="number" 
            min={1}
            max={240} 
            value={customRestTime} 
            onChange={(e) => setCustomRestTime(Number(e.target.value))}
            className='w-full px-2 py-1 mb-3 rounded bg-stone-700 text-white'
           />

          <label className="block mb-2">
            Task name (Optional)
            <input
              type="text"
              value={customTaskName}
              onChange={(e) => setCustomTaskName(e.target.value)}
              className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:ring focus:ring-blue-200"
              placeholder="Ej: Study for tomorrow's exam"
            />
          </label>

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
                  task_name: customTaskName || undefined,
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

      {!isRunning && secondsLeft === 0 && (
      <button
          onClick={() => {
            if (!isWorkMode) {
              // Start pomodoro -> show customization 
              setShowCustomization(true);
            } else {
              // Start rest pause
              setIsWorkMode(false);
              setSecondsLeft(rest_time * 60);
              setIsRunning(true);
            }
          }}
          className="bg-blue-600 text-white px-4 py-2 mt-4 rounded hover:bg-blue-700 transition"
        >
          Start {isWorkMode ? "break" : "pomodoro (customize)"}
        </button>
      )}
    </div>
  );
}
